from src.stock.entity.stock_candle import StockCandle
from src.trader.service.auto_trade_serv import AutoTradeServ


class StockDetail:
    _auto_trader = None

    _code = None
    _market = "Unknown"
    _category = "Unknown"
    _name = "Unknown"
    _price = 0
    _volume = 0
    _bid_unit = 0

    _max_holdings = 0
    _order_quantity = 1

    _last_tx_update_timestamp = None
    _market_transactions = []
    _incoming_transactions = []
    # 1번봉이 제일 오래된 봉, 4번 봉이 제일 최근 봉
    _candle_1 = None
    _candle_2 = None
    _candle_3 = None
    _candle_4 = None
    _lastest_highest_price = None
    _lastest_lowest_price = None

    def __init__(self, code, max_holdings, order_quantity, api):
        self._auto_trader = AutoTradeServ(api)
        self._code = code
        self._max_holdings = max_holdings
        self._order_quantity = order_quantity

    def get_code(self):
        return self._code

    def get_market(self):
        return self._market

    def get_category(self):
        return self._category

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_price(self):
        return self._price

    def set_price(self, price):
        self._price = price

    def get_volume(self):
        return self._volume

    def get_bid_unit(self):
        return self._bid_unit

    def set_advance_details(self, market, category, price, volume, bid_unit):
        self._market = market
        self._category = category
        self._price = price
        self._volume = volume
        self._bid_unit = bid_unit

    def get_max_holdings(self):
        return self._max_holdings

    def set_max_holdings(self, max_holdings):
        self._max_holdings = max_holdings

    def get_order_quantity(self):
        return self._order_quantity

    def set_order_quantity(self, quantity):
        self._order_quantity = quantity

    def get_last_tx_update_timestamp(self):
        return self._last_tx_update_timestamp

    def set_last_tx_update_timestamp(self, timestamp):
        self._last_tx_update_timestamp = timestamp

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

    def get_lastest_lowest_price(self):
        return self._lastest_lowest_price

    def append_market_transactions(self, new_txs):
        self._incoming_transactions.extend(new_txs)
        # 20개 거래내역을 모아서 20틱 봉 1개 만들고 밀어내기
        while len(self._incoming_transactions) >= 20:
            tx_for_new_candle = self._incoming_transactions[-20:]
            self._candle_1 = self._candle_2
            self._candle_2 = self._candle_3
            self._candle_3 = self._candle_4
            self._candle_4 = StockCandle(tx_for_new_candle)
            self._determine_turning_point()
            self._incoming_transactions = self._incoming_transactions[0:-20]
        self._market_transactions.extend(new_txs)

    def update_market_status(self, market, category, price, volumn, bid_unit):
        self._market = market
        self._category = category
        self._price = price
        self._volume = volumn
        self._bid_unit = bid_unit

    # 시세 반전 여부 확인
    def _determine_turning_point(self):
        if self._candle_3 is None or self._candle_4 is None:
            return
        if self._candle_4.difference > 0 and self._candle_3.difference < 0:
            # 하락하다 상승반전
            self._candle_4.is_reversal = True
            self._update_invest_params(True)
        elif self._candle_4.difference < 0 and self._candle_3.difference > 0:
            # 상승하다 하락반전
            self._candle_4.is_reversal = True
            self._update_invest_params(False)
        else:
            self._candle_4.is_reversal = False

    # 투자지표 갱신 (새로운 봉이 만들어질 때마다)
    def _update_invest_params(self, is_lowest_point):
        if is_lowest_point:
            if self._candle_3.lowest_price < self._candle_4.lowest_price:
                # 3번봉 최저가가 저점인 경우
                self._lastest_lowest_price = self._candle_3.lowest_price
            else:
                # 4번봉 최저가가 저점인 경우
                self._lastest_lowest_price = self._candle_4.lowest_price
        else:
            if self._candle_3.highest_price > self._candle_4.highest_price:
                # 3번봉 최저가가 고점인 경우
                self._lastest_highest_price = self._candle_3.highest_price
            else:
                # 4번봉 최저가가 고점인 경우
                self._lastest_highest_price = self._candle_4.highest_price
