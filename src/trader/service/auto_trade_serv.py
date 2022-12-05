import time

from src.common.api_util import APIUtil
from src.stock.entity.stock_order import StockOrder


class AutoTradeServ:
    _instance = None
    _api = None
    _trade_list = []

    @classmethod
    def get_instance(cls, api):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._api = api
        return cls._instance

    def make_buy_order(self, stock):
        new_order = StockOrder(stock, "매수(BUY)")
        APIUtil().call_api(
            self, self._api.buy_kr_stock(stock.get_code(), stock.get_bid_unit(), 0),
            self.order_ok(new_order), self.order_err(new_order), True
        )

    def make_sell_order(self, stock):
        new_order = StockOrder(stock, "매도(SELL)")
        APIUtil().call_api(
            self, self._api.buy_kr_stock(stock.get_code(), stock.get_bid_unit(), 0),
            self.order_ok(new_order), self.order_err(new_order), True
        )

    def order_ok(self, order):
        def callback(res):
            order.set_timestamp(res["ORD_TMD"])
            order.set_tx_no(res["ODNO"])
            self._trade_list.append(order)
        return callback

    def order_err(self, order):
        def callback():
            order.set_timestamp(time.strftime("%HH%MM%SS"))
            order.set_tx_no("에러(ERROR)")
            self._trade_list.append(order)
        return callback
