import tkinter
import tkinter.messagebox


class APIUtil:
    @staticmethod
    def call_api(window, method, on_success, on_fail=None):
        try:
            result = method()
            on_success(result)
        except RuntimeError as err:
            print(err)
            tkinter.messagebox.showerror("API Error", str(err), parent=window)
            if on_fail is not None:
                on_fail(err)
        except Exception:
            tkinter.messagebox.showerror("API Error", "Unknown Error", parent=window)
