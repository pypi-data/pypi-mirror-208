from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def load_menubar():
    _load_tklib()
    fly_load4("menubar", fly_local()+"\\_tklib\\menubar")
    fly_load4("menubar::tree", fly_local()+"\\_tklib\\menubar\\")


class MenubarTree(Widget):
    def __init__(self, master=None):
        load_menubar()
        super().__init__(master, "menubar::tree create")


if __name__ == '__main__':
    from tkinter import Tk, Entry

    root = Tk()

    load_menubar()

    root.mainloop()