import pytest
from unittest.mock import MagicMock, patch
from moex.moex_connector import MoexConnector
from moex.moex_request import MoexActionRequest, MoexBondRequest, MoexCurrencyRequest
from datetime import date

CONNECTOR = MoexConnector()


@pytest.fixture
def action_request():
    return MoexActionRequest("SBER", date(2023, 4, 3), date(2024, 8, 22))


@pytest.fixture
def bond_request():
    return MoexBondRequest("RU000A0ZZZ01", date(2023, 4, 3), date(2024, 8, 22))


@pytest.fixture
def currency_request():
    return MoexCurrencyRequest("USD_RUB", date(2023, 4, 3), date(2024, 8, 22))


def test_bad_status_code():
    response = MagicMock(status_code=500, text="Error")
    assert not CONNECTOR._is_response_correct(response)


def test_empty_text():
    response = MagicMock(status_code=200, text="")
    assert not CONNECTOR._is_response_correct(response)


def test_correct_response():
    response = MagicMock(status_code=200, text="Valid response")
    assert CONNECTOR._is_response_correct(response)


def test_fetch_data_action_request(action_request):
    with patch("requests.get") as mocked_get:
        mocked_get.return_value = MagicMock(
            status_code=200,
            text="Valid response",
            json=MagicMock(
                return_value={
                    "history": {
                        "columns": ["TRADEDATE", "WAPRICE"],
                        "data": [["2023-04-03", 100.5], ["2024-08-22", 101.5]],
                    }
                }
            ),
        )

        result = CONNECTOR.fetch_data(action_request)
        assert result == {date(2023, 4, 3): 100.5, date(2024, 8, 22): 101.5}
        assert mocked_get.call_count == len(action_request.get_request_urls())


def test_fetch_data_bond_request(bond_request):
    with patch("requests.get") as mocked_get:
        mocked_get.return_value = MagicMock(
            status_code=200,
            text="Valid response",
            json=MagicMock(
                return_value={
                    "history": {
                        "columns": ["TRADEDATE", "WAPRICE"],
                        "data": [["2023-04-03", 105.5], ["2024-08-22", 106.5]],
                    }
                }
            ),
        )

        result = CONNECTOR.fetch_data(bond_request)
        assert result == {date(2023, 4, 3): 105.5, date(2024, 8, 22): 106.5}
        assert mocked_get.call_count == len(bond_request.get_request_urls())


def test_fetch_data_currency_request(currency_request):
    with patch("requests.get") as mocked_get:
        mocked_get.return_value = MagicMock(
            status_code=200,
            text="Valid response",
            json=MagicMock(
                return_value={
                    "history": {
                        "columns": ["TRADEDATE", "WAPRICE"],
                        "data": [["2023-04-03", 75.5], ["2024-08-22", 76.5]],
                    }
                }
            ),
        )

        result = CONNECTOR.fetch_data(currency_request)
        assert result == {date(2023, 4, 3): 75.5, date(2024, 8, 22): 76.5}
        assert mocked_get.call_count == len(currency_request.get_request_urls())


def test_fetch_data_no_data(action_request):
    with patch("requests.get") as mocked_get:
        mocked_get.return_value = MagicMock(
            status_code=200,
            text="Valid response",
            json=MagicMock(
                return_value={
                    "history": {"columns": ["TRADEDATE", "WAPRICE"], "data": []}
                }
            ),
        )

        result = CONNECTOR.fetch_data(action_request)
        assert result == {}
        assert mocked_get.call_count == len(action_request.get_request_urls())


def test_fetch_data_missing_columns(action_request):
    with patch("requests.get") as mocked_get:
        mocked_get.return_value = MagicMock(
            status_code=200,
            text="Valid response",
            json=MagicMock(return_value={"history": {"data": [["2023-04-03", 100.5]]}}),
        )

        result = CONNECTOR.fetch_data(action_request)
        assert result == {}
        assert mocked_get.call_count == len(action_request.get_request_urls())


def test_fetch_data_incorrect_response(action_request):
    with patch("requests.get") as mocked_get:
        mocked_get.return_value = MagicMock(status_code=500, text="Error")

        result = CONNECTOR.fetch_data(action_request)
        assert result == {}
        assert mocked_get.call_count == len(action_request.get_request_urls())


def test_fetch_data_invalid_date_format(action_request):
    with patch("requests.get") as mocked_get:
        mocked_get.return_value = MagicMock(
            status_code=200,
            text="Valid response",
            json=MagicMock(
                return_value={
                    "history": {
                        "columns": ["TRADEDATE", "WAPRICE"],
                        "data": [["03-04-2023", 100.5]],
                    }
                }
            ),
        )

        with pytest.raises(ValueError):
            CONNECTOR.fetch_data(action_request)
        assert mocked_get.call_count == len(action_request.get_request_urls())
