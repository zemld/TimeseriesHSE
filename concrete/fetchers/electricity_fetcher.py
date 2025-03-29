from abstractions.data_fetcher import DataFetcher
from domain_objects.electricity_record import ElectricityRecord
import httpx


class ElectricityFetcher(DataFetcher[ElectricityRecord]):
    _url: str = "https://www.elprisetjustnu.se/api/v1/prices/"

    async def _get_raw_data(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.get_url())
            response.raise_for_status()

        data = response.json()
        if not data:
            self._logger.info("No data fetched.")
            return {}

    def get_url(self) -> str:
        concrete_url = self._url
        if not self._params:
            raise ValueError("Parameters not set.")
        if not all(param in self._params for param in ["year", "month", "day"]):
            raise ValueError("Missing required parameters.")
        year = self._params["year"]
        month = self._params["month"]
        day = self._params["day"]
        concrete_url += f"{year}/{month}-{day}_SE3.json"
        self._logger.info(f"Concrete URL: {concrete_url}")

        return concrete_url

    def parse_data(self, data):
        records = []
        for record in data:
            records.append(
                ElectricityRecord(
                    date=record["time_start"],
                    price=record["EUR_per_kWh"],
                )
            )
        return records
