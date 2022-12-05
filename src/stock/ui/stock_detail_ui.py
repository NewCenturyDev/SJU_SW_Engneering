import tkinter

from src.common.ui_util import UIUtil


class StockDetailUI(tkinter.Toplevel):
    parent = None
    ui_util = None
    api = None

    #UI Fields

    def __init__(self, parent_window, api):
        super().__init__()
        self.parent = parent_window
        self.api = api
        self.setup()

    def setup(self):
        self.title("NewCentury Auto Trader")
        self.ui_util = UIUtil(self, 800, 600)
        self.geometry(self.ui_util.calc_geometry())
        self.resizable(False, False)
        self.launch()

    def launch(self):
        title = self.ui_util.make_title("Stock Detail")
