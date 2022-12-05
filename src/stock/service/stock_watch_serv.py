import asyncio
import requests
import time

from src.login.credential_manager import CredentialManager
from src.stock.entity.stock_detail import StockDetail
from src.stock.entity.stock_transaction import StockTransaction
from src.trader.service.auto_trade_serv import AutoTradeServ


class StockWatchServ:
    _instance = None
    _api = None
    _loop = None
    _task = None
    _auto_trader = None
    _credentail_manager = None
    _watching_list = []
    _exit_signal = False

    @classmethod
    def get_instance(cls, api):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._api = api
            cls._instance._auto_trader = AutoTradeServ().get_instance(api)
            cls._credentail_manager = CredentialManager().get_instance()
        return cls._instance

    def append_stock(self, code, max_holdings, order_quantity):
        new_stock = StockDetail(code, max_holdings, order_quantity, self._api)
        self._fetch_stock_detail(new_stock)

    def remove_stock(self, idx):
        self._watching_list.pop(idx)

    def get_watching_list(self):
        return self._watching_list

    def get_stock_detail(self, idx):
        return self._watching_list[idx]

    def _fetch_stock_detail(self, new_stock):
        # 증권사에서는 제공하지만 pykis library에 없는 API 직접 호출
        key_info = self._credentail_manager.get_key_info()
        try:
            basic_detail_res = requests.get(
                url="https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/search-info",
                headers={
                    "content-type": "application/json; charset=utf-8",
                    "authorization": self._api.token.value,
                    "appkey": key_info["appkey"],
                    "appsecret": key_info["appsecret"],
                    "tr_id": "CTPF1604R",
                    "custtype": "P"
                }, params={
                    "PDNO": new_stock.get_code(),
                    "PRDT_TYPE_CD": "300"  # 300 국내주식 / 512 미국 나스닥 / 513 미국 뉴욕 / 529 미국 아멕스
                }
            )
            new_stock.set_name(basic_detail_res.json()["output"]["prdt_name"])
            advance_detail_raw_res = requests.get(
                url=self._api.domain.get_url("/uapi/domestic-stock/v1/quotations/inquire-price"),
                headers={
                    "content-type": "application/json; charset=utf-8",
                    "authorization": self._api.token.value,
                    "appkey": key_info["appkey"],
                    "appsecret": key_info["appsecret"],
                    "tr_id": "FHKST01010100"
                }, params={
                    "FID_COND_MRKT_DIV_CODE": "J",
                    "FID_INPUT_ISCD": new_stock.get_code()
                }
            )
            advance_detail_res = advance_detail_raw_res.json()["output"]
            new_stock.set_advance_details(
                advance_detail_res["rprs_mrkt_kor_name"],
                advance_detail_res["bstp_kor_isnm"],
                advance_detail_res["stck_prpr"],
                advance_detail_res["acml_vol"],
                advance_detail_res["aspr_unit"]
            )
            self._watching_list.append(new_stock)
        except Exception as err:
            print(err)

    def start_watching(self):
        self._loop = asyncio.new_event_loop()
        self._loop.set_debug(True)
        self._task = self._loop.run_in_executor(None, self._looper)

    def stop_watching(self):
        self._exit_signal = True
        self._task.add_done_callback(self.shutdown_looper)

    def shutdown_looper(self):
        self._loop.close()
        self._loop = None

    # 시세 및 체결 감지 프로세스 코루틴 비동기 실행 (매 1초마다 주식 체결 현황 조회)
    def _looper(self):
        iter_cnt = 0
        while True:
            print("무한루프 가동 중 : " + str(iter_cnt) + "회차")
            iter_cnt += 1
            if self._exit_signal is True:
                self._exit_signal = False
                return
            for stock in self._watching_list:
                self._req_new_market_txs(stock)
                time.sleep(1)
            if len(self._watching_list) == 0:
                time.sleep(1)

    def _req_new_market_txs(self, stock):
        # 증권사에서는 제공하지만 pykis library에 없는 API 직접 호출
        key_info = self._credentail_manager.get_key_info()
        try:
            response = requests.get(
                url=self._api.domain.get_url("/uapi/domestic-stock/v1/quotations/inquire-ccnl"),
                headers={
                    "authorization": self._api.token.value,
                    "appkey": key_info["appkey"],
                    "appsecret": key_info["appsecret"],
                    "tr_id": "FHKST01010300",
                }, params={
                    "FID_COND_MRKT_DIV_CODE": "J",
                    "FID_INPUT_ISCD": stock.get_code()
                }
            )
            self._update_market_txs(response.json()["output"], stock)
        except Exception as err:
            print(err)

    def _update_market_txs(self, transactions, stock):
        new_tx_list = []
        last_tx_update_timestamp = stock.get_last_tx_update_timestamp()
        if int(transactions[0]["stck_cntg_hour"]) > int(last_tx_update_timestamp):
            self._check_immi_sell_condition(stock, transactions[0]["stck_prpr"])
            self._check_immi_buy_condition(stock, transactions[0]["stck_prpr"])
            for tx in transactions:
                tx_timestamp = tx["stck_cntg_hour"]
                tx_price = tx["stck_prpr"]
                tx_volume = tx["cntg_vol"]
                # 기존에 로드되지 않았던 데이터들만 추가
                if last_tx_update_timestamp is None or int(tx_timestamp) > int(last_tx_update_timestamp):
                    new_tx_list.append(StockTransaction(tx_timestamp, tx_price, tx_volume))
            stock.set_last_tx_update_timestamp(transactions[0]["stck_cntg_hour"])
            stock.append_market_transactions(new_tx_list)
            self._check_3_line_sell_condition(stock)
            self._check_3_line_buy_condition(stock)

    def _check_immi_sell_condition(self, stock, last_price):
        # 즉발 조건에 해당할 경우 시장가 매도
        if int(last_price) is None or int(stock.get_lastest_highest_price()) is None:
            return
        # 즉시 매도 조건: 현재가가 LHP(최근 고점)보다 5호가 넘게 떨어진 경우
        if int(last_price) < int(stock.get_lastest_highest_price()) - 5 * int(stock.get_bid_unit()):
            self._auto_trader.make_sell_order(stock)

    def _check_immi_buy_condition(self, stock, last_price):
        # 즉발 조건에 해당할 경우 시장가 매수
        if int(last_price) is None or int(stock.get_lastest_lowest_price()) is None:
            return
        # 즉시 매수 조건: 현재가가 LLP(최근 저점)보다 5호가 넘게 올라간 경우
        if int(last_price) > int(stock.get_lastest_lowest_price()) + 5 * int(stock.get_bid_unit()):
            self._auto_trader.make_buy_order(stock)

    def _check_3_line_sell_condition(self, stock):
        # 3봉 매도 타이밍에 해당하는지 확인 후 해당시 매도 수행
        if (
                stock.get_candle(1).difference > 0 and stock.get_candle(2).difference > 0
                and stock.get_candle(3).difference > 0 and stock.get_candle(4).difference < 0
                and stock.get_candle(4).end_price < stock.get_candle(1).start_price
        ):
            self._auto_trader.make_sell_order(stock)

    def _check_3_line_buy_condition(self, stock):
        # 3봉 매수 타이밍에 해당하는지 확인 후 해당시 매수 수행
        if (
                stock.get_candle(1).difference < 0 and stock.get_candle(2).difference < 0
                and stock.get_candle(3).difference < 0 and stock.get_candle(4).difference > 0
                and stock.get_candle(4).end_price > stock.get_candle(1).start_price
        ):
            self._auto_trader.make_buy_order(stock)
