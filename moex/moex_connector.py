from moex.moex_request import MoexRequestAttributes
from datetime import datetime
from logger import Logger
import requests

SUCCESS = 200


class MoexConnector:
    _logger: Logger

    def __init__(self):
        self._logger = Logger("moex")

    def _is_response_correct(self, response):
        if response.status_code != SUCCESS or response.text == "":
            self._logger.debug("Response is incorrect.")
            return False
        
        self._logger.debug("Response is correct.")
        return True

    def _get_data(self, attributes: MoexRequestAttributes):
        urls = attributes.get_request_urls()
        data = []
        for url in urls:
            response = requests.get(url)
            if self._is_response_correct(response):
                data.append(response.json())

        self._logger.info(f"Collected data.")
        return data

    def fetch_data(self, attributes: MoexRequestAttributes):
        data_as_jsons = self._get_data(attributes)

        if not data_as_jsons:
            self._logger.info("No data fetched.")
            return {}

        history_data = data_as_jsons[0].get("history", {})
        columns = history_data.get("columns", [])
        if not columns:
            self._logger.info("No data fetched.")
            return {}

        tradedate_index = columns.index("TRADEDATE")
        waprice_index = columns.index("WAPRICE")

        trades = {}
        for data in data_as_jsons:
            records = data.get("history").get("data")
            for record in records:
                record_date = datetime.strptime(
                    record[tradedate_index], "%Y-%m-%d"
                ).date()
                trades[record_date] = record[waprice_index]

        self._logger.info(f"Fetched data: {trades}")
        return trades
