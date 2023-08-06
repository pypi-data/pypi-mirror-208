from tkfly.twapi import load_twapi
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def find_windows(*args, **kwargs):
    load_twapi()
    return fly_root().call("twapi::find_windows", *args, **kwargs)


def get_parent_window(*args, **kwargs):
    load_twapi()
    return fly_root().call("twapi::get_parent_window", *args, **kwargs)


def tkpath_to_hwnd(*args, **kwargs):
    load_twapi()
    return fly_root().call("twapi::tkpath_to_hwnd", *args, **kwargs)


if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()
    root.title("helloworld")

    print(find_windows("-text", "helloworld"))


    root.mainloop()