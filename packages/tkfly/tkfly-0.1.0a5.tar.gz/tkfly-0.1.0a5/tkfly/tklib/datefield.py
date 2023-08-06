from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget, ttk


def load_datefield():
    _load_tklib()
    fly_load4("datefield", fly_local()+"\\_tklib\\datefield")


class DateField(ttk.Entry):
    def __init__(self, master=None, **kw):
        """Constructs a Ttk Entry widget with the parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus, xscrollcommand

        WIDGET-SPECIFIC OPTIONS

            exportselection, invalidcommand, justify, show, state,
            textvariable, validate, validatecommand, width, format

        VALIDATION MODES

            none, key, focus, focusin, focusout, all
        """
        load_datefield()
        super().__init__(master, "datefield::datefield", **kw)

    def demo(self):
        self.tk.eval("""
::datefield::datefield .df -background yellow -textvariable myDate \
-format "%Y-%m-%d"
pack .df
""")


if __name__ == '__main__':
    from tkinter import Tk, Entry, ttk, Variable

    root = Tk()

    datevar = Variable()

    datefield = DateField(textvariable=datevar, format="%Y-%m-%d")
    print(datefield.get())
    datefield.pack()

    root.mainloop()