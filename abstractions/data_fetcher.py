from abc import ABC, abstractmethod
from typing import TypeVar, List

T = TypeVar("T")


class DataFetcher(ABC):
    _url: str
    _params: dict

    @abstractmethod
    async def fetch_data(self) -> List[T]:
        pass
    