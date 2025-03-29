from fastapi import FastAPI
from concrete.db_managers.action_db_manager import ActionDBManager
from concrete.fetchers.action_fetcher import ActionFetcher
from logger import Logger
from datetime import datetime
from dateutil.relativedelta import relativedelta

finance_service = FastAPI()
logger = Logger("finance_service")
db_manager = ActionDBManager(
    db_host="finance_db",
    db_port=5432,
    db_name="finance_db",
    db_user="user",
    db_password="secret",
)
fetcher = ActionFetcher()


@finance_service.get("/fetch_data")
async def fetch_data(ticker: str, from_date: str, till_date: str):
    fetcher.set_params(
        ticker=ticker,
        from_date=from_date,
        till_date=till_date,
    )
    data = await fetcher.fetch_data()
    logger.info(f"Fetched data for {ticker}: {data}")
    return {"ticker": ticker, "data": data}


@finance_service.post("/update_data")
async def update_data_in_db(ticker: str):
    till_date = datetime.today().date()
    from_date = till_date - relativedelta(years=1)
    try:
        response = await fetch_data(ticker, str(from_date), str(till_date))
        data = response["data"]
        await db_manager.update(ticker, str(from_date), data)
        logger.info(f"Updated data for {ticker} in DB.")
        return {"ticker": ticker, "status": "updated"}
    except Exception as e:
        logger.error(f"Error updating data for {ticker}: {str(e)}")
        return {"error": str(e)}


@finance_service.get("/get_data")
async def get_data(ticker: str, from_date: str, till_date: str):
    data = await db_manager.select(ticker, from_date, till_date)
    logger.info(f"Retrieved data for {ticker}: {data}")
    return {"ticker": ticker, "data": data}
