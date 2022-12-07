import tkinter
import tkinter.messagebox

from src.common.ui_util import UIUtil, Position
from src.stock.service.stock_watch_serv import StockWatchServ
from src.stock.ui.stock_detail_ui import StockDetailUI
from src.stock.ui.stock_register_ui import StockRegisterUI


class DashboardUI(tkinter.Tk):
    parent = None
    ui_util = None
    api = None
    stock_watch_serv = None
    task = None

    # UI Fields
    cash_balance_value = None
    today_real_profit_value = None
    watching_list_treeview = None
    stock_balance_treeview = None
    order_logs_treeview = None
    stop_trading_btn = None
    start_trading_btn = None

    def __init__(self, parent_window, api):
        super().__init__()
        self.parent = parent_window
        self.api = api
        self.stock_watch_serv = StockWatchServ(self.api)
        self.setup()

    def setup(self):
        self.title("NewCentury Auto Trader")
        self.ui_util = UIUtil(self, 1615, 850)
        self.geometry(self.ui_util.calc_geometry())
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.launch()
        self.refresh()

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

        today_real_profit_label = self.ui_util.make_label(
            "Today's Realized Profit (KRW): ",
            Position(20, 0, 200, 25),
            cst_x=self.cash_balance_value,
            cst_y=title
        )
        self.today_real_profit_value = self.ui_util.make_entry(
            "\\0", Position(5, 0, 150, 25), today_real_profit_label, title, True
        )

        self.start_trading_btn = self.ui_util.make_button(
            "투자시작(Start Trading)",
            Position(150, 0, 250, 25),
            cst_x=self.today_real_profit_value,
            cst_y=title,
            onclick=self.start_trading
        )
        self.stop_trading_btn = self.ui_util.make_button(
            "투자정지(Stop Trading)",
            Position(20, 0, 250, 25),
            cst_x=self.start_trading_btn,
            cst_y=title,
            status="disabled",
            onclick=self.stop_trading
        )
        self.ui_util.make_button(
            "즉시 새로고침(Refresh Now)",
            Position(20, 0, 200, 25),
            cst_x=self.stop_trading_btn,
            cst_y=title,
            onclick=self.refresh
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
            [50, 100, 150, 150, 125, 125, 73],
            Position(20, 5, 775, 300),
            cst_x=None,
            cst_y=watching_list_label
        )
        self.watching_list_treeview.bind("<Double-1>", self.open_stock_detail)

        add_stock_btn = self.ui_util.make_button(
            "감시종목 추가(Add Stock for Watching)",
            Position(20, 0, 225, 25),
            cst_x=None,
            cst_y=self.watching_list_treeview,
            onclick=self.open_add_stock_to_watch_list
        )
        self.ui_util.make_label(
            "감시 종목 정보의 편집과 제거는 목록에서 해당 종목을 더블 클릭하여 실행합니다.\n"
            + "Double click a stock from the list to remove from it or modify details",
            Position(10, 0, 490, 35),
            cst_x=add_stock_btn,
            cst_y=self.watching_list_treeview
        )

        stock_balance_label = self.ui_util.make_label(
            "현재주식잔고 (Current Stock Balance)",
            Position(20, 45, 775, 25),
            cst_x=None,
            cst_y=self.watching_list_treeview
        )
        self.stock_balance_treeview = self.ui_util.make_treeview(
            ["code", "name", "holdings", "price", "avr_bid_price", "bid_price", "eval_price", "profit_price"],
            ["종목ID", "종목명", "보유수량", "현재가", "평균매입가", "매입금액", "평가금액", "평가손익금액"],
            [50, 150, 75, 100, 100, 100, 100, 98],
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
            ["code", "name", "type", "price", "quantity", "timestamp", "tx_no"],
            ["종목ID", "종목명", "매수/매도", "주문단가", "주문수량", "주문시각", "주문번호"],
            [50, 150, 75, 125, 75, 175, 123],
            Position(20, 5, 775, 675),
            cst_x=self.watching_list_treeview,
            cst_y=order_logs_label
        )

    def reload_current_cash_balance(self):
        try:
            self.cash_balance_value.configure(state="normal")
            self.cash_balance_value.delete(0, "end")
            self.cash_balance_value.insert(
                0, "\\" + format(self.stock_watch_serv.get_balance_serv().fetch_cash_balance(), ',')
            )
            self.cash_balance_value.configure(state="readonly")
        except Exception:
            self.cash_balance_value.configure(state="normal")
            self.cash_balance_value.delete(0, "end")
            self.cash_balance_value.insert(0, "ERROR")
            self.cash_balance_value.configure(state="readonly")

    def reload_today_profit_realize(self):
        realied_profit_total = 0
        for row in self.stock_balance_treeview.get_children():
            if (
                    self.stock_balance_treeview.item(row)["evlu_pfls_amt"] is not None
                    and self.stock_balance_treeview.item(row)["evlu_pfls_amt"].isnumeric()
            ):
                realied_profit_total += int(self.stock_balance_treeview.item(row)["evlu_pfls_amt"])
        self.today_real_profit_value.configure(state="normal")
        self.cash_balance_value.delete(0, "end")
        self.cash_balance_value.insert(0, "\\" + format(realied_profit_total, ','))
        self.today_real_profit_value.configure(state="readonly")

    def reload_watching_stock_treeview(self):
        for child in self.watching_list_treeview.get_children():
            self.watching_list_treeview.delete(child)
        for stock in self.stock_watch_serv.get_watching_list():
            self.watching_list_treeview.insert("", "end", values=(
                stock.get_code(), stock.get_market(), stock.get_category(), stock.get_name(),
                stock.get_price(), stock.get_volume(), stock.get_bid_unit()
            ))

    def reload_stock_balance_treeview(self):
        stock_balance_service = self.stock_watch_serv.get_balance_serv()
        for child in self.stock_balance_treeview.get_children():
            self.stock_balance_treeview.delete(child)
        for balance_row in stock_balance_service.fetch_stock_balance():
            self.stock_balance_treeview.insert("", "end", values=balance_row)

    def reload_order_logs_treeview(self):
        auto_trader = self.stock_watch_serv.get_auto_trader()
        for child in self.order_logs_treeview.get_children():
            self.order_logs_treeview.delete(child)
        for order in auto_trader.get_order_list():
            self.order_logs_treeview.insert("", "end", values=order.get_order_detail_row())

    def open_add_stock_to_watch_list(self):
        if self.stock_watch_serv.get_task() is not None and not self.stock_watch_serv.get_task().done():
            tkinter.messagebox.showerror(
                "Error", "투자 종목을 변경하기 전에 먼저 자동 투자를 정지 하십시오\n"
                + "Stop auto trading before to change watching stocks"
            )
        else:
            StockRegisterUI(self, self.stock_watch_serv).setup()

    def open_stock_detail(self, _):
        StockDetailUI(
            self, self.stock_watch_serv,
            self.watching_list_treeview.index(self.watching_list_treeview.selection()[0])
        ).setup()

    def start_trading(self):
        self.start_trading_btn.config(state="disabled")
        self.stop_trading_btn.config(state="normal")
        self.stock_watch_serv.start_watching()

    def stop_trading(self):
        self.stop_trading_btn.config(state="disabled")
        self.start_trading_btn.config(state="normal")
        self.stock_watch_serv.stop_watching()

    def refresh(self, auto_refresh=True):
        self.reload_current_cash_balance()
        self.reload_today_profit_realize()
        self.reload_watching_stock_treeview()
        self.reload_stock_balance_treeview()
        self.reload_order_logs_treeview()
        if auto_refresh:
            self.task = self.after(5000, self.refresh)

    def close(self):
        # 루프가 실행 중인 경우 강제 중지
        self.after_cancel(self.task)
        if self.stock_watch_serv.get_task() is not None and not self.stock_watch_serv.get_task().done():
            self.stock_watch_serv.stop_watching()
        self.destroy()
        self.parent.deiconify()
