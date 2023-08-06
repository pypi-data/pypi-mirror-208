from tkfly._winico.load import load_winico
import os

Smiley = os.path.abspath(os.path.dirname(__file__)) + "//smiley.ico"

TkChat = os.path.abspath(os.path.dirname(__file__)) + "//tkchat.ico"


def smiley():
    return createfrom(Smiley)


def tkchat():
    return createfrom(TkChat)


def createfrom(filename):
    from tkinter import _default_root
    load_winico(_default_root)
    return _default_root.tk.call("winico", "createfrom", filename)


def default_callback(*args, **kwargs):
    pass


def taskbar(id="add", procname="$winico", callback=None, text: str = ""):
    from tkinter import _default_root
    load_winico(_default_root)
    if callback is None:
        callback = _default_root.register(default_callback)
    return _default_root.tk.call("winico", "taskbar", id, procname,
                                 "-callback", callback,
                                 "-text", text)


def load(resourcename, filename=None):
    from tkinter import _default_root
    load_winico(_default_root)
    return _default_root.tk.call("winico", "load", resourcename, filename)


def info(id):
    from tkinter import _default_root
    load_winico(_default_root)
    return _default_root.tk.call("winico", "info", id)


def setwindow(id, size="small"):
    from tkinter import _default_root
    load_winico(_default_root)
    return _default_root.tk.call("winico", "setwindow", id, size)


def delete(id):
    from tkinter import _default_root
    load_winico(_default_root)
    return _default_root.tk.call("winico", "delete", id)
