from tkinter import Tk, Tcl
from tkfly.core import fly_local, fly_chdir


def run_eval(eval):
    from tkfly.blend2d import load_blend2d
    root = Tk()
    load_blend2d()
    with fly_chdir(fly_local()+"\\blend2d\\demos\\"):
        root.eval(eval)
    root.mainloop()