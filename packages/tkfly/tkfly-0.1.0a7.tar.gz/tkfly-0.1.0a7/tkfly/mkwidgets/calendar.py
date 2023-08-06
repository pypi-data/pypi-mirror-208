from tkfly import fly_local, fly_load4, fly_root, fly_chdir
from tkfly.mkwidgets import load_mkwidget
from tkinter import Widget, ttk, Frame


def calendar_demo():
    load_mkwidget()
    fly_root().eval("""
pack [calendar .cal]
    """)


class Calendar(Frame):
    def __init__(self, master=None):
        load_mkwidget()
        Widget.__init__(self, master, "calendar")
    
    def configure(self, **kwargs):
        """

        :return:
        """

        super().configure(**kwargs)

    def get(self, format: str = "%m/%d/%Y"):
        return self.tk.call(self._w, "get", format)


if __name__ == '__main__':
    from tkinter import Tk, Button

    root = Tk()

    cale = Calendar()
    cale.pack(fill="both", expand="yes")

    print(cale.get("%Y-%m-%d"))

    root.mainloop()