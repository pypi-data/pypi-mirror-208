from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def load_chatwidget():
    _load_tklib()
    fly_load4("chatwidget", fly_local()+"\\_tklib\\chatwidget")


class Chat(Widget):
    def __init__(self, master=None):
        load_chatwidget()

        super().__init__(master, "chatwidget::chatwidget")



if __name__ == '__main__':
    from tkinter import Tk, Entry, ttk

    root = Tk()

    chat = Chat()
    chat.pack(fill="both", expand="yes")

    root.mainloop()