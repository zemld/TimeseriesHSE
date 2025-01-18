from flask import Flask, render_template, request, url_for, jsonify
from moex.moex_connector import MoexConnector
from moex.moex_request import MoexRequestAttributes
from db_connection.database_manager import DatabaseManager
import tickers
from datetime import datetime, date
from trade import Trade

app = Flask(__name__)


@app.route("/")
def start():
    return render_template("index.html")


@app.route("/chart-parameters", methods=["POST"])
def handle_parameters():
    parameters = request.json
    category = parameters.get("category")
    value = parameters.get("value")
    start_date = parameters.get("start_date")
    end_date = parameters.get("end_date")

    redirect_url = url_for(
        "show_chart",
        category=category,
        value=value,
        start_date=start_date,
        end_date=end_date,
    )
    return jsonify({"redirect": redirect_url})


def get_request_attributes(
    category, value, from_date, till_date
) -> MoexRequestAttributes:
    if category == "акция":
        attributes = MoexRequestAttributes(
            "stock", tickers.action_value_to_enum(value).value, from_date, till_date
        )
    elif category == "облигация":
        attributes = MoexRequestAttributes(
            "bonds", tickers.bond_value_to_enum(value).value, from_date, till_date
        )
    else:
        attributes = MoexRequestAttributes(
            "currency",
            tickers.currency_value_to_enum(value).value,
            from_date,
            till_date,
        )

    return attributes


def moex_data_to_trade_type(data: dict) -> list:
    trades = []
    for trade_date, price in data.items():
        trades.append(Trade(trade_date, price))
    return trades


def trade_to_dict(trades: list) -> dict:
    return {trade.get_trade_date(): trade.get_price() for trade in trades}

@app.route("/chart")
async def show_chart():
    parameters = request.args
    category = parameters.get("category")
    value = parameters.get("value")
    from_date = datetime.strptime(parameters.get("start_date"), "%Y-%m-%d").date()
    till_date = datetime.strptime(parameters.get("end_date"), "%Y-%m-%d").date()

    # TODO: Вынести запрос к мосбирже отдельно от построения графика.
    moex = MoexConnector()
    request_attributes: MoexRequestAttributes = get_request_attributes(
        category, value, from_date, till_date
    )

    data = moex.fetch_data(request_attributes)
    if data:
        db = DatabaseManager("db", 5432, "db", "user", "secret")
        await db.connect()
        table_name = request_attributes.get_ticker()
        await db.create_table(table_name)
        await db.insert_data(table_name, data)
        selected_data = await db.select_data(table_name, date(2022, 6, 2), date(2022, 6, 9))
        print(selected_data)

    return f"""<h1>График с {request.args.get('start_date')} по {request.args.get('end_date')} построен! 
    Параметр {request.args.get('category'), request.args.get('value')}.</h1>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
