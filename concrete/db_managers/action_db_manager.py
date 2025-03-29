from abstractions.db_manager import DBManager
from domain_objects.action import Action
from logger import Logger
from typing import List


class ActionDBManager(DBManager):
    def __init__(self, host: str, port: int, name: str, user: str, password: str):
        super().__init__(host, port, name, user, password)
        self._logger = Logger("ActionDBManager")

    async def create_table(self, table_name: str, columns: dict):
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
        values = []
        for date, action in data.items():
            values.append(
                (
                    date,
                    action.close,
                    action.open,
                    action.low,
                    action.high,
                    action.trendclspr,
                    action.volume,
                    action.value,
                    action.numtrades,
                )
            )

        placeholders = ",".join(
            [
                f"({','.join(['$'+str(i) for i in range(j*len(columns)+1, (j+1)*len(columns)+1)])})"
                for j in range(len(values))
            ]
        )

        insert_query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES {placeholders}
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

        flat_values = [val for tup in values for val in tup]

        async with self._pool.acquire() as connection:
            await connection.execute(insert_query, *flat_values)
            self._logger.info(f"Inserted {len(values)} records into table {table_name}")

    async def delete_data(self, table_name: str, till_datetime: str):
        await self._check_and_create_connection()
        delete_query = f"DELETE FROM {table_name} WHERE date < '{till_datetime}'"
        async with self._pool.acquire() as connection:
            await connection.execute(delete_query)
            self._logger.info(
                f"Deleted records from {table_name} older than {till_datetime}"
            )

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
