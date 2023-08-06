from tkfly.twapi import load_twapi
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def get_os_version():
    load_twapi()
    return fly_root().call("twapi::get_os_version")


if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()

    print(get_os_version())

    root.mainloop()