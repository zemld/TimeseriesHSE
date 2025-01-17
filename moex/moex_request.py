from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class MoexRequest:
    _ticket: str
    _from_date: date
    _till_date: date
    _RECORDS_PER_REQUEST: int = 100

    def __init__(
        self,
        ticker: str,
        from_date: date = datetime.today() - relativedelta(years=3),
        till_date: date = datetime.today() - relativedelta(days=1),
    ):
        self._ticket = ticker
        self._from_date = from_date
        self._till_date = till_date

    def get_start_date(self) -> date:
        return self._from_date

    def get_end_date(self) -> date:
        return self._till_date

    def get_ticker(self) -> str:
        return self._ticket

    def date_to_string(self, date: date) -> str:
        return f"{date.year}-{date.month}-{date.day}"

    def get_request_urls(self):
        start_date: date = self._from_date
        urls = []
        while start_date < self._till_date:
            url = (
                self._ticket
                + ".json"
                + "?from="
                + self.date_to_string(start_date)
                + "&till="
                + self.date_to_string(self._till_date)
                + "&iss.meta=off"
            )
            urls.append(url)
            start_date += relativedelta(days=self._RECORDS_PER_REQUEST)
        return urls


class MoexActionRequest(MoexRequest):
    _action_request: str = (
        "https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/"
    )

    def get_request_urls(self):
        urls = super().get_request_urls()
        for i in range(len(urls)):
            urls[i] = self._action_request + urls[i]

        return urls


class MoexBondRequest(MoexRequest):
    _bond_request: str = (
        "https://iss.moex.com/iss/history/engines/bonds/markets/shares/boards/TQBR/securities/"
    )

    def get_request_urls(self):
        urls = super().get_request_urls()
        for i in range(len(urls)):
            urls[i] = self._bond_request + urls[i]

        return urls


class MoexCurrencyRequest(MoexRequest):
    _currency_request: str = (
        "https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/CETS/securities/"
    )

    def get_request_urls(self):
        urls = super().get_request_urls()
        for i in range(len(urls)):
            urls[i] = self._currency_request + urls[i]

        return urls
