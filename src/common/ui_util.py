import tkinter
import tkinter.ttk


class UIUtil:
    window = None
    win_width = 1000
    win_height = 500

    def __init__(self, window, width, height):
        self.window = window
        self.win_width = width
        self.win_height = height

    def calc_geometry(self):
        return str(self.win_width) + "x" + str(self.win_height) + "+" \
               + str(self.calc_screen_x_pos()) + "+" + str(self.calc_screen_y_pos())

    def calc_screen_x_pos(self):
        return int(self.window.winfo_screenwidth() / 2 - self.win_width / 2)

    def calc_screen_y_pos(self):
        return int(self.window.winfo_screenheight() / 2 - self.win_height / 2)

    def calc_x_constraint(self, standard_x, offset):
        standard_position = standard_x.place_info()
        return int(standard_position["x"]) + int(standard_position["width"]) + offset

    def calc_y_constraint(self, standard_y, offset):
        standard_position = standard_y.place_info()
        return int(standard_position["y"]) + int(standard_position["height"]) + offset

    def make_title(self, text):
        title = tkinter.Label(self.window, text=text, font=36)
        title.place(x=20, y=0, width=self.win_width - 40, height=80)
        return title

    def make_label(self, text, position, cst_x=None, cst_y=None):
        x_pos = position.offset_x
        y_pos = position.offset_y
        if cst_x is not None:
            x_pos = self.calc_x_constraint(cst_x, position.offset_x)
        if cst_y is not None:
            y_pos = self.calc_y_constraint(cst_y, position.offset_y)
        label = tkinter.Label(self.window)
        label.config(text=text)
        label.place(x=x_pos, y=y_pos, width=position.width, height=position.height)
        return label

    def make_entry(self, text, position, cst_x=None, cst_y=None, readonly=False):
        x_pos = position.offset_x
        y_pos = position.offset_y
        if cst_x is not None:
            x_pos = self.calc_x_constraint(cst_x, position.offset_x)
        if cst_y is not None:
            y_pos = self.calc_y_constraint(cst_y, position.offset_y)
        entry = tkinter.Entry(self.window)
        entry.delete(0, "end")
        entry.insert(0, text)
        if readonly:
            entry.configure(state="readonly")

        entry.place(x=x_pos, y=y_pos, width=position.width, height=position.height)
        return entry

    def make_combo_box(self, values_list, position, cst_x=None, cst_y=None, readonly=False):
        x_pos = position.offset_x
        y_pos = position.offset_y
        if cst_x is not None:
            x_pos = self.calc_x_constraint(cst_x, position.offset_x)
        if cst_y is not None:
            y_pos = self.calc_y_constraint(cst_y, position.offset_y)

        combo_box = tkinter.ttk.Combobox(self.window, values=values_list)
        combo_box.current(0)
        if readonly:
            combo_box.configure(state="readonly")

        combo_box.place(x=x_pos, y=y_pos, width=position.width, height=position.height)
        return combo_box

    def make_button(self, text, position, cst_x=None, cst_y=None, status="normal", onclick=None):
        x_pos = position.offset_x
        y_pos = position.offset_y
        if cst_x is not None:
            x_pos = self.calc_x_constraint(cst_x, position.offset_x)
        if cst_y is not None:
            y_pos = self.calc_y_constraint(cst_y, position.offset_y)

        button = tkinter.ttk.Button(self.window, text=text, state=status, command=onclick)
        button.place(x=x_pos, y=y_pos, width=position.width, height=position.height)
        return button

    def make_treeview(self, column_names, column_texts, column_widths, position, cst_x=None, cst_y=None):
        x_pos = position.offset_x
        y_pos = position.offset_y
        if cst_x is not None:
            x_pos = self.calc_x_constraint(cst_x, position.offset_x)
        if cst_y is not None:
            y_pos = self.calc_y_constraint(cst_y, position.offset_y)

        treeview = tkinter.ttk.Treeview(self.window, columns=column_names, selectmode="browse")
        treeview.column("#0", width=0, stretch=False)
        for (idx, column) in column_texts:
            treeview.column("#" + str(1 + idx), width=column_widths[idx])
            treeview.heading("#" + str(1 + idx), text=column)
        treeview.place(x=x_pos, y=y_pos, width=position.width, height=position.height)
        return treeview


class Position:
    offset_x = 0
    offset_y = 0
    width = 0
    height = 0

    def __init__(self, x, y, w, h):
        self.offset_x = x
        self.offset_y = y
        self.width = w
        self.height = h
