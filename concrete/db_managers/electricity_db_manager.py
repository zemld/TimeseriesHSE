from abstractions.db_manager import DBManager
from logger import Logger
from typing import List
from domain_objects.electricity_record import ElectricityRecord


class ElectricityDBManager(DBManager[ElectricityRecord]):
    def __init__(self, host: str, port: int, name: str, user: str, password: str):
        super().__init__(host, port, name, user, password)
        self._logger = Logger("ElectricityDBManager")

    async def create_table(self, table_name: str):
        await self._check_and_create_connection()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            timestamp TIMESTAMP PRIMARY KEY,
            value DOUBLE PRECISION
        );
        """
        async with self._pool.acquire() as connection:
            await connection.execute(create_table_query)
            self._logger.debug(f"Table {table_name} created or already exists.")

    async def insert(self, table_name: str, data: List[ElectricityRecord]):
        await self._check_and_create_connection()
        if not data:
            self._logger.debug(f"No data to insert into {table_name}.")
            return

        values_list = []
        for record in data:
            values_list.append((record.timestamp, record.value))

        insert_query = f"""
            INSERT INTO {table_name} (timestamp, value)
            VALUES ($1, $2)
            ON CONFLICT (timestamp) DO UPDATE
            SET value = EXCLUDED.value;
        """
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                await connection.executemany(insert_query, values_list)
                self._logger.debug(
                    f"Inserted {len(data)} records into {table_name} in a single query."
                )

    async def select(self, table_name: str, from_datetime: str, till_datetime: str):
        await self._check_and_create_connection()
        select_query = f"""
        SELECT * FROM {table_name}
        WHERE date BETWEEN '{from_datetime}' AND '{till_datetime}'
        """

        async with self._pool.acquire() as connection:
            rows = await connection.fetch(select_query)
            self._logger.info(
                f"Selected {len(rows)} records from {table_name} between {from_datetime} and {till_datetime}."
            )

        electricity_records = []
        for row in rows:
            record = ElectricityRecord(timestamp=row["timestamp"], value=row["value"])
            electricity_records.append(record)

        return electricity_records
