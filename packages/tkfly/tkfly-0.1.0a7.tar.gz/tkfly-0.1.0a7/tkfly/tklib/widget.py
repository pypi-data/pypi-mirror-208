from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def load_widget():
    _load_tklib()
    fly_load4("widget::all", fly_local() + "\\_tklib\\widget")


class ToolBar(Widget):
    def __init__(self, master=None,):
        load_widget()
        super().__init__(master, "widget::toolbar")


if __name__ == '__main__':
    from tkinter import Tk, Entry, ttk

    root = Tk()

    toolbar = ToolBar()

    root.mainloop()
