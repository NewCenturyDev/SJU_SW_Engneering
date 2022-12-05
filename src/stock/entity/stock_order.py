# The Stock Order Class
class StockOrder:
    # Data Fields
    _stock = None
    _order_type = "Unknown"
    _price = "시장가"
    _quantity = 0
    _timestamp = 0
    _tx_no = 0

    # Constructor
    def __init__(self, stock, order_type):
        self._stock = stock
        self._order_type = order_type
        self._quantity = stock.get_bid_unit()

    # Methods
    def get_order_detail_raw(self):
        return (
            self._stock.get_code(), self._stock.get_name(),
            self._order_type, self._price, self._quantity, self._timestamp, self._tx_no
        )

    def set_timestamp(self, timestamp):
        self._timestamp = timestamp

    def set_tx_no(self, tx_no):
        self._tx_no = tx_no
