from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget, PhotoImage


default_image = "48a232a4254abd50dbec2c78e77426e2"

def load_notifywindow():
    _load_tklib()
    fly_load4("notifywindow", fly_local() + "\\_tklib\\notifywindow")


def notifywindow_notifywindow(message: str = "", image=None):
    load_notifywindow()
    fly_root().call("::notifywindow::notifywindow", message, image)


def notifywindow_demo():
    load_notifywindow()
    fly_root().call("::notifywindow::demo")


class NotifyWindow(object):
    def demo(self):
        notifywindow_demo()

    def popup(self, message: str, image=None):
        if image is None:
            image = "info"
        notifywindow_notifywindow(message, image)


if __name__ == '__main__':
    from tkinter import Tk, Entry, ttk

    root = Tk()

    notifywindow = NotifyWindow()
    notifywindow.popup("hello")

    root.mainloop()
