from fastapi import FastAPI
from logger import Logger
from pydantic import BaseModel


analyzer = FastAPI()
logger = Logger("analyzer")


class DataModel(BaseModel):
    series: dict


@analyzer.get("/analize")
def analize(data: DataModel):
    logger.debug(f"Got data: {data.series}")


@analyzer.get("/predict")
def predict(data: DataModel):
    logger.debug(f"Got data: {data.series}")
