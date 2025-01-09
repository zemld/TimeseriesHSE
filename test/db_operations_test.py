from datetime import date
from db_connection import db_connector as dbc
import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def connector():
    conn = dbc.DBConnector("host", 5432, "name", "user", "password")
    conn._pool = AsyncMock()
    conn._check_and_create_connetion = AsyncMock()
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
    mocked_connect = AsyncMock()
    connector.connect = mocked_connect
    connector._pool = None
    await connector._check_and_create_connetion()
    mocked_connect.assert_called_once()


@pytest.mark.asyncio
async def test_create_table(mocker, connector):
    mocked_pool = AsyncMock()
    connector._pool = mocked_pool

    mock_acquire = AsyncMock()
    mocked_pool.acquire.return_value = mock_acquire

    mocked_connection = AsyncMock()
    mock_acquire.__aenter__.return_value = mocked_connection
    mocked_connection.execute = AsyncMock()

    await connector.create_table("TEST_TABLE")
    mocked_connection.execute.assert_called_once_with(
        """
        CREATE TABLE IF NOT EXISTS TEST_TABLE (
            date DATE PRIMARY KEY,
            price DOUBLE
        );
        """
    )


@pytest.mark.asyncio
async def test_insert_data(mocker, connector):
    mocked_pool = AsyncMock()
    connector._pool = mocked_pool

    mock_acquire = AsyncMock()
    mocked_pool.acquire.return_value = mock_acquire

    mocked_connection = AsyncMock()
    mock_acquire.__aenter__.return_value = mocked_connection
    mocked_connection.execute = AsyncMock()

    await connector.insert_data("TEST_TABLE", {"2022-01-01": 1.0, "2022-01-02": 2.0})
    mocked_connection.execute.assert_called_once_with(
        "INSERT INTO TEST_TABLE (date, price) VALUES\n\t('2022-01-01', 1.0),\n\t('2022-01-02', 2.0);"
    )


@pytest.mark.asyncio
async def test_select_data(mocker, connector):
    mocked_pool = AsyncMock()
    connector._pool = mocked_pool

    mock_acquire = AsyncMock()
    mocked_pool.acquire.return_value = mock_acquire

    mocked_connection = AsyncMock()
    mock_acquire.__aenter__.return_value = mocked_connection
    mocked_connection.fetch.return_value = {"2022-01-01": 1.0, "2022-01-02": 2.0}

    result = await connector.select_data(
        "TEST_TABLE", date(2022, 1, 1), date(2022, 1, 2)
    )
    assert result == {"2022-01-01": 1.0, "2022-01-02": 2.0}
    mocked_connection.fetch.assert_called_once_with(
        "SELECT * FROM TEST_TABLE WHERE date BETWEEN '2022-01-01' AND '2022-01-02';"
    )


@pytest.mark.asyncio
async def test_delete_data(mocker, connector):
    mocked_pool = AsyncMock()
    connector._pool = mocked_pool

    mock_acquire = AsyncMock()
    mocked_pool.acquire.return_value = mock_acquire

    mocked_connection = AsyncMock()
    mock_acquire.__aenter__.return_value = mocked_connection
    mocked_connection.execute = AsyncMock()

    await connector.delete_data("TEST_TABLE", date(2022, 1, 2))
    mocked_connection.execute.assert_called_once_with(
        "DELETE FROM TEST_TABLE WHERE date <= '2022-01-02';"
    )
