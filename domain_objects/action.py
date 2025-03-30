from datetime import date


class Action:
    date_value: date
    close: float
    open_value: float
    low: float
    high: float
    trendclspr: float
    volume: int
    value: float
    numtrades: int

    def __init__(
        self,
        date_value: date,
        close: float,
        open_value: float,
        low: float,
        high: float,
        trendclspr: float,
        volume: int,
        value: float,
        numtrades: int,
    ):
        self.date_value = date_value
        self.close = close
        self.open_value = open_value
        self.low = low
        self.high = high
        self.trendclspr = trendclspr
        self.volume = volume
        self.value = value
        self.numtrades = numtrades
