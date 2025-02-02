import asyncio
import tickers
import time
from logger import Logger
import schedule
from typing import List
from moex.moex_request import MoexRequestAttributes
from moex.moex_connector import MoexConnector
from db_connection.database_manager import DatabaseManager


class DataUpdater:
    _tickers: List[str] = tickers.get_all_action_tickers()
    _logger: Logger = Logger("data_updater")

    def get_attributes(self) -> List[MoexRequestAttributes]:
        return [MoexRequestAttributes("stock", ticker) for ticker in self._tickers]

    def _get_data(self, attribute: MoexRequestAttributes) -> dict:
        mc = MoexConnector()
        data = mc.fetch_data(attribute)
        return data

    async def connect_to_db_and_update_data(self, table: str, data: dict):
        db = DatabaseManager("db", 5432, "db", "user", "secret")
        await db.connect()
        await db.start_transaction()
        try:
            await db.create_table(table)
            # self._logger.debug("deletion")
            # await db.delete_data(table_name, attribute.get_from_date())
            self._logger.debug("insertion")
            await db.insert_data(table, data)
        except Exception as e:
            self._logger.error(f"Error: {e}")
            await db.rollback_transaction()
        await db.end_transaction()

    async def update_data(self, attribute: MoexRequestAttributes):
        data = self._get_data(attribute)
        table_name = attribute.get_ticker()
        await self.connect_to_db_and_update_data(table_name, data)
        self._logger.info(f"Data for {attribute.get_ticker()} updated.")

    async def update_all_data(self):
        self._logger.info("Update started.")
        attributes = self.get_attributes()
        for attribute in attributes:
            self._logger.debug(attribute.get_ticker())
            await self.update_data(attribute)
        self._logger.info("All data updated.")

    def schedule_updates(self):
        schedule.every(10).seconds.do(lambda: asyncio.run(self.update_all_data()))
        # schedule.every().day.at("10:56").do(self.update_all_data)
        while True:
            self._logger.info("action")
            schedule.run_pending()
            time.sleep(2)


if __name__ == "__main__":
    updater = DataUpdater()
    updater.schedule_updates()
