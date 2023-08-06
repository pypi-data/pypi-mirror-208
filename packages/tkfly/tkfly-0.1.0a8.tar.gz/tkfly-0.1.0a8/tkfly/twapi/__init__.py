from tkfly._twapi import _load_twapi
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def load_twapi():
    _load_twapi()
    fly_load4("twapi", fly_local() + "\\_twapi")


def debuglog_enable():
    load_twapi()
    return fly_root().call("twapi::debuglog_enable")


def get_version():
    load_twapi()
    return fly_root().call("twapi::get_version")


if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()

    print(get_version())

    root.mainloop()