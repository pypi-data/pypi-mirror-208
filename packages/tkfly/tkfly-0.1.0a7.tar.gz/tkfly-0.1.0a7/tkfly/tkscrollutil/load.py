from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget, ttk


def load_datefield():
    _load_tklib()
    fly_load4("datefield", fly_local()+"\\_tklib\\datefield")


def load():
    _load_tklib()
    fly_load4("scrollutil", fly_local()+"\\_tklib\\scrollutil")


def load_tile():
    _load_tklib()
    fly_load4("scrollutil_tile", fly_local()+"\\_tklib\\scrollutil")
