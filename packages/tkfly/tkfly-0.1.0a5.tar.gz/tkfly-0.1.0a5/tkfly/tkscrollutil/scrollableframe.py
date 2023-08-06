from tkinter import Widget, Frame
from tkfly.tkscrollutil.load import load
from tkfly.tkscrollutil.attrib import Attrib


class ScrollLabelFrame(Widget, Attrib):
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

        WIDGET-SPECIFIC OPTIONS

            contentheight
            contentwidth
            fitcontentheight
            fitcontentwidth
            height
            takefocus
            width screenDistance
            xscrollincrement
            yscrollincrement

        """
        load()
        Widget.__init__(self, master, "scrollutil::scrollableframe", cnf, kw, )

    def contentframe(self) -> Frame:
        _frame = self.tk.call(self._w, "contentframe")

        _Frame = Frame()
        _Frame.nametowidget(_frame)

        return _Frame


if __name__ == '__main__':
    from tkinter import Tk, Label
    from tkfly.tkscrollutil.scrollarea import ScrollArea
    from tkfly.tkscrollutil.wheelevent import createWheelEventBindings
    root = Tk()

    area = ScrollArea(root, yscrollbarmode="static")
    frame = ScrollLabelFrame(area)
    area.setwidget(frame)

    context = frame.contentframe()

    createWheelEventBindings()

    for item in range(10):
        Label(context, text=str(item)).pack()

    area.pack(fill="both", expand="yes")

    root.mainloop()