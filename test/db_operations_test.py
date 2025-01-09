import pytest
from unittest.mock import AsyncMock
from db_connection import db_connector as dbc


@pytest.fixture
def connector():
    conn = dbc.DBConnector("host", 5432, "name", "user", "password")
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
    mock = mocker.patch("db_connection.db_connector.DBConnector.connect")
    await connector._check_and_create_connetion()
    assert not mock.connect.called


@pytest.mark.asyncio
async def test_check_and_create_connetion_when_pool_does_not_exist(mocker, connector):
    mock = mocker.patch("db_connection.db_connector.DBConnector.connect")
    connector._pool = None
    await connector._check_and_create_connetion()
    mock.assert_called_once()
