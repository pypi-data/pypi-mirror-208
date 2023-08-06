from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def load_wcb():
    _load_tklib()
    fly_load4("wcb", fly_local()+"\\_tklib")
    fly_load4("Wcb", fly_local()+"\\_tklib")
    fly_load4("wcb", fly_local()+"\\_tklib\\wcb")
    fly_load4("Wcb", fly_local()+"\\_tklib\\wcb")
    fly_load4("wcb", fly_local()+"\\_tklib\\wcb", "wcb.tcl")
    fly_load4("wcb", fly_local()+"\\_tklib\\wcb\\scripts", "wcbEntry.tcl")


def wcb_version():
    return "3.6"


def wcb_changeEntryText(widget, text: str = ""):

    load_wcb()

    fly_root().call("wcb::changeEntryText", widget, text)


if __name__ == '__main__':
    from tkinter import Tk, Entry
    from tkinter import ttk

    root = Tk()

    entry = ttk.Entry()
    wcb_changeEntryText(entry, "asdasd")
    entry.pack()

    root.mainloop()