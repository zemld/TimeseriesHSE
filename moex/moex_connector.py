from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import requests
from enum import Enum


class MOEXConnector:
    class MOEXRequestAttributes:
        _ticket: str
        _from_date: date
        _till_date: date

        def __init__(
            self,
            ticket: str,
            from_date=datetime.today() - relativedelta(years=3),
            till_date=datetime.today(),
        ):
            self._ticket = ticket
            self._from_date = from_date
            self._till_date = till_date

        def get_start_date(self) -> date:
            return self._from_date

        def get_end_date(self) -> date:
            return self._till_date

        def get_ticket(self) -> str:
            return self._ticket

        def date_to_string(self, date: date) -> str:
            return f"{date.year}-{date.month}-{date.day}"

    _action_request: str = (
        "https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/"
    )
    _bond_request: str = (
        "https://iss.moex.com/iss/history/engines/bonds/markets/shares/boards/TQBR/securities/"
    )
    _currency_request: str = (
        "https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/CETS/securities/"
    )

    def _create_request(self, request_body: str, attributes: MOEXRequestAttributes):
        from_date: date = attributes.get_start_date()
        till_date: date = attributes.get_end_date()
        url = (
            request_body
            + attributes.get_ticket()
            + ".json"
            + "?from="
            + attributes.date_to_string(from_date)
            + "&till="
            + attributes.date_to_string(till_date)
            + "&iss.meta=off"
        )
        return url

    def get_actions(self, attributes: MOEXRequestAttributes):
        url = self._create_request(self._action_request, attributes)
        response = requests.get(url)
        return response.json()

    def get_bonds(self, attributes: MOEXRequestAttributes):
        url = self._create_request(self._bond_request, attributes)
        response = requests.get(url)
        return response.json()

    def get_currency(self, attributes: MOEXRequestAttributes):
        url = self._create_request(self._currency_request, attributes)
        response = requests.get(url)
        return response.json()