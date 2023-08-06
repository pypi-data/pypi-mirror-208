from tkfly import fly_local, fly_load4, fly_root, fly_chdir
from tkfly.mkwidgets import load_mkwidget
from tkinter import Toplevel


def document_demo():
    load_mkwidget()
    fly_root().eval("""
. config -title {Main Window}

window .w
.w config -title {New Window} -minsize {320 200}
.w config -ondelete {
if { [tk_messageBox -icon question -message "Close it?" -type yesno] == "yes" } {
  destroy .w
}
}
    """)


class Window(Toplevel):
    def __init__(self, master=None):
        load_mkwidget()
        Toplevel.__init__(self, master, name="window")
    

if __name__ == '__main__':
    from tkinter import Tk, Button

    root = Tk()

    document = Window()
    document.title("asdas")

    root.mainloop()