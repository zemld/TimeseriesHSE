from abc import ABC, abstractmethod
from typing import TypeVar, List

T = TypeVar("T")


class DataFetcher(ABC):
    _url: str
    _params: dict

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
        return concrete_url
