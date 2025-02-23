from fastapi import FastAPI, HTTPException
from datetime import date
from pydantic import BaseModel
from moex_connector import MoexConnector
from moex_request import MoexRequestAttributes
from logger import Logger

moex_app = FastAPI()
logger = Logger("moex")

class FetchDataRequest(BaseModel):
    ticker: str
    from_date: date
    till_date: date


@moex_app.post("/fetch_data_from_moex")
async def fetch_data(request: FetchDataRequest):
    try:
        attributes = MoexRequestAttributes(
            request.ticker, request.from_date, request.till_date
        )
        connector = MoexConnector()
        data = connector.fetch_data(attributes)
        
        logger.info(f"Collected data: {data}")
        return {"data": data}
    except Exception as e:
        logger.error(f"Error happened while fetching data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
