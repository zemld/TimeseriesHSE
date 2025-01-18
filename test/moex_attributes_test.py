from datetime import date
from pytest import fixture
from moex.moex_request import MoexRequestAttributes


@fixture
def actions_request():
    return MoexRequestAttributes(
        category="stock", ticker="SBER", from_date=date(2023, 4, 3), till_date=date(2024, 8, 22)
    )


@fixture
def bonds_request():
    return MoexRequestAttributes(
        category="bonds", ticker="RU000A0ZZZ01", from_date=date(2023, 4, 3), till_date=date(2024, 8, 22)
    )


@fixture
def currency_request():
    return MoexRequestAttributes(
        category="currency", ticker="USD_RUB", from_date=date(2023, 4, 3), till_date=date(2024, 8, 22)
    )


def test_get_start_date(actions_request, bonds_request, currency_request):
    assert actions_request.get_start_date() == date(2023, 4, 3)
    assert bonds_request.get_start_date() == date(2023, 4, 3)
    assert currency_request.get_start_date() == date(2023, 4, 3)


def test_get_end_date(actions_request, bonds_request, currency_request):
    assert actions_request.get_end_date() == date(2024, 8, 22)
    assert bonds_request.get_end_date() == date(2024, 8, 22)
    assert currency_request.get_end_date() == date(2024, 8, 22)


def test_get_ticker(actions_request, bonds_request, currency_request):
    assert actions_request.get_ticker() == "SBER"
    assert bonds_request.get_ticker() == "RU000A0ZZZ01"
    assert currency_request.get_ticker() == "USD_RUB"


def test_date_to_string(actions_request):
    assert actions_request.date_to_string(date(2023, 4, 3)) == "2023-4-3"
    assert actions_request.date_to_string(date(2024, 8, 22)) == "2024-8-22"


def test_get_request_urls(actions_request, bonds_request, currency_request):
    action_urls = actions_request.get_request_urls()
    bond_urls = bonds_request.get_request_urls()
    currency_urls = currency_request.get_request_urls()

    # Проверяем первый URL для каждой категории
    assert action_urls[0] == (
        "https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/"
        "SBER.json?from=2023-4-3&till=2024-8-22&iss.meta=off"
    )
    assert bond_urls[0] == (
        "https://iss.moex.com/iss/history/engines/bonds/markets/shares/boards/TQBR/securities/"
        "RU000A0ZZZ01.json?from=2023-4-3&till=2024-8-22&iss.meta=off"
    )
    assert currency_urls[0] == (
        "https://iss.moex.com/iss/history/engines/currency/markets/shares/boards/TQBR/securities/"
        "USD_RUB.json?from=2023-4-3&till=2024-8-22&iss.meta=off"
    )