from fastapi import FastAPI
from concrete.db_managers.electricity_db_manager import ElectricityDBManager
from concrete.fetchers.electricity_fetcher import ElectricityFetcher
from logger import Logger

electricity_service = FastAPI()
electricity_logger = Logger("electricity_service")
electricity_db_manager = ElectricityDBManager(
    db_name="electricity_db",
    db_port=5432,
    db_user="electricity_db",
    db_password="secret",
)
electricity_fetcher = ElectricityFetcher()


@electricity_service.get("/fetch_data")
async def fetch_data():
    pass


@electricity_service.post("/update_data")
async def update_data_in_db():
    pass
