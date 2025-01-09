from datetime import date
from moex import moex_connector as mc
from pytest import fixture

CONNECTOR = mc.MOEXConnector()


@fixture
def actions_attributes():
    return mc.MOEXConnector.MOEXRequestAttributes(
        "SBER", from_date=date(2023, 4, 3), till_date=date(2024, 8, 22)
    )


@fixture
def bonds_attributes():
    return mc.MOEXConnector.MOEXRequestAttributes(
        "SU26209RMFS0", from_date=date(2023, 4, 3), till_date=date(2024, 8, 22)
    )


@fixture
def currency_attributes():
    return mc.MOEXConnector.MOEXRequestAttributes(
        "USD000000TOD", from_date=date(2023, 4, 3), till_date=date(2024, 8, 22)
    )


def test_bad_status_code(mocker):
    mocked_response = mocker.MagicMock(status_code=500, text="Result text")
    assert not CONNECTOR._is_response_correct(mocked_response)


def test_empty_text(mocker):
    mocked_response = mocker.MagicMock(status_code=200, text="")
    assert not CONNECTOR._is_response_correct(mocked_response)


def test_correct_response(mocker):
    mocked_response = mocker.MagicMock(status_code=200, text="Result text")
    assert CONNECTOR._is_response_correct(mocked_response)


def test_success_get_actions(mocker, actions_attributes):
    mocked_response = mocker.patch("moex.moex_connector.requests.get")
    mocked_response.return_value.status_code = 200
    mocked_response.return_value.text = "Result text"
    mocked_response.return_value.json.return_value = {"data": "data"}

    assert CONNECTOR.get_actions(actions_attributes) == {"data": "data"}
    mocked_response.assert_called_once_with(CONNECTOR._create_request(CONNECTOR._action_request, actions_attributes))


def test_failed_get_actions(mocker, actions_attributes):
    mocked_response = mocker.patch("moex.moex_connector.requests.get")
    mocked_response.return_value.status_code = 500
    mocked_response.return_value.text = "Result text"
    mocked_response.return_value.json.return_value = {"data": "data"}

    assert CONNECTOR.get_actions(actions_attributes) is None
    mocked_response.assert_called_once_with(CONNECTOR._create_request(CONNECTOR._action_request, actions_attributes))


def test_empty_result_get_actions(mocker, actions_attributes):
    mocked_response = mocker.patch("moex.moex_connector.requests.get")
    mocked_response.return_value.status_code = 200
    mocked_response.return_value.text = ""
    mocked_response.return_value.json.return_value = {"data": "data"}

    assert CONNECTOR.get_actions(actions_attributes) is None
    mocked_response.assert_called_once_with(CONNECTOR._create_request(CONNECTOR._action_request, actions_attributes))


def test_success_get_bonds(mocker, bonds_attributes):
    mocked_response = mocker.patch("moex.moex_connector.requests.get")
    mocked_response.return_value.status_code = 200
    mocked_response.return_value.text = "Result text"
    mocked_response.return_value.json.return_value = {"data": "data"}

    assert CONNECTOR.get_bonds(bonds_attributes) == {"data": "data"}
    mocked_response.assert_called_once_with(CONNECTOR._create_request(CONNECTOR._bond_request, bonds_attributes))


def test_failed_get_bonds(mocker, bonds_attributes):
    mocked_response = mocker.patch("moex.moex_connector.requests.get")
    mocked_response.return_value.status_code = 500
    mocked_response.return_value.text = "Result text"
    mocked_response.return_value.json.return_value = {"data": "data"}

    assert CONNECTOR.get_bonds(bonds_attributes) is None
    mocked_response.assert_called_once_with(CONNECTOR._create_request(CONNECTOR._bond_request, bonds_attributes))


def test_empty_result_get_bonds(mocker, bonds_attributes):
    mocked_response = mocker.patch("moex.moex_connector.requests.get")
    mocked_response.return_value.status_code = 200
    mocked_response.return_value.text = ""
    mocked_response.return_value.json.return_value = {"data": "data"}

    assert CONNECTOR.get_bonds(bonds_attributes) is None
    mocked_response.assert_called_once_with(CONNECTOR._create_request(CONNECTOR._bond_request, bonds_attributes))


def test_success_get_currency(mocker, currency_attributes):
    mocked_response = mocker.patch("moex.moex_connector.requests.get")
    mocked_response.return_value.status_code = 200
    mocked_response.return_value.text = "Result text"
    mocked_response.return_value.json.return_value = {"data": "data"}

    assert CONNECTOR.get_currency(currency_attributes) == {"data": "data"}
    mocked_response.assert_called_once_with(CONNECTOR._create_request(CONNECTOR._currency_request, currency_attributes))


def test_failed_get_currency(mocker, currency_attributes):
    mocked_response = mocker.patch("moex.moex_connector.requests.get")
    mocked_response.return_value.status_code = 500
    mocked_response.return_value.text = "Result text"
    mocked_response.return_value.json.return_value = {"data": "data"}

    assert CONNECTOR.get_currency(currency_attributes) is None
    mocked_response.assert_called_once_with(CONNECTOR._create_request(CONNECTOR._currency_request, currency_attributes))


def test_empty_result_get_currency(mocker, currency_attributes):
    mocked_response = mocker.patch("moex.moex_connector.requests.get")
    mocked_response.return_value.status_code = 200
    mocked_response.return_value.text = ""
    mocked_response.return_value.json.return_value = {"data": "data"}

    assert CONNECTOR.get_currency(currency_attributes) is None
    mocked_response.assert_called_once_with(CONNECTOR._create_request(CONNECTOR._currency_request, currency_attributes))


def test_get_part_of_data(mocker, actions_attributes):
    mocked_response = mocker.patch("moex.moex_connector.MOEXConnector.get_actions")
    mocked_response.return_value = {
        "history": {
            "columns": ["TRADEDATE", "WAPRICE"],
            "data": [["2023-4-10", 2], ["2024-8-22", 4]],
        }
    }

    assert CONNECTOR.get_part_of_data(
        mc.MOEXConnector.RequestType.ACTIONS, actions_attributes
    ) == {"2023-4-10": 2, "2024-8-22": 4}
    mocked_response.assert_called_once_with(actions_attributes)


def test_get_part_of_data_incorrect_response(mocker, actions_attributes):
    mocked_response = mocker.patch("moex.moex_connector.MOEXConnector.get_actions")
    mocked_response.return_value = None

    assert CONNECTOR.get_part_of_data(mc.MOEXConnector.RequestType.ACTIONS, actions_attributes) == {}
    mocked_response.assert_called_once_with(actions_attributes)


def test_get_part_of_data_empty(mocker, actions_attributes):
    mocked_response = mocker.patch("moex.moex_connector.MOEXConnector.get_actions")
    mocked_response.return_value.json.return_value = {}

    assert CONNECTOR.get_part_of_data(mc.MOEXConnector.RequestType.ACTIONS, actions_attributes) == {}
    mocked_response.assert_called_once_with(actions_attributes)