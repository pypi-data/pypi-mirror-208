from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def load_tooltip():
    _load_tklib()
    fly_load4("tooltip", fly_local()+"\\_tklib\\tooltip")


class Tooltip(Widget):
    def __init__(self, master=None):
        load_tooltip()

        super().__init__(master, "tooltip::tooltip")

    def tooltip(self, widget, tooltip: str = "tooltip"):
        fly_root().call("tooltip::tooltip", widget,
                        "--", tooltip)

    def fade(self, boolean: bool = True):
        self.tk.call("tooltip::tooltip", "fade", boolean)

    def delay(self, millisecs: int = 50):
        self.tk.call("tooltip::tooltip", "delay", millisecs)

    def clear(self, pattern: str = "defaults"):
        self.tk.call("tooltip::tooltip", "clear", "-pattern", pattern)


def tooltip_example_tcl():
    load_tooltip()
    fly_root().eval("""
# Demonstrate widget tooltip
package require tooltip
pack [label .l -text "label"]
tooltip::tooltip .l "This is a label widget"

# Demonstrate menu tooltip
package require tooltip
. configure -menu [menu .menu]
.menu add cascade -label Test -menu [menu .menu.test -tearoff 0]
.menu.test add command -label Tooltip
tooltip::tooltip .menu.test -index 0 "This is a menu tooltip"

# Demonstrate canvas item tooltip
package require tooltip
pack [canvas .c]
set item [.c create rectangle 10 10 80 80 -fill red]
tooltip::tooltip .c -item $item "Canvas item tooltip"

# Demonstrate listbox item tooltip
package require tooltip
pack [listbox .lb]
.lb insert 0 "item one"
tooltip::tooltip .lb -item 0 "Listbox item tooltip"

# Demonstrate text tag tooltip
package require tooltip
pack [text .txt]
.txt tag configure TIP-1 -underline 1
tooltip::tooltip .txt -tag TIP-1 "tooltip one text"
.txt insert end "An example of a " {} "tooltip" TIP-1 " tag.\n" {}
""")


if __name__ == '__main__':
    from tkinter import Tk, Entry, ttk

    root = Tk()

    tooltip_example_tcl()

    root.mainloop()