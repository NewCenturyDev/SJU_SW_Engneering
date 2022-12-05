import tkinter
import tkinter.messagebox


class APIUtil:
    @staticmethod
    def call_api(window, method, on_success, on_fail=None, silent=False):
        try:
            result = method()
            on_success(result)
        except RuntimeError as err:
            print(err)
            if not silent:
                tkinter.messagebox.showerror("API Error", str(err), parent=window)
            if on_fail is not None:
                on_fail(err)
        except Exception:
            if not silent:
                tkinter.messagebox.showerror("API Error", "Unknown Error", parent=window)
