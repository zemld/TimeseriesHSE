from abc import ABC, abstractmethod
from typing import TypeVar, List
from logger import Logger

T = TypeVar("T")


class DataFetcher(ABC):
    _url: str
    _params: dict
    _logger: Logger

    async def fetch_data(self) -> List[T]:
        raw_data = await self._get_raw_data()
        records = self.parse_data(raw_data)
        return records

    @abstractmethod
    async def _get_raw_data(self) -> dict:
        pass

    @abstractmethod
    def parse_data(self, data: dict) -> List[T]:
        pass

    def set_params(self, params: dict) -> None:
        self._params = params

    @abstractmethod
    def get_url(self) -> str:
        pass