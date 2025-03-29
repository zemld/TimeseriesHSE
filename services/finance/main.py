from fastapi import FastAPI
from domain_objects.action import Action
from concrete.db_managers.action_db_manager import ActionDBManager
from concrete.fetchers.action_fetcher import ActionFetcher
from logger import Logger

finance_service = FastAPI()
finance_logger = Logger("finance_service")
finance_db_manager = ActionDBManager(
    db_name="finance_db",
    db_port=5432,
    db_user="finance_db",
    db_password="secret",
)
finance_fetcher = ActionFetcher()

@finance_service.get("/fetch_data")
async def fetch_data():
    pass

@finance_service.post("/update_data")
async def update_data_in_db():
    pass

