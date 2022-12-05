# The Stock Transaction Class
class StockTransaction:
    # Data Fields
    _time = "Unknown"
    _price = 0
    _volume = 0

    # Constructor
    def __init__(self, time, price, volume):
        self._time = time
        self._price = price
        self._volume = volume

    # Methods
    def get_time(self):
        return self._time

    def get_price(self):
        return self._price

    def get_volumn(self):
        return self._volume
