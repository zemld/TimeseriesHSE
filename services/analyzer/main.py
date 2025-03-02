from fastapi import FastAPI, Request
from logger import Logger


analyzer = FastAPI()
logger = Logger("analyzer")


@analyzer.post("/analize")
async def analize(request: Request):
    data_json = await request.json()
    data = data_json.get("data")
    logger.debug(f"Got data: {data}")
    return {0: 1}


@analyzer.post("/predict")
async def predict(request: Request):
    data_json = await request.json()
    data = data_json.get("data")
    logger.debug(f"Got data: {data}")
    return {1: 1}
