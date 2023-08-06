from tkinter.ttk import Widget
from tkfly.tkscrollutil.load import load_tile
from tkfly.tkscrollutil.attrib import Attrib


class ScrollSync(Widget, Attrib):
    def __init__(self, master=None, cnf={}, **kw):
        """
        STANDARD OPTIONS

            activebackground, activeforeground, anchor,
            background, bitmap, borderwidth, cursor,
            disabledforeground, font, foreground
            highlightbackground, highlightcolor,
            highlightthickness, image, justify,
            padx, pady, relief, repeatdelay,
            repeatinterval, takefocus, text,
            textvariable, underline, wraplength

        """
        try:
            load_tile(master)
        except:
            from tkinter import _default_root
            load_tile(_default_root)
        Widget.__init__(self, master, "scrollutil::scrollsync", kw, )

    def setwidgets(self, widgetList: list):
        return self.tk.call(self._w, "setwidgets", widgetList)


if __name__ == '__main__':
    from tkinter import Tk, Listbox, Frame
    from tkfly.tkscrollutil import ttkScrollArea
    root = Tk()

    frame = Frame()

    area = ttkScrollArea(frame, yscrollbarmode="static")
    sync = ScrollSync(area)
    area.setwidget(sync)

    area.pack(fill="y", side="right")

    list1 = Listbox()
    list1.pack(fill="both", side="left", expand="yes")
    list2 = Listbox()
    list2.pack(fill="both", side="right", expand="yes")

    for item in range(300):
        list1.insert(item, item)
        list2.insert(item, item)

    sync.setwidgets([list1, list2])

    frame.pack(fill="both", expand="yes")

    root.mainloop()