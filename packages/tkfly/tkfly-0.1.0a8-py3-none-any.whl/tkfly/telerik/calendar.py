from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadCalendar(FlyRadWidget):
    def __init__(self, *args, width=320, height=240, theme="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(theme=theme)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadCalendar
        self._widget = RadCalendar()

    def configure(self, **kwargs):
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "value":
            return self._widget.Value
        else:
            return super().cget(attribute_name)

    def navigation(self, show: bool = None):
        if show is None:
            return self._widget.ShowNavigation
        else:
            self._widget.ShowNavigation = show


if __name__ == '__main__':
    root = tk.Tk()
    calc = FlyRadCalendar()
    calc.pack()
    root.mainloop()