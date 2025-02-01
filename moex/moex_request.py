from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from logger import Logger

class MoexRequestAttributes:
    _category: str
    _ticket: str
    _from_date: date
    _till_date: date
    _RECORDS_PER_REQUEST: int = 100
    _logger: Logger

    def __init__(
        self,
        category: str,
        ticker: str,
        from_date: date = datetime.today() - relativedelta(years=3),
        till_date: date = datetime.today() - relativedelta(days=1),
    ):
        self._category = category
        self._ticket = ticker
        self._from_date = from_date
        self._till_date = till_date
        self._logger = Logger("moex_attributes")

    def get_category(self) -> str:
        return self._category

    def get_start_date(self) -> date:
        return self._from_date

    def get_end_date(self) -> date:
        return self._till_date

    def get_ticker(self) -> str:
        return self._ticket

    def date_to_string(self, date: date) -> str:
        return f"{date.year}-{date.month}-{date.day}"

    def get_url_body(self) -> str:
        category: str = self.get_category()
        return f"https://iss.moex.com/iss/history/engines/{category}/markets/shares/boards/{"CETS" if category == "currency" else "TQBR"}/securities/"

    def get_request_urls(self):
        url_body = self.get_url_body()
        start_date: date = self._from_date
        urls = []
        while start_date < self._till_date:
            url = (
                url_body
                + self._ticket
                + ".json"
                + "?from="
                + self.date_to_string(start_date)
                + "&till="
                + self.date_to_string(self._till_date)
                + "&iss.meta=off"
            )
            urls.append(url)
            start_date += relativedelta(days=self._RECORDS_PER_REQUEST)
        self._logger.debug(f"Created {len(urls)} url(s) for request: {urls}")
        return urls
