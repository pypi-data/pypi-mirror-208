from tkfly import fly_local, fly_load4


def load_tkpdf():
    fly_load4("mupdf::widget", fly_local()+"\\_mupdf")


if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()

    load_tkpdf()

    root.mainloop()