from abstractions.db_manager import DBManager
from domain_objects.action import Action
from logger import Logger
from typing import List
from datetime import date


class ActionDBManager(DBManager[Action]):
    def __init__(self, host: str, port: int, name: str, user: str, password: str):
        super().__init__(host, port, name, user, password)
        self._logger = Logger("ActionDBManager")

    async def create_table(self, table_name: str):
        await self._check_and_create_connection()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            date TIMESTAMP PRIMARY KEY,
            close DOUBLE PRECISION,
            open DOUBLE PRECISION,
            low DOUBLE PRECISION,
            high DOUBLE PRECISION,
            trendclspr DOUBLE PRECISION,
            volume BIGINT,
            value DOUBLE PRECISION,
            numtrades INTEGER
        );
        """
        async with self._pool.acquire() as connection:
            await connection.execute(create_table_query)
            self._logger.info(f"Table {table_name} created or already exists.")

    async def insert(self, table_name: str, data: List[Action]):
        await self._check_and_create_connection()
        if not data or len(data) == 0:
            self._logger.warning("No data to insert.")
            return
        columns = [
            "date",
            "close",
            "open",
            "low",
            "high",
            "trendclspr",
            "volume",
            "value",
            "numtrades",
        ]
        values = [
            (
                date.fromisoformat(a.date_value),
                a.close,
                a.open_value,
                a.low,
                a.high,
                a.trendclspr,
                a.volume,
                a.value,
                a.numtrades,
            )
            for a in data
        ]

        query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (date) DO UPDATE SET
            close = EXCLUDED.close,
            open = EXCLUDED.open,
            low = EXCLUDED.low,
            high = EXCLUDED.high,
            trendclspr = EXCLUDED.trendclspr,
            volume = EXCLUDED.volume,
            value = EXCLUDED.value,
            numtrades = EXCLUDED.numtrades
        """

        async with self._pool.acquire() as conn:
            await conn.executemany(query, values)
            self._logger.info(f"Inserted {len(values)} records into table {table_name}")

    async def select(
        self, table_name: str, from_datetime: str, till_datetime: str
    ) -> List[Action]:
        await self._check_and_create_connection()
        select_query = f"""
        SELECT * FROM {table_name}
        WHERE date BETWEEN '{from_datetime}' AND '{till_datetime}'
        """
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(select_query)
            self._logger.info(
                f"Selected records from {table_name} between {from_datetime} and {till_datetime}"
            )
        actions = []
        for row in rows:
            action = Action(
                date_value=row["date"],
                close=row["close"],
                open_value=row["open"],
                low=row["low"],
                high=row["high"],
                trendclspr=row["trendclspr"],
                volume=row["volume"],
                value=row["value"],
                numtrades=row["numtrades"],
            )
            actions.append(action)
        return actions
