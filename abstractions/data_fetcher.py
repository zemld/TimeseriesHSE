from abc import ABC, abstractmethod
from typing import TypeVar, List
from logger import Logger

T = TypeVar("T")


class DataFetcher(ABC):
    _url: str
    _params: dict
    _logger: Logger

    @abstractmethod
    async def fetch_data(self) -> List[T]:
        pass

    def set_params(self, params: dict) -> None:
        self._params = params

    def get_url(self) -> str:
        concrete_url = self._url
        if self._params:
            concrete_url += "?"
            for key, value in self._params.items():
                concrete_url += f"{key}={value}&"
            concrete_url = concrete_url[:-1]
        self._logger.info(f"Concrete URL: {concrete_url}")
        return concrete_url
