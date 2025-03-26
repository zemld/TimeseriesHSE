from moex_request import MoexRequestAttributes
from datetime import datetime
import requests
from logger import Logger

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
        close_index = columns.index("CLOSE")
        open_index = columns.index("OPEN")
        low_index = columns.index("LOW")
        high_index = columns.index("HIGH")
        trendclspr_index = columns.index("TRENDCLSPR")
        volume_index = columns.index("VOLUME")
        numtrades_index = columns.index("NUMTRADES")

        trades = []
        for data in data_as_jsons:
            records = data.get("history").get("data")
            for record in records:
                record_date = str(datetime.strptime(
                    record[tradedate_index], "%Y-%m-%d"
                ).date())
                trades.append(
                    {
                        "date": record_date,
                        "close": record[close_index],
                        "open": record[open_index],
                        "low": record[low_index],
                        "high": record[high_index],
                        "trendclspr": record[trendclspr_index],
                        "volume": record[volume_index],
                        "numtrades": record[numtrades_index],
                    }
                )

        self._logger.info(f"Fetched data: {trades}")
        return trades
