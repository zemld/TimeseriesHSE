from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class MOEXRequestAttributes:
    _ticket: str
    _from_date: date
    _till_date: date


    def __init__(self, ticket: str, from_date=datetime.today() - relativedelta(years=3), till_date=datetime.today()):
        self._ticket = ticket
        self._from_date = from_date
        self._till_date = till_date

    
    def _get_start_date(self) -> date:
        return self._from_date


    def _get_end_date(self) -> date:
        return self._till_date


    def get_ticket(self) -> str:
        return self._ticket
    

    def get_date_as_string(self, is_date_from=True) -> str:
        date_to_return: date
        if is_date_from:
            date_to_return = self._get_start_date()
        else:
            date_to_return = self._get_end_date()
        
        return f'{date_to_return.year}-{date_to_return.month}-{date_to_return.day}'