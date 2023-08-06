from tkinter import Widget
from tkfly.tkscrollutil.load import load
from tkfly.tkscrollutil.attrib import Attrib


class ScrollSync(Widget, Attrib):
    def __init__(self, master=None, cnf={}, **kw):
        """The command creates a new window named and of the class , and makes it into a scrollarea widget.
        Additional options, described below, may be specified on the command line or in the option database to configure aspects of the scrollarea such as its borderwidth, relief, and display mode to be used for the scrollbars.
        The command returns its argument.
        At the time this command is invoked, there must not exist a window named , but 's parent must exist.scrollutil::scrollareapathNameScrollareascrollutil::scrollareapathNamepathNamepathName

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
            load(master)
        except:
            from tkinter import _default_root
            load(_default_root)
        Widget.__init__(self, master, "scrollutil::scrollsync", cnf, kw, )

    def setwidgets(self, widgetList: list):
        return self.tk.call(self._w, "setwidgets", widgetList)

    def widgets(self):
        return self.tk.call(self._w, "widgets")

    def xview(self, *args):
        return self.tk.call(self._w, "xview", *args)

    def yview(self, *args):
        return self.tk.call(self._w, "yview", *args)


if __name__ == '__main__':
    from tkinter import Tk, Listbox, Frame
    from tkfly.tkscrollutil import ScrollArea
    root = Tk()

    frame = Frame()

    area = ScrollArea(frame, yscrollbarmode="static")
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