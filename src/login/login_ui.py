# Import External Packages
import tkinter

# Import Internal Packages
from src.common.ui_util import UIUtil, Position
from src.dashboard.dashboard_ui import DashboardUI

# Class for Login Window UI
from src.login.credential_manager import CredentialManager


class LoginUI(tkinter.Tk):
    # Utility and Libraries
    ui_util = None
    credential_manager = CredentialManager()

    # UI Fields
    account_select = None

    # Constructor
    def __init__(self):
        super().__init__()
        self.setup()

    # Methods
    def setup(self):
        self.title("NewCentury Auto Trade")
        self.ui_util = UIUtil(self, 400, 200)
        self.geometry(self.ui_util.calc_geometry())
        self.resizable(False, False)
        self.launch()

    def launch(self):
        title = self.ui_util.make_title("Welcome")
        account_select_label = self.ui_util.make_label(
            "Account Choice: ",
            Position(45, 0, 100, 25), cst_x=None, cst_y=title
        )
        self.account_select = self.ui_util.make_combo_box([
            "Test Account (모의투자)",
            "Real Account (실전투자)"
        ], Position(10, 0, 200, 25), cst_x=account_select_label, cst_y=title, readonly=True)
        self.ui_util.make_button(
            "Connect To Server", Position(45, 10, 310, 40),
            cst_x=None, cst_y=self.account_select,
            onclick=self.login
        )

    def login(self):
        self.credential_manager.load_credentials(self.account_select.current(), self.open_dashboard)

    def open_dashboard(self):
        DashboardUI(self, self.credential_manager).setup()
