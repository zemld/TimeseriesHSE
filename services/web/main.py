from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from datetime import datetime
import httpx

webapp = FastAPI()
templates = Jinja2Templates(directory="templates")


@webapp.get("/")
async def start(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@webapp.post("/chart-parameters")
async def handle_parameters(request: Request):
    parameters = await request.json()
    category = parameters.get("category")
    value = parameters.get("value")
    start_date = parameters.get("start_date")
    end_date = parameters.get("end_date")

    redirect_url = webapp.url_path_for(
        "show_chart",
        category=category,
        value=value,
        start_date=start_date,
        end_date=end_date,
    )
    return {"redirect": redirect_url}


@webapp.get("/chart")
async def show_chart(request: Request):
    parameters = request.query_params
    value = parameters.get("value")
    from_date = datetime.strptime(parameters.get("start_date"), "%Y-%m-%d").date()
    till_date = datetime.strptime(parameters.get("end_date"), "%Y-%m-%d").date()
    params = {"table_name": value, "from_date": from_date, "till_date": till_date}
    r = httpx.get("http://db_service:8002/select_data", params=params)
    print(r.url)
    return f"{r.text}"
