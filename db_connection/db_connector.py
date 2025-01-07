import asyncpg


class DBConnector:
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

    def _chech_and_create_connetion(self) -> None:
        if self.pool is None:
            self.connect()

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
        self._chech_and_create_connetion()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            date DATE PRIMARY KEY,
            price DOUBLE
        );
        """
        
        async with self._pool.acquire() as connection:
            await connection.execute(create_table_query)
            print(f"Table {table_name} created.")

    async def insert_data(self, table_name: str, data: dict) -> None:
        self._chech_and_create_connetion()
        insert_query = f"INSERT INTO {table_name} (date, price) VALUES\n\t"
        values = ",\n\t".join([f"('{date}', {price})" for date, price in data.items()])
        insert_query += values + ";"
        
        async with self._pool.acquire() as connection:
            await connection.execute(insert_query)
            print(f"Data inserted into {table_name}.")
