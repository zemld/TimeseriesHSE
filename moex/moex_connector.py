from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import requests
from enum import Enum

SUCCESS = 200

class MOEXConnector:
    # TODO Придумать, как реализовать определение тикета (возможно, сделать перечисление)
    class RequestType(Enum):
        ACTIONS = 1
        BONDS = 2
        CURRENCY = 3

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
        if response.status_code != SUCCESS:
            return None
        return response.json()

    def get_bonds(self, attributes: MOEXRequestAttributes):
        url = self._create_request(self._bond_request, attributes)
        response = requests.get(url)
        if response.status_code != SUCCESS:
            return None
        return response.json()

    def get_currency(self, attributes: MOEXRequestAttributes):
        url = self._create_request(self._currency_request, attributes)
        response = requests.get(url)
        if response.status_code != SUCCESS:
            return None
        return response.json()
    
    def get_part_of_data(self, type: RequestType, attributes: MOEXRequestAttributes):
        if (type == self.RequestType.ACTIONS):
            response = self.get_actions(attributes)
        elif (type == self.RequestType.BONDS):
            response = self.get_bonds(attributes)
        else:
            response = self.get_currency(attributes)
        
        if response is None:
            return None
        
        history_data = response.get("history", {})
        columns = history_data.get("columns", [])
        if not columns:
            return None
        
        trade_date_index = columns.index("TRADEDATE")
        value_index = columns.index("VALUE")

        chosen_data = {}
        data = history_data.get("data", [])
        for record in data:
            chosen_data[record[trade_date_index]] = record[value_index]

        return chosen_data