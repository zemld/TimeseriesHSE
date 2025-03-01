from datetime import datetime
from fastapi import FastAPI, HTTPException
from moex_connector import MoexConnector
from moex_request import MoexRequestAttributes
from logger import Logger

moex = FastAPI()
logger = Logger("moex")


@moex.get("/fetch_data")
async def fetch_data(ticker: str, from_date: str, till_date: str):
    try:
        attributes = MoexRequestAttributes(
            ticker,
            datetime.strptime(from_date, "%Y-%m-%d").date(),
            datetime.strptime(till_date, "%Y-%m-%d").date(),
        )
        connector = MoexConnector()
        data = connector.fetch_data(attributes)

        logger.info(f"Collected data: {data}")
        return {"data": data}
    except Exception as e:
        logger.error(f"Error happened while fetching data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
