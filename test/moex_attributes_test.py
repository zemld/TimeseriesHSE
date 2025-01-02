from moex.moex_connector import MOEXConnector as mc
from datetime import date

FIRST_DATE = date(2023, 4, 3)
SECOND_DATE = date(2024, 8, 22)
ACTIONS_TICKET = "SBER"
BONDS_TICKET = "SU26209RMFS0"
CURRENCY_TICKET = "USD000000TOD"

ACTIONS_ATTRIBUTES = mc.MOEXRequestAttributes("SBER", from_date=FIRST_DATE, till_date=SECOND_DATE)
BONDS_ATTRIBUTES = mc.MOEXRequestAttributes("SU26209RMFS0", from_date=FIRST_DATE, till_date=SECOND_DATE)
CURRENCY_ATTRIBUTES = mc.MOEXRequestAttributes("USD000000TOD", from_date=FIRST_DATE, till_date=SECOND_DATE)

def test_get_start_date():
    assert ACTIONS_ATTRIBUTES.get_start_date() == FIRST_DATE
    assert BONDS_ATTRIBUTES.get_start_date() == FIRST_DATE
    assert CURRENCY_ATTRIBUTES.get_start_date() == FIRST_DATE

def test_get_end_date():
    assert ACTIONS_ATTRIBUTES.get_end_date() == SECOND_DATE
    assert BONDS_ATTRIBUTES.get_end_date() == SECOND_DATE
    assert CURRENCY_ATTRIBUTES.get_end_date() == SECOND_DATE

def test_get_ticket():
    assert ACTIONS_ATTRIBUTES.get_ticket() == "SBER"
    assert BONDS_ATTRIBUTES.get_ticket() == "SU26209RMFS0"
    assert CURRENCY_ATTRIBUTES.get_ticket() == "USD000000TOD"

def test_date_to_string():
    assert ACTIONS_ATTRIBUTES.date_to_string(FIRST_DATE) == "2023-4-3"
    assert ACTIONS_ATTRIBUTES.date_to_string(SECOND_DATE) == "2024-8-22"

def test_create_request():
    connector = mc()
    assert connector._create_request(connector._action_request, ACTIONS_ATTRIBUTES) == "https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/SBER.json?from=2023-4-3&till=2024-8-22&iss.meta=off"
    assert connector._create_request(connector._bond_request, BONDS_ATTRIBUTES) == "https://iss.moex.com/iss/history/engines/bonds/markets/shares/boards/TQBR/securities/SU26209RMFS0.json?from=2023-4-3&till=2024-8-22&iss.meta=off"
    assert connector._create_request(connector._currency_request, CURRENCY_ATTRIBUTES) == "https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/CETS/securities/USD000000TOD.json?from=2023-4-3&till=2024-8-22&iss.meta=off"

