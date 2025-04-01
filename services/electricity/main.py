from fastapi import FastAPI
from concrete.db_managers.electricity_db_manager import ElectricityDBManager
from concrete.fetchers.electricity_fetcher import ElectricityFetcher
from logger import Logger
from datetime import datetime
from dateutil.relativedelta import relativedelta

electricity_service = FastAPI()
logger = Logger("electricity_service")
db_manager = ElectricityDBManager(
    host="electricity_db",
    port=5432,
    name="electricity_db",
    user="user",
    password="secret",
)
fetcher = ElectricityFetcher()


def get_date_parts_from_date(date: str) -> dict:
    date_as_date = datetime.strptime(date, "%Y-%m-%d").date()
    year = date_as_date.year
    month = str(date_as_date.month).zfill(2)
    day = str(date_as_date.day).zfill(2)
    return {"year": year, "month": month, "day": day}


@electricity_service.get("/fetch_data")
async def fetch_data(date: str):
    params = get_date_parts_from_date(date)
    year = params["year"]
    month = params["month"]
    day = params["day"]

    logger.debug(f"Fetching electricity data for {year}-{month}-{day}")
    fetcher.set_params(params)
    data = await fetcher.fetch_data()
    logger.info(
        f"Fetched electricity data for {year}-{month}-{day}: {len(data)} records"
    )
    return {"date": f"{year}-{month}-{day}", "data": data}


@electricity_service.post("/update_data")
async def update_data_in_db(from_date: str, till_date: str):
    current_date = datetime.strptime(from_date, "%Y-%m-%d").date()
    till_date_as_date = datetime.strptime(till_date, "%Y-%m-%d").date()
    while current_date <= till_date_as_date:
        try:
            logger.info(f"Updating electricity data for {current_date}")
            response = await fetch_data(str(current_date))
            data = response["data"]
            await db_manager.update("electricity", from_date, data)
            logger.info(f"Updated electricity data for {current_date} in DB.")
        except Exception as e:
            logger.error(f"Error updating electricity data: {str(e)}")
        finally:
            current_date += relativedelta(days=1)


@electricity_service.get("/get_data")
async def get_data(from_date: str, till_date: str):
    try:
        logger.debug(f"Getting electricity data from {from_date} to {till_date}")
        data = await db_manager.select("electricity", from_date, till_date)
        logger.info(f"Retrieved electricity data: {len(data)} records")
        return {"from_date": from_date, "till_date": till_date, "data": data}
    except Exception as e:
        logger.error(f"Error retrieving electricity data: {str(e)}")
        return {"error": str(e)}
