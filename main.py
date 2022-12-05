import tkinter
import logging

from src.login.login_ui import LoginUI

# 스크립트를 실행하려면 여백의 녹색 버튼을 누릅니다.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    LoginUI().setup()
    tkinter.mainloop()

# https://www.jetbrains.com/help/pycharm/에서 PyCharm 도움말 참조
