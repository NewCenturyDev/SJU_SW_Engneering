import tkinter

from src.common.api_util import APIUtil
from src.common.ui_util import UIUtil, Position


class DashboardUI(tkinter.Toplevel):
    parent = None
    ui_util = None
    api = None

    def __init__(self, parent_window):
        super().__init__()
        self.parent = parent_window
        self.api = parent_window.api
        self.setup()

    def setup(self):
        self.title("NewCentury Auto Trade")
        self.ui_util = UIUtil(self, 1000, 800)
        self.geometry(self.ui_util.calc_geometry())
        self.resizable(False, False)
        self.launch()

    def launch(self):
        title = self.ui_util.make_title("Dashboard")
        cash_balance_label = self.ui_util.make_label("Cash Balance: ", Position(20, 20, 150, 25), None, title)
        cash_balance_value = self.ui_util.make_entry(
            "", Position(5, 20, 150, 25), cash_balance_label, title, True
        )

        def ok(result):
            cash_balance_value.configure(state="normal")
            cash_balance_value.delete(0, "end")
            cash_balance_value.insert(0, "\\" + format(result, ',') + "")
            cash_balance_value.configure(state="readonly")

        def fail(_):
            cash_balance_value.configure(state="normal")
            cash_balance_value.delete(0, "end")
            cash_balance_value.insert(0, "ERROR")
            cash_balance_value.configure(state="readonly")
        APIUtil.call_api(self, self.api.get_kr_buyable_cash, ok, fail)

        # def ok(result):
        #     print(result)
        # APIUtil.call_api(self, self.api.get_kr_stock_balance, ok)
