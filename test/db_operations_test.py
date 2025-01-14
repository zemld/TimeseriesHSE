from datetime import date
from db_connection import database_manager as dbc
import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def connector():
    conn = dbc.DatabaseManager("host", 5432, "name", "user", "password")
    conn._pool = AsyncMock()
    return conn


@pytest.mark.asyncio
async def test_connect(mocker, connector):
    mock = mocker.patch("asyncpg.create_pool")
    await connector.connect()
    mock.assert_called_once_with(
        user="user",
        password="password",
        database="name",
        host="host",
        port=5432,
        min_size=1,
        max_size=10,
    )


@pytest.mark.asyncio
async def test_check_and_create_connetion_when_pool_exists(mocker, connector):
    mock_connect = mocker.patch("db_connection.db_connector.DBConnector.connect")
    await connector._check_and_create_connetion()
    assert not mock_connect.connect.called


# TODO: исправить тесты
@pytest.mark.asyncio
async def test_check_and_create_connetion_when_pool_does_not_exist(mocker, connector):
    mock_connect = mocker.patch("db_connection.db_connector.DBConnector.connect")
    connector._pool = None
    await connector._check_and_create_connetion()
    mock_connect.assert_called_once()


@pytest.mark.asyncio
async def test_create_table_success(mocker, connector):
    mocker.patch("db_connection.db_connector.DBConnector._check_and_create_connetion")
    mocked_connection = AsyncMock()
    mocked_connection.execute = AsyncMock()
    connector._pool.acquire = AsyncMock(return_value=mocked_connection)

    await connector.create_table("TEST_TABLE")

    connector._check_and_create_connetion.assert_called_once()
    connector._pool.acquire.assert_called_once()
    mocked_connection.execute.assert_called_once()


@pytest.mark.asyncio
async def test_insert_data(mocker, connector):
    mocker.patch("db_connection.db_connector.DBConnector._check_and_create_connetion")
    mocked_connection = AsyncMock()
    mocked_connection.execute = AsyncMock()
    connector._pool.acquire = AsyncMock(return_value=mocked_connection)

    await connector.insert_data(
        "TEST_TABLE", {date(2022, 1, 1): 1.0, date(2022, 1, 2): 2.0}
    )

    connector._check_and_create_connetion.assert_called_once()
    connector._pool.acquire.assert_called_once()
    mocked_connection.execute.assert_called_once()


@pytest.mark.asyncio
async def test_select_data(mocker, connector):
    mocker.patch("db_connection.db_connector.DBConnector._check_and_create_connetion")
    mocked_connection = AsyncMock()
    mocked_connection.execute = AsyncMock()
    connector._pool.acquire = AsyncMock(return_value=mocked_connection)

    mocked_connection.fetch.return_value = [
        {"date": date(2022, 1, 1), "price": 1.0},
        {"date": date(2022, 1, 2), "price": 2.0},
    ]

    result = await connector.select_data(
        "TEST_TABLE", date(2022, 1, 1), date(2022, 1, 2)
    )

    assert result == {date(2022, 1, 1): 1.0, date(2022, 1, 2): 2.0}
    connector._check_and_create_connetion.assert_called_once()
    connector._pool.acquire.assert_called_once()
    mocked_connection.fetch.assert_called_once()


@pytest.mark.asyncio
async def test_delete_data(mocker, connector):
    mocker.patch("db_connection.db_connector.DBConnector._check_and_create_connetion")
    mocked_connection = AsyncMock()
    mocked_connection.execute = AsyncMock()
    connector._pool.acquire = AsyncMock(return_value=mocked_connection)

    await connector.delete_data("TEST_TABLE", date(2022, 1, 2))

    connector._check_and_create_connetion.assert_called_once()
    connector._pool.acquire.assert_called_once()
    mocked_connection.execute.assert_called_once()
