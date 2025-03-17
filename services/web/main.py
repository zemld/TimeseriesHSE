from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from logger import Logger
from tickers import action_value_to_enum

webapp = FastAPI()
templates = Jinja2Templates(directory="templates")
logger = Logger("webapp")


async def fetch_finance_parameters(request: Request):
    parameters = await request.json()
    logger.debug(f"Got parameters: {parameters}")
    value = action_value_to_enum(parameters.get("value")).value
    start_date = parameters.get("start_date")
    end_date = parameters.get("end_date")
    return (value, start_date, end_date)


@webapp.get("/")
async def start(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@webapp.get("/actions")
async def choose_action(request: Request):
    return templates.TemplateResponse("actions.html", {"request": request})


@webapp.post("/make-action-analysis")
async def run_action_flow(request: Request):
    (table_name, from_date, till_date) = await fetch_finance_parameters(request)
    logger.debug(f"Sending request with params: {table_name, from_date, till_date}")

    try:
        async with httpx.AsyncClient() as client:
            db_response = await client.get(
                "http://db_service:8002/select_data",
                params={
                    "table_name": table_name,
                    "from_date": from_date,
                    "till_date": till_date,
                },
            )
            logger.info(f"Got info: {db_response.text}")

            data_json = db_response.json()
            data = data_json.get("data")
            if not data:
                raise Exception("No data found")

            logger.debug(f"Sending data to analyzer: {data}")
            analize_response = await client.post(
                "http://analyzer_service:8004/analize", json={"data": data}
            )
            logger.debug(analize_response.text)
            predict_response = await client.post(
                "http://analyzer_service:8004/predict", json={"data": data}
            )
            logger.debug(predict_response.text)
    except Exception as e:
        logger.error(e)
        return RedirectResponse(url=f"/error?error={e}")


@webapp.get("/electricity")
async def choose_electricity(request: Request):
    return templates.TemplateResponse("electricity.html", {"request": request})

@webapp.post("/make-electricity-analysis")
async def run_electricity_flow(request: Request):
    pass

# @webapp.get("/flights")
# async def choose_flight(request: Request):
#     return templates.TemplateResponse("flights.html", {"request": request})


# @webapp.post("/make-flight-analysis")
# async def run_flight_flow(request: Request):
#     pass

@webapp.get("/error")
async def handle_error(request: Request):
    error = request.get("error")
    return f"Error: {error}"
