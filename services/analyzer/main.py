from fastapi import FastAPI, Request
import httpx
from logger import Logger
from concrete.analyzing_models.cnn import CNNModel
from concrete.analyzing_models.rnn import RNNModel
from concrete.analyzing_models.tft import TFTModel
import pandas as pd
import numpy as np
import os

analyzer = FastAPI()
logger = Logger("analyzer")

models = {
    "cnn": CNNModel(window_size=30, features=1),
    "rnn": RNNModel(window_size=30, features=1),
    "tft": TFTModel(window_size=30, features=1),
}

MODELS_DIR = "saved_models"
os.makedirs(MODELS_DIR, exist_ok=True)

for model_name, model in models.items():
    model_path = f"{MODELS_DIR}/{model_name}"
    model_file = f"{model_path}/{model_name}_model.keras"

    os.makedirs(model_path, exist_ok=True)
    if os.path.exists(model_file):
        logger.info(f"Loading saved model: {model_name}")
        try:
            model.load(model_path)
            logger.info(f"Model {model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
    else:
        logger.info(
            f"Model file for {model_name} not found at {model_file}. Will be trained when needed."
        )


async def get_parameters(request: Request, has_horizon=False):
    data_json = await request.json()
    data = data_json.get("data", []).get("data", [])
    model_type = data_json.get("model_type", "cnn")
    ticker = data_json.get("ticker", "unknown")
    if has_horizon:
        horizon = data_json.get("horizon", 5)
        logger.debug(f"Received parameters: {data}, {model_type}, {ticker}, {horizon}")
        return (data, model_type, ticker, horizon)
    logger.debug(f"Received parameters: {data}, {model_type}, {ticker}")
    return (data, model_type, ticker)


def check_model(model_type):
    if model_type not in models:
        logger.error(f"Unsupported model type: {model_type}")
        raise Exception({"error": f"Model type {model_type} not supported"})


def convert_to_dataframe(data, target_column: str):
    df = pd.DataFrame(data)
    target = df[[target_column]].values
    logger.debug(f"Prepared {len(target)} price points for analysis")
    logger.debug(f"Target has type: {type(target)}")
    return (df, target)


def train_and_save_models(model_type: str, target):
    logger.debug(f"target has type: {type(target)}")
    model_path = f"{MODELS_DIR}/{model_type}"
    model_file = f"{model_path}/{model_type}_model.keras"
    if not os.path.exists(model_file):
        logger.info(f"Model {model_type} not trained yet, training now")
        logger.debug(f"Scaler has type: {type(models[model_type].scaler)}")
        models[model_type].scaler.fit(target)
        models[model_type].train(target)
        models[model_type].save(model_path)
        logger.info(f"Model {model_type} trained and saved")
    else:
        try:
            models[model_type].scaler.transform(target[:1])
        except Exception as e:
            logger.warning(f"Scaler for {model_type} not fitted, fitting now")
            logger.debug(f"Scaler has type: {type(models[model_type].scaler)}")
            models[model_type].scaler.fit(target)


def make_analysis(data: pd.DataFrame, model_type: str, target: np.ndarray, ticker: str):
    logger.debug(f"Starting analysis with {model_type} model")
    analysis = models[model_type].analyze(target)
    logger.debug(f"Analysis completed for {ticker} using {model_type}: {analysis}")

    analysis["data_points"] = len(target)
    analysis["start_date"] = (
        data["timestamp"].iloc[0] if "timestamp" in data.columns else None
    )
    analysis["end_date"] = (
        data["timestamp"].iloc[-1] if "timestamp" in data.columns else None
    )
    return analysis


@analyzer.post("/analize_finance_data")
async def analize_finance_data(request: Request):
    try:
        data, model_type, ticker = await get_parameters(request)
        logger.info(f"Analyzing data for {ticker} with model {model_type}")

        if not data:
            raise Exception("No data provided for analysis")
        logger.debug(
            f"Before converting to dataframe scaler has type: {type(models[model_type].scaler)}"
        )
        df, prices = convert_to_dataframe(data, "close")
        logger.debug(
            f"After converting to dataframe scaler has type: {type(models[model_type].scaler)}"
        )
        train_and_save_models(model_type, prices)
        logger.debug(
            f"After training and saving models scaler has type: {type(models[model_type].scaler)}"
        )
        analysis = make_analysis(df, model_type, prices, ticker)
        return {"ticker": ticker, "model": model_type, "analysis": analysis}
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return {"error": str(e)}


def make_prediction(
    data: pd.DataFrame, model_type: str, target: np.ndarray, horizon: int
):
    logger.debug(f"Starting prediction with {model_type} model")
    predictions = models[model_type].predict(target, horizon=horizon)
    logger.debug(f"Generated {len(predictions)} prediction points")

    try:
        last_date = (
            pd.to_datetime(data["timestamp"].iloc[-1])
            if "timestamp" in data.columns
            else pd.Timestamp.now()
        )
        dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=len(predictions),
            freq="D",
        )

        forecast = [
            {"timestamp": date.strftime("%Y-%m-%d"), "price": float(price[0])}
            for date, price in zip(dates, predictions)
        ]
        logger.debug(f"Formatted prediction results: {len(forecast)} points")
    except Exception as e:
        logger.error(f"Error formatting prediction results: {str(e)}")
        forecast = [
            {"step": i + 1, "price": float(price[0])}
            for i, price in enumerate(predictions)
        ]
    finally:
        return forecast


@analyzer.post("/predict_finance_data")
async def predict_finance_data(request: Request):
    try:
        data, model_type, ticker, horizon = await get_parameters(
            request, has_horizon=True
        )
        logger.info(
            f"Predicting for {ticker} with model {model_type}, horizon={horizon}"
        )

        if not data:
            raise Exception("No data provided for prediction")

        check_model(model_type)

        df, prices = convert_to_dataframe(data, "close")
        train_and_save_models(model_type, prices)

        forecast = make_prediction(df, model_type, prices, horizon)
        logger.info(f"Prediction completed for {ticker} using {model_type}")

        return {
            "ticker": ticker,
            "model": model_type,
            "horizon": horizon,
            "forecast": forecast,
            "last_observed_price": float(prices[-1][0]) if len(prices) > 0 else None,
        }
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return {"error": str(e)}
