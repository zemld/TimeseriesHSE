from fastapi import FastAPI, BackgroundTasks
from fastapi_utils.tasks import repeat_every
from datetime import datetime
from dateutil.relativedelta import relativedelta
import httpx
import tickers

data_updater = FastAPI()


async def update_ticker_data(ticker: str):
    async with httpx.AsyncClient() as client:
        from_date = datetime.today().date() - relativedelta(years=3)
        till_date = datetime.today().date()
        moex_response = await client.post(
            "http://moex_service:8001/fetch_data",
            json={
                "ticker": ticker,
                "from_date": from_date.isoformat(),
                "till_date": till_date.isoformat(),
            },
        )
        data = moex_response.json()["data"]

        await client.post("http://db_service:8002/create_table", params=f"{ticker}")
        await client.post(
            "http://db_service:8002/delete_data",
            json={"table_name": ticker, "till_date": till_date},
        )
        await client.post(
            "http://db_service:8002/insert_data" "http://db_service:8002/insert_data",
            json={"table_name": ticker, "data": data},
        )


@data_updater.on_event("startup")
@repeat_every(seconds=60 * 60 * 24, wait_first=True)
async def scheduled_update():
    for ticker in tickers.get_all_action_tickers():
        await update_ticker_data(ticker)


@data_updater.post("/trigger_update")
async def trigger_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(scheduled_update)
    return {"message": "Update triggered"}
