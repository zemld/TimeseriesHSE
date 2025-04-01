from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import httpx
from logger import Logger
from tickers import action_value_to_enum
import json
from datetime import date

webapp = FastAPI()
templates = Jinja2Templates(directory="templates")
logger = Logger("webapp")


def cache_results(data):
    with open("cached_results.json", "w") as f:
        json.dump(data, f)


async def fetch_finance_parameters(request: Request):
    parameters = await request.json()
    logger.debug(f"Got parameters: {parameters}")
    value = action_value_to_enum(parameters.get("value")).value
    start_date = parameters.get("start_date")
    end_date = parameters.get("end_date")
    return (value, start_date, end_date)


async def fetch_electricity_parameters(request: Request):
    parameters = await request.json()
    logger.debug(f"Got electricity parameters: {parameters}")
    from_date = parameters.get("fromDate")
    return from_date


@webapp.get("/")
async def start(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@webapp.get("/actions")
async def choose_action(request: Request):
    return templates.TemplateResponse("actions.html", {"request": request})


@webapp.get("/waiting-for-action-analysis")
async def waiting_page(request: Request):
    return templates.TemplateResponse("waiting-for-action-analysis.html", {"request": request})


@webapp.get("/waiting-for-electricity-analysis")
async def waiting_page_electricity(request: Request):
    return templates.TemplateResponse("waiting-for-electricity-analysis.html", {"request": request})


@webapp.post("/make-action-analysis")
async def run_action_flow(request: Request):
    try:
        (ticker, from_date, till_date) = await fetch_finance_parameters(request)
        logger.debug(f"Sending request with params: {ticker, from_date, till_date}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            finance_response = await client.get(
                "http://finance:8005/get_data",
                params={
                    "ticker": ticker,
                    "from_date": from_date,
                    "till_date": till_date,
                },
            )
            logger.debug(
                f"Response from finance service with code {finance_response.status_code}: {finance_response.text}"
            )
            if finance_response.status_code != 200:
                logger.error(f"Failed to fetch data: {finance_response.text}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Failed to retrieve data for the specified stock"
                    },
                )

            historical_data = finance_response.json()
            logger.info(f"Retrieved {len(historical_data.get("data", []))} records for {ticker}")

            models_response = await client.get("http://analyzer:8004/models")
            if models_response.status_code != 200:
                available_models = [
                    "cnn",
                    "rnn",
                    "tft",
                ]
                logger.warning(
                    f"Could not fetch available models, using defaults: {available_models}"
                )
            else:
                available_models = models_response.json().get(
                    "available_models", ["cnn", "rnn", "tft"]
                )

            logger.info(f"Will use models: {available_models}")

            analysis_results = {}
            for model_type in available_models:
                try:
                    analysis_response = await client.post(
                        "http://analyzer:8004/analize_finance_data",
                        json={
                            "data": historical_data,
                            "ticker": ticker,
                            "model_type": model_type,
                        },
                        timeout=60.0,
                    )

                    if analysis_response.status_code == 200:
                        analysis_results[model_type] = analysis_response.json()
                        logger.info(f"Successfully analyzed with {model_type}")
                    else:
                        logger.error(
                            f"Failed to analyze with {model_type}: {analysis_response.text}"
                        )
                        analysis_results[model_type] = {
                            "error": f"Analysis failed for {model_type}"
                        }
                except Exception as model_error:
                    logger.error(
                        f"Error during {model_type} analysis: {str(model_error)}"
                    )
                    analysis_results[model_type] = {"error": str(model_error)}

            prediction_results = {}
            for model_type in available_models:
                try:
                    predict_response = await client.post(
                        "http://analyzer:8004/predict_finance_data",
                        json={
                            "data": historical_data,
                            "ticker": ticker,
                            "model_type": model_type,
                            "horizon": 30,
                        },
                        timeout=60.0,
                    )

                    if predict_response.status_code == 200:
                        prediction_results[model_type] = predict_response.json()
                        logger.info(f"Successfully predicted with {model_type}")
                    else:
                        logger.error(
                            f"Failed to predict with {model_type}: {predict_response.text}"
                        )
                        prediction_results[model_type] = {
                            "error": f"Prediction failed for {model_type}"
                        }
                except Exception as model_error:
                    logger.error(
                        f"Error during {model_type} prediction: {str(model_error)}"
                    )
                    prediction_results[model_type] = {"error": str(model_error)}
            response_content = {
                "historical_data": historical_data,
                "analysis": analysis_results,
                "prediction": prediction_results,
                "ticker": ticker,
                "start_date": from_date,
                "end_date": till_date,
                "models_used": available_models,
            }
            cache_results(response_content)
            # При  запуске программы локально переадресация должна быть на http://localhost:8501
            redirect_address = "http://localhost:8501"
            # redirect_address = "http://ithse.ru:1171"
            return JSONResponse(content={"redirect": redirect_address})
    except Exception as e:
        logger.error(f"Error in run_action_flow: {str(e)}")
        return JSONResponse(
            status_code=500, content={"error": f"An error occurred: {str(e)}"}
        )


