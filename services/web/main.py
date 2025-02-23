from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import httpx
from logger import Logger

webapp = FastAPI()
templates = Jinja2Templates(directory="templates")
logger = Logger("webapp")


@webapp.get("/")
async def start(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@webapp.post("/chart-parameters")
async def handle_parameters(request: Request):
    parameters = await request.json()
    value = parameters.get("value")
    start_date = parameters.get("start_date")
    end_date = parameters.get("end_date")

    logger.info(f"Got parameters: {value}, {start_date}, {end_date}")

    redirect_url = (
        str(request.url_for("show_chart"))
        + f"?value={value}&start_date={start_date}&end_date={end_date}"
    )

    logger.info(f"Make redirect for {redirect_url}")

    return {"redirect": redirect_url}


@webapp.get("/chart")
async def show_chart(request: Request):
    parameters = request.query_params
    value = parameters.get("value")
    from_date = parameters.get("start_date")
    till_date = parameters.get("end_date")
    params = {"table_name": value, "from_date": from_date, "till_date": till_date}

    logger.debug(f"Sending request with params: {params}")
    r = httpx.get("http://db_service:8002/select_data", params=params)

    logger.info(f"Got info: {r.text}")
    return f"{r.text}"
