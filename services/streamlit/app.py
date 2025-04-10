import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import httpx
from logger import Logger
from datetime import datetime

logger = Logger("streamlit")

st.set_page_config(
    page_title="Визуализация финансовых данных",
    page_icon="📈",
    layout="wide",
)


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


def plot_timeseries(df, ticker=None, column_name="close"):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"] if "timestamp" in df.columns else df["date_value"],
            y=df[column_name],
            mode="markers",
            name=f"{ticker + ' ' if ticker else ''}Price",
        )
    )

    title = (
        f"{ticker} Исторические цены" if ticker else "Исторические цены электричества"
    )
    y_label = "Цена" if column_name == "close" else "Цена (EUR/kWh)"

    fig.update_layout(
        title=title,
        xaxis_title="Дата",
        yaxis_title=y_label,
        template="plotly_white",
        height=500,
    )
    return fig


def plot_prediction(
    historical_df,
    prediction_data,
    title_prefix,
    model_name,
    x_column="date_value",
    y_column="close",
):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=historical_df[x_column],
            y=historical_df[y_column],
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
        title=f"Предсказания цен для {title_prefix} - модель {model_name}",
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


def show_prediction_result(
    model, prediction, df, title_prefix, x_column="date_value", y_column="close"
):
    st.subheader(f"Прогнозирование данных с помощью модели {model.upper()}")
    if model in prediction and "error" not in prediction[model]:
        model_prediction = prediction[model].get("forecast", [])
        logger.debug(f"Предсказания модели {model_prediction}")
        if model_prediction:
            fig_pred = plot_prediction(
                df, model_prediction, title_prefix, model.upper(), x_column, y_column
            )
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


def show_electricity_result_for_model(tabs, index, model, analysis, prediction, df):
    with tabs[index]:
        show_historical_analysis_result(model, analysis, df)
        show_prediction_result(
            model, prediction, df, "электричества", "timestamp", "price"
        )


def show_electricity_result(results):
    historical_data = results["historical_data"].get("data", [])
    logger.debug(f"Electricity historical data: {historical_data}")
    analysis = results.get("analysis", {})
    prediction = results.get("prediction", {})
    models_used = results.get("models_used", [])
    start_date = results.get("start_date", "Unknown")
    end_date = results.get("end_date", "Unknown")

    st.header(f"Анализ данных потребления электричества")
    st.subheader(f"Период: {start_date} - {end_date}")

    df = pd.DataFrame(historical_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    logger.debug(f"Electricity DataFrame: {df}")

    st.subheader("Исторические данные")
    fig = plot_timeseries(df, column_name="price")
    st.plotly_chart(fig, use_container_width=True)

    if len(models_used) > 0:
        tabs = st.tabs(models_used)

        for i, model in enumerate(models_used):
            show_electricity_result_for_model(tabs, i, model, analysis, prediction, df)


def main():
    st.title("📊 Анализ временных рядов")

    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = None

    with st.spinner("Загрузка данных..."):
        if st.session_state.last_refresh is None:
            results = get_cached_results()
            st.session_state.results = results
            st.session_state.last_refresh = datetime.now()
        else:
            results = st.session_state.results

    if not results:
        st.info("Нет доступных данных. Необходимо сначала провести анализ.")
        return

    if "ticker" in results:
        show_finance_analysis_result(results)
    else:
        show_electricity_result(results)


if __name__ == "__main__":
    if not st.runtime.exists():
        for key in st.session_state.keys():
            del st.session_state[key]
    main()
