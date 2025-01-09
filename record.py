from datetime import date

class Record:
    _trade_date: date
    _price: float

    def __init__(self, trade_date: date, price: float = 0):
        self._trade_date = trade_date
        self._price = price

    def get_trade_date(self) -> date:
        return self._trade_date
    
    def get_price(self) -> float:
        return self._price