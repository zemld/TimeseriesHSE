from moex_request import MoexRequest
from datetime import datetime
import requests

SUCCESS = 200


class MoexConnector:
    def _is_response_correct(self, response):
        if response.status_code != SUCCESS or response.text == "":
            return False
        return True

    def _get_data(self, attributes: MoexRequest):
        urls = attributes.get_request_urls()
        data = []
        for url in urls:
            response = requests.get(url)
            if self._is_response_correct(response):
                data.append(response.json())

        return data

    def fetch_data(self, attributes: MoexRequest):
        data_as_jsons = self._get_data(attributes)

        if not data_as_jsons:
            return {}

        history_data = data_as_jsons[0].get("history", {})
        columns = history_data.get("columns", [])
        if not columns:
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

        return trades
