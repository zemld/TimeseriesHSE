import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import httpx
from logger import Logger
from datetime import datetime

logger = Logger("streamlit")

st.set_page_config(
    page_title="FinanceTS Visualization",
    page_icon="📈",
    layout="wide",
)


@st.cache_data(ttl=300)
def get_cached_results():
    try:
        response = httpx.get("http://web:8000/get-cached-results")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch data from web service")
            return None
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None


def plot_timeseries(df, ticker):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date_value"],
            y=df["close"],
            mode="markers",
            name=f"{ticker} Close Price",
        )
    )

    fig.update_layout(
        title=f"{ticker} Historical Price",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        height=500,
    )
    return fig


def plot_prediction(historical_df, prediction_data, ticker, model_name):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=historical_df["date_value"],
            y=historical_df["close"],
            mode="markers",
            name="Historical Data",
        )
    )

    dates = [item["timestamp"] for item in prediction_data]
    prices = [item["price"] for item in prediction_data]

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=prices,
            mode="lines",
            name=f"Prediction ({model_name})",
            line=dict(dash="dash"),
        )
    )

    fig.update_layout(
        title=f"{ticker} Price Prediction - {model_name} Model",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        height=500,
    )
    return fig


def show_historical_analysis_result(model, analysis, df):
    st.subheader(f"Analysis with {model.upper()} model")
    if model in analysis and "error" not in analysis[model]:
        col1, col2 = st.columns(2)
        model_analysis = analysis[model].get("analysis", {})
        logger.debug(f"Model analysis: {model_analysis}")

        with col1:
            st.metric("MSE", f"{model_analysis.get('mse', 'N/A'):.6f}")
            st.metric("Trend", model_analysis.get("trend", "N/A").upper())

        with col2:
            st.metric(
                "Last Value",
                f"{model_analysis.get('last_value', 'N/A'):.2f}",
            )
            st.metric(
                "Data Points",
                model_analysis.get("data_points", len(df)),
            )
    else:
        st.error(f"Analysis failed for {model} model")


def show_prediction_result(model, prediction, df, ticker):
    st.subheader(f"Prediction with {model.upper()} model")
    if model in prediction and "error" not in prediction[model]:
        model_prediction = prediction[model].get("forecast", [])
        logger.debug(f"Model prediction: {model_prediction}")
        if model_prediction:
            fig_pred = plot_prediction(df, model_prediction, ticker, model.upper())
            st.plotly_chart(fig_pred, use_container_width=True)
        else:
            st.info("No prediction data available")
    else:
        st.error(f"Prediction failed for {model} model")


def show_finance_analysis_result_for_model(
    tabs, index, model, analysis, prediction, df, ticker
):
    with tabs[index]:
        show_historical_analysis_result(model, analysis, df)
        show_prediction_result(model, prediction, df, ticker)


def show_finance_analysis_result(results):
    ticker = results.get("ticker", "Unknown")
    historical_data = results["historical_data"].get("data", [])
    logger.debug(f"Historical data: {historical_data}")
    analysis = results.get("analysis", {})
    prediction = results.get("prediction", {})
    models_used = results.get("models_used", [])

    st.header(f"Analysis for {ticker}")

    df = pd.DataFrame(historical_data)
    df["date_value"] = pd.to_datetime(df["date_value"])
    logger.debug(f"DataFrame: {df}")
    st.subheader("Historical Data")
    fig = plot_timeseries(df, ticker)
    st.plotly_chart(fig, use_container_width=True)

    if len(models_used) > 0:
        tabs = st.tabs(models_used)

        for i, model in enumerate(models_used):
            show_finance_analysis_result_for_model(
                tabs, i, model, analysis, prediction, df, ticker
            )


def main():
    st.title("📊 Financial Time Series Analysis")
    results = get_cached_results()
    if not results:
        st.info("No data available. Please run an analysis first.")
        return

    show_finance_analysis_result(results)


if __name__ == "__main__":
    main()
