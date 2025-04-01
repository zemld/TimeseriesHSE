from fastapi import FastAPI
from concrete.db_managers.action_db_manager import ActionDBManager
from concrete.fetchers.action_fetcher import ActionFetcher
from logger import Logger
from datetime import datetime
from dateutil.relativedelta import relativedelta

finance_service = FastAPI()
logger = Logger("finance_service")
db_manager = ActionDBManager(
    host="finance_db",
    port=5432,
    name="finance_db",
    user="user",
    password="secret",
)
fetcher = ActionFetcher()


@finance_service.get("/fetch_data")
async def fetch_data(ticker: str, from_date: str, till_date: str):
    params = {
        "ticker": ticker,
        "from_date": from_date,
        "till_date": till_date,
    }
    fetcher.set_params(params)
    logger.debug(f"Fetching data with params: {params}")
    data = await fetcher.fetch_data()
    logger.info(f"Fetched data for {ticker}: {len(data)} records")
    return {"ticker": ticker, "data": data}


@finance_service.post("/update_data")
async def update_data_in_db(ticker: str, from_date: str, till_date: str):
    from_tmp_date = datetime.strptime(from_date, "%Y-%m-%d").date()
    till_date_as_date = datetime.strptime(till_date, "%Y-%m-%d").date()
    till_tmp_date = from_tmp_date + relativedelta(days=100)
    logger.debug(f"From date: {from_tmp_date}, Till date: {till_tmp_date}")
    while from_tmp_date < till_date_as_date:
        try:
            logger.info(
                f"Updating data for {ticker} from {from_tmp_date} to {min(till_tmp_date, till_date_as_date)}"
            )
            response = await fetch_data(
                ticker, str(from_tmp_date), str(min(till_tmp_date, till_date_as_date))
            )
            logger.debug(f"Response: {response}")
            data = response["data"]
            logger.debug("Data fetched successfully.")
            await db_manager.update(ticker, from_date, data)
            logger.info(f"Updated data for {ticker} in DB.")
        except Exception as e:
            logger.error(f"Error updating data for {ticker}: {str(e)}")
        finally:
            from_tmp_date = till_tmp_date
            till_tmp_date = from_tmp_date + relativedelta(days=100)


@finance_service.get("/get_data")
async def get_data(ticker: str, from_date: str, till_date: str):
    data = await db_manager.select(ticker, from_date, till_date)
    for row in data:
        row.date_value = row.timestamp.date()
    logger.info(f"Retrieved {len(data)} records for {ticker}: {data}")
    return {"ticker": ticker, "data": data}
