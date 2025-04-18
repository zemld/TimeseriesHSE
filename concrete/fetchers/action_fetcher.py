from abstractions.data_fetcher import DataFetcher
from domain_objects.action import Action
import httpx
from logger import Logger


class ActionFetcher(DataFetcher[Action]):
    _url: str = (
        "https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/"
    )

    def __init__(self):
        self._logger = Logger("ActionFetcher")

    async def _get_raw_data(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.get_url())
            response.raise_for_status()
            self._logger.debug(f"Response status code: {response.status_code}")

        data = response.json()
        if not data:
            self._logger.info("No data fetched.")
            return {}
        return data

    def get_url(self) -> str:
        concrete_url = self._url
        if not self._params:
            raise ValueError("Parameters not set.")
        if not all(
            param in self._params for param in ["ticker", "from_date", "till_date"]
        ):
            raise ValueError("Missing required parameters.")
        ticker = self._params["ticker"]
        from_date = self._params["from_date"]
        till_date = self._params["till_date"]
        concrete_url += f"{ticker}.json?from={from_date}&till={till_date}&iss.meta=off"
        self._logger.info(f"Concrete URL: {concrete_url}")
        return concrete_url

    def parse_data(self, data):
        history_data = data.get("history", {})
        columns = history_data.get("columns", [])
        if not columns:
            self._logger.info("No data fetched.")
            return []

        tradedate_index = columns.index("TRADEDATE")
        close_index = columns.index("CLOSE")
        open_index = columns.index("OPEN")
        low_index = columns.index("LOW")
        high_index = columns.index("HIGH")
        trendclspr_index = columns.index("TRENDCLSPR")
        volume_index = columns.index("VOLUME")
        value_index = columns.index("VALUE")
        numtrades_index = columns.index("NUMTRADES")

        actions = []
        records = history_data.get("data", [])
        for record in records:
            try:
                record_date = str(record[tradedate_index])
                actions.append(
                    Action(
                        timestamp=record_date,
                        close=record[close_index],
                        open_value=record[open_index],
                        low=record[low_index],
                        high=record[high_index],
                        trendclspr=record[trendclspr_index],
                        volume=record[volume_index],
                        value=record[value_index],
                        numtrades=record[numtrades_index],
                    )
                )
                self._logger.debug(f"Action: {actions[-1]}")
            except Exception as e:
                self._logger.error(f"Error parsing record {record}: {e}")
                continue
        self._logger.info(f"Parsed {len(actions)} actions.")
        return actions
