from moex.moex_connector import MOEXConnector as mc
from datetime import date
from pytest import fixture

@fixture
def actions_attributes():
    return mc.MOEXRequestAttributes(
        "SBER", from_date=date(2023, 4, 3), till_date=date(2024, 8, 22)
    )

@fixture
def bonds_attributes():
    return mc.MOEXRequestAttributes(
        "SU26209RMFS0", from_date=date(2023, 4, 3), till_date=date(2024, 8, 22)
    )

@fixture
def currency_attributes():
    return mc.MOEXRequestAttributes(
        "USD000000TOD", from_date=date(2023, 4, 3), till_date=date(2024, 8, 22)
    )

def test_get_start_date(actions_attributes, bonds_attributes, currency_attributes):
    assert actions_attributes.get_start_date() == date(2023, 4, 3)
    assert bonds_attributes.get_start_date() == date(2023, 4, 3)
    assert currency_attributes.get_start_date() == date(2023, 4, 3)

def test_get_end_date(actions_attributes, bonds_attributes, currency_attributes):
    assert actions_attributes.get_end_date() == date(2024, 8, 22)
    assert bonds_attributes.get_end_date() == date(2024, 8, 22)
    assert currency_attributes.get_end_date() == date(2024, 8, 22)

def test_get_ticket(actions_attributes, bonds_attributes, currency_attributes):
    assert actions_attributes.get_ticket() == "SBER"
    assert bonds_attributes.get_ticket() == "SU26209RMFS0"
    assert currency_attributes.get_ticket() == "USD000000TOD"

def test_date_to_string(actions_attributes):
    assert actions_attributes.date_to_string(date(2023, 4, 3)) == "2023-4-3"
    assert actions_attributes.date_to_string(date(2024, 8, 22)) == "2024-8-22"

def test_create_request(actions_attributes, bonds_attributes, currency_attributes):
    connector = mc()
    assert (
        connector._create_request(connector._action_request, actions_attributes)
        == "https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/SBER.json?from=2023-4-3&till=2024-8-22&iss.meta=off"
    )
    assert (
        connector._create_request(connector._bond_request, bonds_attributes)
        == "https://iss.moex.com/iss/history/engines/bonds/markets/shares/boards/TQBR/securities/SU26209RMFS0.json?from=2023-4-3&till=2024-8-22&iss.meta=off"
    )
    assert (
        connector._create_request(connector._currency_request, currency_attributes)
        == "https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/CETS/securities/USD000000TOD.json?from=2023-4-3&till=2024-8-22&iss.meta=off"
    )
