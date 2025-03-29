from datetime import datetime


class ElectricityRecord:
    timestamp: datetime
    price: float

    def __init__(self, timestamp: datetime, price: float):
        self.timestamp = timestamp
        self.price = price
