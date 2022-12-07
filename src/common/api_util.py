import tkinter
import tkinter.messagebox
import logging


class APIUtil:
    @staticmethod
    def call_api(window, method, on_success, on_fail=None, silent=False):
        try:
            if type(method) == "dict":
                result = method
                on_success(result)
            else:
                result = method()
                on_success(result)
        except RuntimeError as err:
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            logger.error(str(err), exc_info=True)
            if not silent:
                tkinter.messagebox.showerror("API Error", str(err), parent=window)
            if on_fail is not None:
                on_fail(err)
        except Exception as err:
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            logger.error(str(err), exc_info=True)
            if on_fail is not None:
                on_fail(err)
            if not silent:
                tkinter.messagebox.showerror("API Error", "Unknown Error", parent=window)
