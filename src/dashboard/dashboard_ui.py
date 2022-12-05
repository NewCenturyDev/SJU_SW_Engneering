import tkinter

from src.common.api_util import APIUtil
from src.common.ui_util import UIUtil, Position


class DashboardUI(tkinter.Toplevel):
    parent = None
    ui_util = None
    api = None

    # UI Fields
    cash_balance_value = None
    today_real_profit_value = None
    watching_list_treeview = None
    stock_balance_treeview = None
    order_logs_treeview = None

    def __init__(self, parent_window, cred_manager):
        super().__init__()
        self.parent = parent_window
        self.api = cred_manager.get_api()
        self.setup()

    def setup(self):
        self.title("NewCentury Auto Trade")
        self.ui_util = UIUtil(self, 1615, 850)
        self.geometry(self.ui_util.calc_geometry())
        self.resizable(False, False)
        self.launch()

    def launch(self):
        title = self.ui_util.make_title("Dashboard")

        cash_balance_label = self.ui_util.make_label(
            "Cash Balance (KRW): ",
            Position(20, 0, 150, 25),
            cst_x=None,
            cst_y=title
        )
        self.cash_balance_value = self.ui_util.make_entry(
            "", Position(5, 0, 150, 25), cash_balance_label, title, True
        )
        APIUtil.call_api(self, self.api.get_kr_buyable_cash, self.fetch_cash_balance_ok, self.fetch_cash_balance_err)

        today_real_profit_label = self.ui_util.make_label(
            "Today's Realized Profit (KRW): ",
            Position(20, 0, 200, 25),
            cst_x=self.cash_balance_value,
            cst_y=title
        )
        self.today_real_profit_value = self.ui_util.make_entry(
            "", Position(5, 0, 150, 25), today_real_profit_label, title, True
        )

        start_trading_btn = self.ui_util.make_button(
            "투자시작(Start Trading)",
            Position(150, 0, 250, 25),
            cst_x=self.today_real_profit_value,
            cst_y=title
        )
        stop_trading_btn = self.ui_util.make_button(
            "투자정지(Stop Trading)",
            Position(20, 0, 250, 25),
            cst_x=start_trading_btn,
            cst_y=title
        )
        self.ui_util.make_button(
            "설정(Settings)",
            Position(20, 0, 200, 25),
            cst_x=stop_trading_btn,
            cst_y=title
        )

        watching_list_label = self.ui_util.make_label(
            "감시종목 (Watching Stocks)",
            Position(20, 20, 775, 25),
            cst_x=None,
            cst_y=cash_balance_label
        )
        self.watching_list_treeview = self.ui_util.make_treeview(
            ["code", "market", "category", "name", "price", "volume", "unit"],
            ["종목ID", "시장", "업종/테마", "종목명", "현재가", "거래량", "호가단위"],
            [50, 100, 100, 150, 125, 150, 98],
            Position(20, 5, 775, 300),
            cst_x=None,
            cst_y=watching_list_label
        )

        stock_balance_label = self.ui_util.make_label(
            "현재주식잔고 (Current Stock Balance)",
            Position(20, 45, 775, 25),
            cst_x=None,
            cst_y=self.watching_list_treeview
        )
        self.stock_balance_treeview = self.ui_util.make_treeview(
            ["code", "name", "holdings", "price", "avr_bid_price", "bid_price", "eval_price"],
            ["종목ID", "종목명", "보유수량", "현재가", "평균매입가", "매입금액", "평가금액"],
            [50, 150, 75, 125, 125, 125, 123],
            Position(20, 5, 775, 300),
            cst_x=None,
            cst_y=stock_balance_label
        )

        order_logs_label = self.ui_util.make_label(
            "자동주문내역 (Automated Order Logs)",
            Position(20, 20, 775, 25),
            cst_x=self.watching_list_treeview,
            cst_y=cash_balance_label
        )
        self.order_logs_treeview = self.ui_util.make_treeview(
            ["code", "name", "type", "price", "quntity", "timestamp", "tx_no"],
            ["종목ID", "종목명", "매수/매도", "주문단가", "주문수량", "주문시각", "주문번호"],
            [50, 150, 75, 125, 75, 175, 123],
            Position(20, 5, 775, 675),
            cst_x=self.watching_list_treeview,
            cst_y=order_logs_label
        )

    def fetch_cash_balance_ok(self, result):
        self.cash_balance_value.configure(state="normal")
        self.cash_balance_value.delete(0, "end")
        self.cash_balance_value.insert(0, "\\" + format(result, ',') + "")
        self.cash_balance_value.configure(state="readonly")

    def fetch_cash_balance_err(self, _):
        self.cash_balance_value.configure(state="normal")
        self.cash_balance_value.delete(0, "end")
        self.cash_balance_value.insert(0, "ERROR")
        self.cash_balance_value.configure(state="readonly")
