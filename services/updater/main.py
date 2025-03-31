import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi_utils.tasks import repeat_every
from datetime import datetime
import httpx
import tickers
from logger import Logger
from dateutil.relativedelta import relativedelta

data_updater = FastAPI()
logger = Logger("updater")


async def update_finance_data(ticker: str, from_date: str, till_date: str):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.debug(f"From date: {from_date}, Till date: {till_date}")
            update_response = await client.post(
                "http://finance:8005/update_data",
                params={
                    "ticker": ticker,
                    "from_date": from_date,
                    "till_date": till_date,
                },
            )

            if update_response.status_code != 200:
                logger.error(f"Failed to update data in DB: {update_response.text}")
                return

            logger.debug(f"Data for {ticker} updated successfully.")
    except Exception as e:
        logger.error(f"Failed to update {ticker}: {str(e)}")


async def update_electricity_data():
    today = datetime.today().date()
    current_date = today - relativedelta(days=50)
    while current_date < today:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                update_response = await client.post(
                    "http://electricity:8007/update_data",
                    params={"date": current_date.strftime("%Y-%m-%d")},
                )

                if update_response.status_code != 200:
                    logger.error(
                        f"Failed to update electricity data in DB: {update_response.text}"
                    )
                    return

                logger.debug("Electricity data updated successfully.")
        except Exception as e:
            logger.error(f"Failed to fetch electricity data: {str(e)}")
        finally:
            current_date += relativedelta(days=1)


@data_updater.on_event("startup")
@repeat_every(seconds=86400, wait_first=False)
async def scheduled_update():
    logger.info("Update scheduled")
    today = datetime.today().date()
    from_date = today - relativedelta(years=3)
    try:
        tickers_list = tickers.get_all_action_tickers()
        logger.debug(f"Tickers list: {tickers_list}")
        finance_tasks = [
            update_finance_data(ticker, from_date, today) for ticker in tickers_list
        ]
        tasks = finance_tasks + [update_electricity_data()]
        await asyncio.gather(*tasks)

        logger.info("Update completed successfully")
    except Exception as e:
        logger.error(f"Error during scheduled update: {str(e)}")


@data_updater.post("/trigger_update")
async def trigger_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(scheduled_update)
    logger.info("Update triggered.")
    return {"status": "update_triggered"}
