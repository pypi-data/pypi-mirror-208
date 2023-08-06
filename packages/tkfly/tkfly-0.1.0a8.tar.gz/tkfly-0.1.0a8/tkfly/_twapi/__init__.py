from tkfly import fly_local, fly_load5


def _load_twapi():
    fly_load5(fly_local()+"\\_twapi")


if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()

    _load_twapi()

    root.mainloop()