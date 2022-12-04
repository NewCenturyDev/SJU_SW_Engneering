# Import External Packages
import json
import os
import tkinter
import pykis

# Import Internal Packages
import file_config
from src.common.ui_util import UIUtil, Position
from src.dashboard.dashboard_ui import DashboardUI


# Class for Login Window UI
class LoginUI(tkinter.Tk):
    # Utility and Libraries
    ui_util = None

    # UI Fields
    account_select = None

    # Data Fields
    credentials_file = os.path.join(file_config.ROOT_DIR, "credential.json")
    credentails_info = None
    api = None

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
            cst_x=None, cst_y=self.account_select, onclick=self.load_credentials
        )

    def load_credentials(self):
        with open(self.credentials_file, 'r') as file:
            self.credentails_info = json.load(file)
            if self.account_select.current() == 0:
                self.api = pykis.Api(
                    domain_info=pykis.DomainInfo(kind="virtual"),
                    key_info=self.credentails_info["secret_test"],
                    account_info=self.credentails_info["account_test"]
                )
            else:
                self.api = pykis.Api(
                    key_info=self.credentails_info["secret"],
                    account_info=self.credentails_info["account"]
                )
            DashboardUI(self).setup()
