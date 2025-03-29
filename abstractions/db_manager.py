from abc import ABC, abstractmethod
import asyncpg
from logger import Logger
from typing import TypeVar, List

T = TypeVar("T")


class DBManager(ABC):
    _host: str
    _port: int
    _name: str
    _user: str
    _password: str
    _pool: asyncpg.Pool
    _logger: Logger

    def __init__(self, host: str, port: int, name: str, user: str, password: str):
        self._host = host
        self._port = port
        self._name = name
        self._user = user
        self._password = password
        self._pool = None

    async def _check_and_create_connection(self):
        if self._pool is None:
            await self.connect()
            self._logger.info("Database connection pool created.")

    async def connect(self):
        try:
            self._pool = await asyncpg.create_pool(
                user=self._user,
                password=self._password,
                database=self._name,
                host=self._host,
                port=self._port,
                min_size=1,
                max_size=10,
            )
            self._logger.debug("Connection created")
        except Exception as e:
            self._logger.error(f"Failed to create connection: {e}")
            raise

    async def disconnect(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._logger.debug("Connection closed")

    async def start_transaction(self):
        await self._check_and_create_connection()
        transaction_query = "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
        async with self._pool.acquire() as connection:
            await connection.execute(transaction_query)
            self._logger.debug("Transaction started")

    async def rollback_transaction(self):
        await self._check_and_create_connection()
        transaction_query = "ROLLBACK;"
        async with self._pool.acquire() as connection:
            await connection.execute(transaction_query)
            self._logger.debug("Transaction rolled back")

    async def commit_transaction(self):
        await self._check_and_create_connection()
        transaction_query = "COMMIT;"
        async with self._pool.acquire() as connection:
            await connection.execute(transaction_query)
            self._logger.debug("Transaction committed")

    @abstractmethod
    async def create_table(self, table_name: str):
        pass

    @abstractmethod
    async def insert(self, table_name: str, data: List[T]):
        pass

    @abstractmethod
    async def delete_data(self, table_name: str, till_datetime: str):
        pass

    @abstractmethod
    async def select(
        self, table_name: str, from_datetime: str, till_datetime: str
    ) -> List[T]:
        pass
