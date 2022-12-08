from src.stock.entity.stock_candle import StockCandle
from src.stock.service.auto_trade_serv import AutoTradeServ


class StockDetail:
    def __init__(self, code, max_holdings, order_quantity, api):
        self._code = code
        self._market = "Unknown"
        self._category = "Unknown"
        self._name = "Unknown"
        self._price = 0
        self._volume = 0
        self._bid_unit = 0

        self._max_holdings = max_holdings
        self._order_quantity = order_quantity

        self._last_tx_update_timestamp = None
        self._market_transactions = []
        self._incoming_transactions = []

        # 1번봉이 제일 오래된 봉, 4번 봉이 제일 최근 봉
        self._candle_1 = None
        self._candle_2 = None
        self._candle_3 = None
        self._candle_4 = None
        self._lastest_highest_price = None
        self._lastest_lowest_price = None
        self._is_new_lhp = False
        self._is_new_llp = False

    def get_code(self):
        return self._code

    def get_market(self):
        return self._market

    def get_category(self):
        return self._category

    def get_name(self):
        return self._name

    def get_price(self):
        return self._price

    def get_volume(self):
        return self._volume

    def get_bid_unit(self):
        return self._bid_unit

    def get_max_holdings(self):
        return self._max_holdings

    def set_price(self, price):
        self._price = price

    def get_order_quantity(self):
        return self._order_quantity

    def get_last_tx_update_timestamp(self):
        return self._last_tx_update_timestamp

    def get_market_transactions(self):
        return self._market_transactions

    def get_candle(self, idx):
        if idx == 1:
            return self._candle_1
        if idx == 2:
            return self._candle_2
        if idx == 3:
            return self._candle_3
        if idx == 4:
            return self._candle_4

    def get_lastest_highest_price(self):
        return self._lastest_highest_price

    def is_new_lhp(self):
        return self._is_new_lhp

    def get_lastest_lowest_price(self):
        return self._lastest_lowest_price

    def is_new_llp(self):
        return self._is_new_llp

    def set_name(self, name):
        self._name = name

    def set_advance_details(self, market, category, price, volume, bid_unit):
        self._market = market
        self._category = category
        self._price = price
        self._volume = volume
        self._bid_unit = bid_unit

    def set_max_holdings(self, max_holdings):
        self._max_holdings = max_holdings

    def set_order_quantity(self, quantity):
        self._order_quantity = quantity

    def set_last_tx_update_timestamp(self, timestamp):
        self._last_tx_update_timestamp = timestamp

    def llp_outdated(self):
        self._is_new_llp = False

    def lhp_outdated(self):
        self._is_new_lhp = False

    def append_market_transactions(self, new_txs):
        self._incoming_transactions = new_txs + self._incoming_transactions
        # 20개 거래내역을 모아서 15틱 봉 1개 만들고 밀어내기
        while len(self._incoming_transactions) >= 30:
            tx_for_new_candle = self._incoming_transactions[-30:]
            self._candle_1 = self._candle_2
            self._candle_2 = self._candle_3
            self._candle_3 = self._candle_4
            self._candle_4 = StockCandle(tx_for_new_candle)
            self._determine_turning_point()
            self._incoming_transactions = self._incoming_transactions[0:-30]
        self._market_transactions = new_txs + self._market_transactions

    # 시세 반전 여부 확인
    def _determine_turning_point(self):
        if self._candle_3 is None or self._candle_4 is None:
            return
        if self._candle_4.difference > 0 and self._candle_3.difference <= 0:
            # 하락하다 상승반전
            self._candle_4.is_reversal = True
            self._update_invest_params(True)
        elif self._candle_4.difference < 0 and self._candle_3.difference >= 0:
            # 상승하다 하락반전
            self._candle_4.is_reversal = True
            self._update_invest_params(False)
        else:
            self._candle_4.is_reversal = False

    # 투자지표 갱신 (새로운 봉이 만들어질 때마다)
    def _update_invest_params(self, is_lowest_point):
        if is_lowest_point:
            self._is_new_llp = True
            if self._candle_3.lowest_price < self._candle_4.lowest_price:
                # 3번봉 최저가가 저점인 경우
                self._lastest_lowest_price = self._candle_3.lowest_price
            else:
                # 4번봉 최저가가 저점인 경우
                self._lastest_lowest_price = self._candle_4.lowest_price
        else:
            self._is_new_lhp = True
            if self._candle_3.highest_price > self._candle_4.highest_price:
                # 3번봉 최저가가 고점인 경우
                self._lastest_highest_price = self._candle_3.highest_price
            else:
                # 4번봉 최저가가 고점인 경우
                self._lastest_highest_price = self._candle_4.highest_price