@webapp.get("/electricity")
async def choose_electricity(request: Request):
    return templates.TemplateResponse("electricity.html", {"request": request})


@webapp.post("/make-electricity-analysis")
async def run_electricity_flow(request: Request):
    try:
        from_date = await fetch_electricity_parameters(request)
        logger.debug(f"Sending electricity request with params: {from_date}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            electricity_response = await client.get(
                "http://electricity:8007/get_data",
                params={
                    "from_date": from_date,
                    "till_date": date.today().strftime("%Y-%m-%d"),
                },
            )
            logger.debug(
                f"Response from electricity service with code {electricity_response.status_code}: {electricity_response.text}"
            )
            if electricity_response.status_code != 200:
                logger.error(f"Failed to fetch electricity data: {electricity_response.text}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Failed to retrieve electricity data for the specified region"
                    },
                )

            historical_data = electricity_response.json()
            logger.info(f"Retrieved {len(historical_data.get('data', []))} records")

            models_response = await client.get("http://analyzer:8004/models")
            if models_response.status_code != 200:
                available_models = [
                    "cnn",
                    "rnn",
                    "tft",
                ]
                logger.warning(
                    f"Could not fetch available models, using defaults: {available_models}"
                )
            else:
                available_models = models_response.json().get(
                    "available_models", ["cnn", "rnn", "tft"]
                )

            logger.info(f"Will use models: {available_models}")

            analysis_results = {}
            for model_type in available_models:
                try:
                    analysis_response = await client.post(
                        "http://analyzer:8004/analize_electricity_data",
                        json={
                            "data": historical_data,
                            "model_type": model_type,
                        },
                        timeout=60.0,
                    )

                    if analysis_response.status_code == 200:
                        analysis_results[model_type] = analysis_response.json()
                        logger.info(f"Successfully analyzed electricity data with {model_type}")
                    else:
                        logger.error(
                            f"Failed to analyze electricity data with {model_type}: {analysis_response.text}"
                        )
                        analysis_results[model_type] = {
                            "error": f"Analysis failed for {model_type}"
                        }
                except Exception as model_error:
                    logger.error(
                        f"Error during electricity {model_type} analysis: {str(model_error)}"
                    )
                    analysis_results[model_type] = {"error": str(model_error)}

            prediction_results = {}
            for model_type in available_models:
                try:
                    predict_response = await client.post(
                        "http://analyzer:8004/predict_electricity_data",
                        json={
                            "data": historical_data,
                            "model_type": model_type,
                            "horizon": 30,
                        },
                        timeout=60.0,
                    )

                    if predict_response.status_code == 200:
                        prediction_results[model_type] = predict_response.json()
                        logger.info(f"Successfully predicted electricity data with {model_type}")
                    else:
                        logger.error(
                            f"Failed to predict electricity data with {model_type}: {predict_response.text}"
                        )
                        prediction_results[model_type] = {
                            "error": f"Prediction failed for {model_type}"
                        }
                except Exception as model_error:
                    logger.error(
                        f"Error during electricity {model_type} prediction: {str(model_error)}"
                    )
                    prediction_results[model_type] = {"error": str(model_error)}
            
            response_content = {
                "historical_data": historical_data,
                "analysis": analysis_results,
                "prediction": prediction_results,
                "start_date": from_date,
                "end_date": date.today().strftime("%Y-%m-%d"),
                "models_used": available_models,
            }
            cache_results(response_content)
            # redirect_address = "http://localhost:8501" Для запуска локально
            redirect_address = "http://ithse.ru:1171"
            return JSONResponse(content={"redirect": redirect_address})
    except Exception as e:
        logger.error(f"Error in run_electricity_flow: {str(e)}")
        return JSONResponse(
            status_code=500, content={"error": f"An error occurred: {str(e)}"}
        )


@webapp.get("/error")
async def handle_error(request: Request):
    error = request.get("error")
    return f"Error: {error}"


@webapp.get("/get-cached-results")
async def get_cached_results():
    try:
        with open("cached_results.json", "r") as f:
            result = json.load(f)
            logger.debug(f"Loaded cached results.")
            return JSONResponse(content=result)
    except (FileNotFoundError, json.JSONDecodeError):
        return JSONResponse(
            status_code=404, content={"error": "No cached results available"}
        )
