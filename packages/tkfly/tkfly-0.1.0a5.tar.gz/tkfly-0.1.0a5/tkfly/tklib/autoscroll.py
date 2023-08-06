from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def load_autoscroll():
    _load_tklib()
    fly_load4("autoscroll", fly_local()+"\\_tklib\\autoscroll")


def autoscroll(widget: Widget):
    load_autoscroll()
    fly_root().call("autoscroll::autoscroll", widget)


if __name__ == '__main__':
    from tkinter import Tk, Listbox, ttk

    root = Tk()

    list = Listbox()
    list.pack()

    autoscroll(list)

    root.mainloop()