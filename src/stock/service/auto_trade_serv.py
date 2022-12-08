import time
import logging
import requests

from src.common.singleton import MetaSingleton
from src.login.credential_manager import CredentialManager
from src.stock.entity.stock_order import StockOrder


class AutoTradeServ(metaclass=MetaSingleton):
    _api = None
    _credential_manager = None
    _trade_list = []

    def __init__(self, api):
        self._api = api
        self._credential_manager = CredentialManager()

    def get_order_list(self):
        return self._trade_list

    def make_buy_order(self, stock):
        # 증권사에서는 제공하지만 pykis library에 없는 API 직접 호출
        new_order = StockOrder(stock, "매수(BUY)")
        tr_id = "TTTC0802U"
        if self._credential_manager.get_account_idx() == 0:
            tr_id = "VTTC0802U"
        self.collect_order_result(new_order, stock, tr_id)

    def make_sell_order(self, stock):
        # 증권사에서는 제공하지만 pykis library에 없는 API 직접 호출
        new_order = StockOrder(stock, "매도(SELL)")
        tr_id = "TTTC0801U"
        if self._credential_manager.get_account_idx() == 0:
            tr_id = "VTTC0801U"
        self.collect_order_result(new_order, stock, tr_id)

    def collect_order_result(self, new_order, stock, tr_id):
        key_info = self._credential_manager.get_key_info()
        account_info = self._credential_manager.get_account_info()
        try:
            order_result = requests.post(
                url=self._api.domain.get_url("/uapi/domestic-stock/v1/trading/order-cash"),
                headers={
                    "content-type": "application/json; charset=utf-8",
                    "authorization": self._api.token.value,
                    "appkey": key_info["appkey"],
                    "appsecret": key_info["appsecret"],
                    "tr_id": tr_id
                }, json={
                    "CANO": account_info["account_code"],
                    "ACNT_PRDT_CD": account_info["product_code"],
                    "PDNO": stock.get_code(),
                    "ORD_DVSN": "01",
                    "ORD_QTY": str(stock.get_order_quantity()),
                    "ORD_UNPR": "0",
                }
            )
            if order_result.json()["rt_cd"] == "0":
                new_order.set_timestamp(order_result.json()["output"]["ORD_TMD"])
                new_order.set_tx_no(order_result.json()["output"]["ODNO"])
            else:
                new_order.set_timestamp(time.strftime("%HH%MM%SS"))
                new_order.set_tx_no("에러(ERROR): " + order_result.json()["msg1"])
                self._trade_list.append(new_order)

            self._trade_list.append(new_order)
        except Exception as err:
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            logger.error(str(err), exc_info=True)
            new_order.set_timestamp(time.strftime("%HH%MM%SS"))
            new_order.set_tx_no("에러(ERROR): Network Error")
            self._trade_list.append(new_order)
