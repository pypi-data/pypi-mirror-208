from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadStatusBar(FlyRadWidget):
    def __init__(self, *args, width=300, height=30, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadStatusStrip
        self._widget = RadStatusStrip()

    def configure(self, **kwargs):
        if "sizegrip" in kwargs:
            self._widget.SizingGrip = kwargs.pop("sizegrip")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "sizegrip":
            return self._widget.SizingGrip
        else:
            return super().cget(attribute_name)

    from tkfly.telerik.elements import FlyRadElement

    def add(self, item: FlyRadElement):
        self._widget.Items.AddRange(item.widget())


if __name__ == '__main__':
    from tkfly import FlyRadTextElement, FlyRadButtonElement
    root = tk.Tk()
    statusbar = FlyRadStatusBar()
    statusbar.add(FlyRadTextElement("Label"))
    statusbar.add(FlyRadButtonElement("Button"))
    statusbar.pack(side="bottom", fill="x")
    root.mainloop()