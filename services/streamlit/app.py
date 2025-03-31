import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import httpx
from logger import Logger
from datetime import datetime

logger = Logger("streamlit")

st.set_page_config(
    page_title="Визуализация финансовых данных",
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
            st.error("Не удалось получить данные из кэша")
            return None
    except Exception as e:
        st.error(f"Ошибка получения данных: {str(e)}")
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
        title=f"{ticker} Исторические цены",
        xaxis_title="Дата",
        yaxis_title="Цена",
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
            name="Исторические данные",
        )
    )

    dates = [item["timestamp"] for item in prediction_data]
    prices = [item["price"] for item in prediction_data]

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=prices,
            mode="lines",
            name=f"Предсказания модели ({model_name})",
            line=dict(dash="dash"),
        )
    )

    fig.update_layout(
        title=f"Предсказания цен акций для {ticker} - модель {model_name}",
        xaxis_title="Дата",
        yaxis_title="Цена",
        template="plotly_white",
        height=500,
    )
    return fig


def show_historical_analysis_result(model, analysis, df):
    st.subheader(f"Анализ с использованием модели {model.upper()}")
    if model in analysis and "error" not in analysis[model]:
        col1, col2 = st.columns(2)
        model_analysis = analysis[model].get("analysis", {})
        logger.debug(f"Model analysis: {model_analysis}")

        with col1:
            st.metric("MSE", f"{model_analysis.get('mse', 'N/A'):.6f}")
            st.metric("Trend", model_analysis.get("trend", "N/A").upper())

        with col2:
            st.metric(
                "Последнее значение",
                f"{model_analysis.get('last_value', 'N/A'):.2f}",
            )
            st.metric(
                "Точечные данные",
                model_analysis.get("data_points", len(df)),
            )
    else:
        st.error(f"Не удалось провести анализ с помощью модели {model}")


def show_prediction_result(model, prediction, df, ticker):
    st.subheader(f"Прогнозирование данных с помощью модели {model.upper()}")
    if model in prediction and "error" not in prediction[model]:
        model_prediction = prediction[model].get("forecast", [])
        logger.debug(f"Предсказания модели {model_prediction}")
        if model_prediction:
            fig_pred = plot_prediction(df, model_prediction, ticker, model.upper())
            st.plotly_chart(fig_pred, use_container_width=True)
        else:
            st.info("Нет доступных данных для предсказания")
    else:
        st.error(f"Не удалось предсказать данные с помощью модели {model}")


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

    st.header(f"Анализ данных для акций {ticker}")

    df = pd.DataFrame(historical_data)
    df["date_value"] = pd.to_datetime(df["date_value"])
    logger.debug(f"DataFrame: {df}")
    st.subheader("Исторические данные")
    fig = plot_timeseries(df, ticker)
    st.plotly_chart(fig, use_container_width=True)

    if len(models_used) > 0:
        tabs = st.tabs(models_used)

        for i, model in enumerate(models_used):
            show_finance_analysis_result_for_model(
                tabs, i, model, analysis, prediction, df, ticker
            )


def main():
    st.title("📊 Анализ финансовых временных рядов")
    results = get_cached_results()
    if not results:
        st.info("Нет доступных данных. Необходимо сначала провести анализ.")
        return

    show_finance_analysis_result(results)


if __name__ == "__main__":
    main()
