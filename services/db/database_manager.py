import asyncpg
from datetime import date
from logger import Logger


class DatabaseManager:
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
        self._logger = Logger("db_manager")

    async def _check_and_create_connetion(self) -> None:
        if self._pool is None:
            await self.connect()

    async def start_transaction(self) -> None:
        await self._check_and_create_connetion()
        transaction_query = "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
        async with self._pool.acquire() as connection:
            await connection.execute(transaction_query)
            self._logger.debug("Transaction started")

    async def rollback_transaction(self) -> None:
        await self._check_and_create_connetion()
        transaction_query = "ROLLBACK;"
        async with self._pool.acquire() as connection:
            await connection.execute(transaction_query)
            self._logger.debug("Transaction rolled back")

    async def end_transaction(self) -> None:
        await self._check_and_create_connetion()
        transaction_query = "COMMIT;"
        async with self._pool.acquire() as connection:
            await connection.execute(transaction_query)
            self._logger.debug("Transaction ended")

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
            self._logger.debug(f"Failed to create connection: {str(e)}")

    async def create_table(self, table_name: str) -> None:
        await self._check_and_create_connetion()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            date DATE PRIMARY KEY,
            price DOUBLE PRECISION
        );
        """

        async with self._pool.acquire() as connection:
            connection.execute(create_table_query)
        self._logger.info(f"Table {table_name} created")

    async def insert_data(self, table_name: str, data: dict) -> None:
        await self._check_and_create_connetion()
        insert_query = f"INSERT INTO {table_name} (date, price) VALUES\n\t"
        values = ",\n\t".join(
            [
                f"('{date}', {price if price is not None else "null"})"
                for date, price in data.items()
            ]
        )
        insert_query += values + "\nON CONFLICT (date) DO NOTHING;"

        async with self._pool.acquire() as connection:
            connection.execute(insert_query)
        self._logger.info(f"Data inserted into {table_name}")

    async def select_data(
        self, table_name: str, from_date: date, till_date: date
    ) -> dict[date, float]:
        await self._check_and_create_connetion()
        select_query = f"SELECT * FROM {table_name} WHERE date BETWEEN '{from_date}' AND '{till_date}';"

        rows = []
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(select_query)

        result = {row["date"]: row["price"] for row in rows}
        self._logger.info(f"Data selected from {table_name}: {result}")
        return result

    async def delete_data(self, table_name: str, till_date: date) -> None:
        await self._check_and_create_connetion()
        delete_query = f"DELETE FROM {table_name} WHERE date <= '{till_date}';"

        async with self._pool.acquire() as connection:
            connection.execute(delete_query)
        self._logger.info(f"Data deleted from {table_name}")
