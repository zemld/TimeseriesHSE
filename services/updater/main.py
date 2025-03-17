import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi_utils.tasks import repeat_every
from datetime import datetime
from dateutil.relativedelta import relativedelta
import httpx
import tickers
from logger import Logger

data_updater = FastAPI()
logger = Logger("updater")


async def update_finance_data(ticker: str):
    from_date = datetime.today().date() - relativedelta(years=3)
    till_date = datetime.today().date()

    logger.debug(f"Fetching data for {ticker}")
    try:
        async with httpx.AsyncClient() as client:
            moex_response = await client.get(
                "http://moex_service:8001/fetch_data",
                params={
                    "table_name": ticker,
                    "from_date": str(from_date),
                    "till_date": str(till_date),
                },
            )
            logger.debug(
                f"Moex response: {moex_response.status_code}, {moex_response.text}"
            )
            moex_response.raise_for_status()
            data = moex_response.json()["data"]

            logger.info(f"Collected data: {data}")

            await client.post(
                "http://finance_db:8002/create_table", params={"table_name": ticker}
            )
            logger.debug(f"Table {ticker} created.")
            await client.post(
                "http://finance_db:8002/delete_data",
                json={"table_name": ticker, "till_date": str(till_date)},
            )
            logger.debug(f"Data deleted.")
            await client.post(
                "http://finance_db:8002/insert_data",
                json={"table_name": ticker, "data": data},
            )
            logger.debug(f"Data inserted.")
    except Exception as e:
        logger.error(e)


async def update_electricity_data():
    today = datetime.today().date()
    logger.debug(f"Fetching data for {today}")

    try:
        async with httpx.AsyncClient() as client:
            electricity_response = await client.get(
                "http://electricity_service:8007/fetch_electricity_data",
                params={
                    "year": str(today.year),
                    "month": str(today.month),
                    "day": str(today.day),
                },
            )
            logger.debug(
                f"Electricity response: {electricity_response.status_code}, {electricity_response.text}"
            )
            electricity_response.raise_for_status()
            data = electricity_response.json()
            logger.info(f"Collected data: {data}")

            await client.post(
                "http://electricity_db_service:8006/create_table",
                params={"table_name": "electricity"},
            )
            logger.debug("Table electricity created.")
            await client.post(
                "http://electricity_db_service:8006/delete_data",
                json={"table_name": "electricity", "till_date": str(today)},
            )
            logger.debug("Data deleted.")
            await client.post(
                "http://electricity_db_service:8006/insert_data",
                json={"table_name": "electricity", "data": {today: data["price"]}},
            )
            logger.debug("Data inserted.")
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch data: {e}")


@data_updater.on_event("startup")
@repeat_every(days=1, wait_first=False)
async def scheduled_update():
    logger.info("Update scheduled")
    tickers_list = tickers.get_all_action_tickers()
    await asyncio.gather(*(update_finance_data(ticker) for ticker in tickers_list))


@data_updater.post("/trigger_update")
async def trigger_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(scheduled_update)
    logger.info("Update triggered")
