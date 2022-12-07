import tkinter
import tkinter.messagebox

from src.common.ui_util import UIUtil, Position


class StockDetailUI(tkinter.Toplevel):
    _parent = None
    _ui_util = None
    _stock_watch_serv = None
    _task = None
    _stock = None
    _idx = None

    # UI Fields
    _stock_code_entry = None
    _stock_name_entry = None
    _max_holdings_entry = None
    _order_quantity_entry = None
    _market_tx_log_treeview = None
    _modify_btn = None

    def __init__(self, parent_window, stock_watch_serv, idx):
        super().__init__()
        self._parent = parent_window
        self._stock_watch_serv = stock_watch_serv
        self._idx = idx
        self.setup()

    def setup(self):
        self.title("NewCentury Auto Trader")
        self._ui_util = UIUtil(self, 450, 800)
        self.geometry(self._ui_util.calc_geometry())
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self._stock = self._stock_watch_serv.get_stock_detail(self._idx)
        if self._stock is None:
            tkinter.messagebox.showerror("Error", "종목 정보 불러오기 실패\nStock Info Fetch Failure")
            self.destroy()
        self.launch()
        self.reload_market_tx_log_treeview()

    def launch(self):
        title = self._ui_util.make_title("Stock Detail")
        stock_code_lable = self._ui_util.make_label(
            "종목코드(Stock Code):", Position(20, 0, 250, 25),
            cst_x=None, cst_y=title
        )
        stock_code_lable.configure(anchor="w")
        self._stock_code_entry = self._ui_util.make_entry(
            self._stock.get_code(), Position(10, 0, 150, 25),
            cst_x=stock_code_lable, cst_y=title, readonly=True
        )
        stock_name_lable = self._ui_util.make_label(
            "종목명(Stock Name):", Position(20, 0, 250, 25),
            cst_x=None, cst_y=self._stock_code_entry
        )
        stock_name_lable.configure(anchor="w")
        self._stock_name_entry = self._ui_util.make_entry(
            self._stock.get_name(), Position(10, 0, 150, 25),
            cst_x=stock_name_lable, cst_y=self._stock_code_entry, readonly=True
        )
        max_holdings_label = self._ui_util.make_label(
            "최대 보유 주식수(Maximum Holdings):", Position(20, 0, 250, 25),
            cst_x=None, cst_y=self._stock_name_entry
        )
        max_holdings_label.configure(anchor="w")
        self._max_holdings_entry = self._ui_util.make_entry(
            str(self._stock.get_max_holdings()), Position(10, 0, 150, 25),
            cst_x=max_holdings_label, cst_y=self._stock_name_entry, readonly=True
        )
        order_quantity_label = self._ui_util.make_label(
            "1회 주문 수량(Quantity Per Order):", Position(20, 0, 250, 25),
            cst_x=None, cst_y=self._max_holdings_entry
        )
        order_quantity_label.configure(anchor="w")
        self._order_quantity_entry = self._ui_util.make_entry(
            str(self._stock.get_order_quantity()), Position(10, 0, 150, 25),
            cst_x=order_quantity_label, cst_y=self._max_holdings_entry, readonly=True
        )

        tx_log_treeview_label = self._ui_util.make_label(
            "시장 거래체결 내역 (Market Transaction Logs)",
            Position(20, 0, 410, 25),
            cst_x=None,
            cst_y=self._order_quantity_entry
        )
        self._market_tx_log_treeview = self._ui_util.make_treeview(
            ["timestamp", "price", "volume"],
            ["시간(Time)", "체결가격(Price)", "체결거래량(Volume)"],
            [160, 125, 123],
            Position(20, 0, 410, 500),
            cst_x=None,
            cst_y=tx_log_treeview_label
        )

        self._modify_btn = self._ui_util.make_button(
            "종목 정보 수정(Modify Stock Detail)", Position(20, 5, 410, 25),
            cst_x=None, cst_y=self._market_tx_log_treeview, onclick=self.modify_mode
        )
        remove_btn = self._ui_util.make_button(
            "종목 감시 해제(Remove Watching Stock)", Position(20, 5, 410, 25),
            cst_x=None, cst_y=self._modify_btn, onclick=self.remove_stock
        )
        self._ui_util.make_button(
            "닫기(Close)", Position(20, 5, 410, 25),
            cst_x=None, cst_y=remove_btn, onclick=self.close
        )

    def reload_market_tx_log_treeview(self):
        for child in self._market_tx_log_treeview.get_children():
            self._market_tx_log_treeview.delete(child)
        for tx in self._stock.get_market_transactions():
            self._market_tx_log_treeview.insert("", "end", values=(
                tx.get_time(),
                tx.get_price(),
                tx.get_volume()
            ))
        self._task = self.after(5000, self.reload_market_tx_log_treeview)

    def modify_mode(self):
        if self._stock_watch_serv.get_task() is not None and not self._stock_watch_serv.get_task().done():
            tkinter.messagebox.showerror(
                "Error", "투자 종목을 변경하기 전에 먼저 자동 투자를 정지 하십시오\n"
                         + "Stop auto trading before to change watching stocks"
            )
        else:
            self._modify_btn.destroy()
            self._modify_btn = self._ui_util.make_button(
                "변경사항 저장(Save Modifications)", Position(20, 5, 410, 25),
                cst_x=None, cst_y=self._market_tx_log_treeview, onclick=self.modify_stock
            )
            self._max_holdings_entry.configure(state="normal")
            self._order_quantity_entry.configure(state="normal")

    def modify_stock(self):
        stock = self._stock_watch_serv.get_stock_detail(self._idx)
        stock.set_max_holdings(int(self._max_holdings_entry.get()))
        stock.set_order_quantity(int(self._order_quantity_entry.get()))
        self._modify_btn.destroy()
        self._modify_btn = self._ui_util.make_button(
            "종목 정보 수정(Modify Stock Detail)", Position(20, 5, 410, 25),
            cst_x=None, cst_y=self._market_tx_log_treeview, onclick=self.modify_mode
        )
        self._max_holdings_entry.configure(state="readonly")
        self._order_quantity_entry.configure(state="readonly")

    def remove_stock(self):
        if self._stock_watch_serv.get_task() is not None and not self._stock_watch_serv.get_task().done():
            tkinter.messagebox.showerror(
                "Error", "투자 종목을 변경하기 전에 먼저 자동 투자를 정지 하십시오\n"
                         + "Stop auto trading before to change watching stocks"
            )
        else:
            self._stock_watch_serv.remove_stock(self._idx)
            self._parent.refresh()
            self.destroy()

    def close(self):
        self.after_cancel(self._task)
        self.destroy()
