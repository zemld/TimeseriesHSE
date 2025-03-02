from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from logger import Logger

webapp = FastAPI()
templates = Jinja2Templates(directory="templates")
logger = Logger("webapp")


async def fetch_parameters(request: Request):
    parameters = await request.json()
    value = parameters.get("value")
    start_date = parameters.get("start_date")
    end_date = parameters.get("end_date")
    return (value, start_date, end_date)


@webapp.get("/")
async def start(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@webapp.get("/make-analysis")
async def run_flow(request: Request):
    select_data_parameters = await fetch_parameters(request)
    logger.debug(f"Sending request with params: {select_data_parameters}")

    try:
        async with httpx.AsyncClient() as client:
            db_response = await client.get(
                "http://db_service:8002/select_data",
                params=dict(
                    zip(
                        ["table_name", "from_date", "till_date"], select_data_parameters
                    )
                ),
            )
            logger.info(f"Got info: {db_response.text}")

            data = db_response.get("data")
            if not data:
                raise Exception("No data found")

            logger.debug(f"Sending data to analyzer: {data}")
            analize_response = await client.get(
                "http://analyzer:8003/analize", params={"data": data}
            )
            predict_response = await client.get(
                "http://analyzer:8003/predict", params={"data": data}
            )
    except Exception as e:
        logger.error(e)
        return RedirectResponse(url=f"/error?error={e}")


@webapp.get("/error")
async def handle_error(request: Request):
    error = request.get("error")
    return f"Error: {error}"
