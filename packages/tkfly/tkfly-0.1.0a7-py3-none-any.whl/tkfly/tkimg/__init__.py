from tkfly import fly_local, fly_load5


def _load_tkimg():
    fly_load5(fly_local()+"\\tkimg")



if __name__ == '__main__':
    from tkinter import *

    root = Tk()
    _load_tkimg()
    root.mainloop()
