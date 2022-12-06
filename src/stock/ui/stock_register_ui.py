import tkinter
import tkinter.messagebox

from src.common.ui_util import UIUtil, Position


class StockRegisterUI(tkinter.Toplevel):
    _parent = None
    _ui_util = None
    _stock_watch_serv = None

    # UI Fields
    stock_code_entry = None
    max_holdings_entry = None
    order_quantity_entry = None

    def __init__(self, parent_window, stock_watch_serv):
        super().__init__()
        self._parent = parent_window
        self._stock_watch_serv = stock_watch_serv
        self.setup()

    def setup(self):
        self.title("NewCentury Auto Trader")
        self._ui_util = UIUtil(self, 450, 200)
        self.geometry(self._ui_util.calc_geometry())
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.launch()

    def launch(self):
        title = self._ui_util.make_title("Add Stock")
        stock_code_lable = self._ui_util.make_label(
            "종목코드(Stock Code):", Position(20, 0, 250, 25),
            cst_x=None, cst_y=title
        )
        stock_code_lable.configure(anchor="w")
        self.stock_code_entry = self._ui_util.make_entry(
            "", Position(10, 0, 150, 25),
            cst_x=stock_code_lable, cst_y=title
        )
        max_holdings_label = self._ui_util.make_label(
            "최대 보유 주식수(Maximum Holdings):", Position(20, 0, 250, 25),
            cst_x=None, cst_y=self.stock_code_entry
        )
        max_holdings_label.configure(anchor="w")
        self.max_holdings_entry = self._ui_util.make_entry(
            "", Position(10, 0, 150, 25),
            cst_x=max_holdings_label, cst_y=self.stock_code_entry
        )

        order_quantity_label = self._ui_util.make_label(
            "1회 주문 수량(Quantity Per Order):", Position(20, 0, 250, 25),
            cst_x=None, cst_y=self.max_holdings_entry
        )
        order_quantity_label.configure(anchor="w")
        self.order_quantity_entry = self._ui_util.make_entry(
            "", Position(10, 0, 150, 25),
            cst_x=order_quantity_label, cst_y=self.max_holdings_entry
        )

        confirm_btn = self._ui_util.make_button(
            "감시대상 종목 추가(Append Watching Stock)", Position(20, 10, 275, 25),
            cst_x=None, cst_y=self.order_quantity_entry, onclick=self.confirm
        )
        self._ui_util.make_button(
            "취소(Cancel)", Position(10, 10, 125, 25),
            cst_x=confirm_btn, cst_y=self.order_quantity_entry, onclick=self.cancel
        )

    def confirm(self):
        if len(self.stock_code_entry.get()) == 0 or len(self.stock_code_entry.get()) > 6:
            tkinter.messagebox.showerror(
                "Error", "주식 코드는 6자리의 숫자(국내주식) 또는 1~6자의 영문알파벳(티커, 미국주식)이어야 합니다.\n"
                + "Stock code should be 6 digits number(korean stock market) or 1~6 alphabet characters(US market)"
            )
        elif not self.max_holdings_entry.get().isnumeric():
            tkinter.messagebox.showerror(
                "Error", "최대보유량은 0 또는 양수의 정수여야 합니다.\nMaximum Holdings should be 0 or positive integer"
            )
        elif not self.order_quantity_entry.get().isnumeric():
            tkinter.messagebox.showerror(
                "Error", "주문단위는 0 또는 양수의 정수여야 합니다.\nOrder Quantity should be 0 or positive integer"
            )
        else:
            self._stock_watch_serv.append_stock(
                self.stock_code_entry.get(), self.max_holdings_entry.get(), self.order_quantity_entry.get()
            )
            self._parent.refresh()
            self.destroy()

    def cancel(self):
        if tkinter.messagebox.askokcancel(
            "Warning", "창을 닫으면 작성하던 내용은 삭제됩니다.\n Your input will be deleted if you close window."
        ):
            self._parent.refresh()
            self.destroy()
