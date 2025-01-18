import asyncpg
from datetime import date


class DatabaseManager:
    _host: str
    _port: int
    _name: str
    _user: str
    _password: str
    _pool: asyncpg.Pool

    def __init__(self, host: str, port: int, name: str, user: str, password: str):
        self._host = host
        self._port = port
        self._name = name
        self._user = user
        self._password = password
        self._pool = None

    async def _check_and_create_connetion(self) -> None:
        if self._pool is None:
            await self.connect()

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
            # TODO: добавить логгер.
            print("Connection created.")
        except Exception as e:
            print(f"Error with connection: {e}")

    async def create_table(self, table_name: str) -> None:
        await self._check_and_create_connetion()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            date DATE PRIMARY KEY,
            price DOUBLE PRECISION
        );
        """

        connection = await self._pool.acquire()
        try:
            await connection.execute(create_table_query)
            print(f"Table {table_name} created.")
        except Exception as e:
            print(f"Error with creating table: {e}")

    async def insert_data(self, table_name: str, data: dict) -> None:
        await self._check_and_create_connetion()
        insert_query = f"INSERT INTO {table_name} (date, price) VALUES\n\t"
        values = ",\n\t".join([f"('{date}', {price if price is not None else "null"})" for date, price in data.items()])
        insert_query += values + ";"

        connection = await self._pool.acquire()
        try:
            await connection.execute(insert_query)
            print(f"Data inserted into {table_name}.")
        except Exception as e:
            print(f"Error with inserting data: {e}")

    async def select_data(
        self, table_name: str, from_date: date, till_date: date
    ) -> dict[date, float]:
        await self._check_and_create_connetion()
        select_query = f"SELECT * FROM {table_name} WHERE date BETWEEN '{from_date}' AND '{till_date}';"

        connection = await self._pool.acquire()
        try:
            rows = await connection.fetch(select_query)
        except Exception as e:
            print(f"Error with selecting data: {e}")
            rows = []

        result = {row["date"]: row["price"] for row in rows}
        return result

    async def delete_data(self, table_name: str, till_date: date) -> None:
        await self._check_and_create_connetion()
        delete_query = f"DELETE FROM {table_name} WHERE date <= '{till_date}';"

        connection = await self._pool.acquire()
        try:
            await connection.execute(delete_query)
            print(f"Data deleted from {table_name}.")
        except Exception as e:
            print(f"Error with deleting data: {e}")
