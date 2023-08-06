from tkfly import fly_local, fly_load4, fly_root, fly_chdir
from tkfly.mkwidgets import load_mkwidget
from tkinter import Widget, ttk, Frame


def document_demo():
    load_mkwidget()
    fly_root().eval("""
pack [frame .w -back darkgray] -fill both -expand 1
document .w.d1
document .w.d2
document .w.d3

.w.d3 pack [label .w.d3.f -border 2 -relief sunken -text "1"] -fill both -expand 1
pack [label .w.d3.f.f -border 2 -relief raised -text "2"] -fill both -expand 1
    """)


class Document(Frame):
    def __init__(self, master=None):
        load_mkwidget()
        Widget.__init__(self, master, "document")
    
    def configure(self, **kwargs):
        """
        x : 文档窗口x坐标
        y : 文档窗口y坐标
        title : 文档窗口标题

        :return:
        """

        super().configure(**kwargs)
    

if __name__ == '__main__':
    from tkinter import Tk, Button

    root = Tk()

    document = Document()

    button = ttk.Button(document)
    button.pack(fill="both", expand="yes")

    document.config(title="asdas", icontext="info")

    root.mainloop()