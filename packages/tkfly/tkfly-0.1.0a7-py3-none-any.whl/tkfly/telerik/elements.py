class FlyRadElement(object):
    def __init__(self):
        self.init()

    def onclick(self, func):
        self._widget.Click += lambda _1, _2: func()

    def ondown(self, func):
        self._widget.MouseDown += lambda _1, _2: func()

    def onup(self, func):
        self._widget.MouseUp += lambda _1, _2: func()

    def init(self):
        from tkfly import FlyRadLoadBase
        FlyRadLoadBase()

    def widget(self):
        return self._widget

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        elif "anchor" in kwargs:
            anchor = kwargs.pop("anchor")
            from System.Drawing import ContentAlignment
            if anchor == "center":
                self._widget.Alignment = ContentAlignment.MiddleCenter
            elif anchor == "w":
                self._widget.Alignment = ContentAlignment.MiddleLeft
            elif anchor == "e":
                self._widget.Alignment = ContentAlignment.MiddleRight
            elif anchor == "n":
                self._widget.Alignment = ContentAlignment.MiddleTop
            elif anchor == "s":
                self._widget.Alignment = ContentAlignment.MiddleBottom
            elif anchor == "nw":
                self._widget.Alignment = ContentAlignment.TopLeft
        elif "text_anchor_ment" in kwargs:
            anchor = kwargs.pop("text_anchor_ment")
            from System.Drawing import ContentAlignment
            if anchor == "center":
                self._widget.TextAlignment = ContentAlignment.MiddleCenter
            elif anchor == "w":
                self._widget.TextAlignment = ContentAlignment.MiddleLeft
            elif anchor == "e":
                self._widget.TextAlignment = ContentAlignment.MiddleRight
            elif anchor == "n":
                self._widget.TextAlignment = ContentAlignment.MiddleTop
            elif anchor == "s":
                self._widget.TextAlignment = ContentAlignment.MiddleBottom
            elif anchor == "nw":
                self._widget.TextAlignment = ContentAlignment.TopLeft
            elif anchor == "ne":
                self._widget.TextAlignment = ContentAlignment.TopRight
            elif anchor == "sw":
                self._widget.TextAlignment = ContentAlignment.BottomLeft
            elif anchor == "se":
                self._widget.TextAlignment = ContentAlignment.BottomRight

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text


from tkfly.telerik.label import FlyRadLabel
from tkfly.telerik.button import FlyRadButton
from tkfly.telerik.text import FlyRadText


class FlyRadLabelElement(FlyRadElement, FlyRadLabel):
    def __init__(self, text=""):
        super().__init__()
        self.configure(text=text)

    def init(self):
        from tkfly import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadLabelElement
        self._widget = RadLabelElement()


class FlyRadButtonElement(FlyRadElement, FlyRadButton):
    def __init__(self, text=""):
        super().__init__()
        self.configure(text=text)

    def init(self):
        from tkfly import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadButtonElement
        self._widget = RadButtonElement()


class FlyRadTextElement(FlyRadElement, FlyRadText):
    def __init__(self, text=""):
        super().__init__()
        self.configure(text=text)

    def init(self):
        from tkfly import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadTextBoxElement
        self._widget = RadTextBoxElement()

