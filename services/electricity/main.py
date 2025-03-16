from fastapi import FastAPI
import httpx
from logger import Logger

electricity_service = FastAPI()
logger = Logger("electricity_service")

@electricity_service.get("/fetch_electricity_data")
async def fetch(year: str, month: str, day: str):
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{year}/{month}-{day}_SE3.json"
    try:
        response = await httpx.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Collected data: {data}")
        return data
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch data: {e}")
        return {"error": str(e)}