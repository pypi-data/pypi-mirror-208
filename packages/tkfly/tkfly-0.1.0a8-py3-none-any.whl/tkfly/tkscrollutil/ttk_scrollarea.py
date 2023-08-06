from tkinter.ttk import Widget
from tkfly.tkscrollutil.load import load_tile
from tkfly.tkscrollutil.attrib import Attrib


class ScrollArea(Widget, Attrib):
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

        WIDGET-SPECIFIC OPTIONS

            autohidescrollbars, lockinterval,
            respectheader, respecttitlecolumns, setfocus, xscrollbarmode, yscrollbarmode

        """
        load_tile()
        Widget.__init__(self, master, "scrollutil::scrollarea", kw, )

    def setwidget(self, widget: Widget = ""):
        return self.tk.call(self._w, "setwidget", widget)


if __name__ == '__main__':
    from tkinter import Tk, Listbox
    root = Tk()

    area = ScrollArea(root)
    list = Listbox(area)
    for item in range(30):
        list.insert(item+1, item+1)
    area.setwidget(list)
    area.pack(fill="both", expand="yes")

    root.mainloop()