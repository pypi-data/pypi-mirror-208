from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadClock(FlyRadWidget):
    def __init__(self, *args, width=200, height=200,  theme="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(theme=theme)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadClock
        self._widget = RadClock()

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "value":
            return self._widget.Value

    def system_time(self, show: bool = None):
        if show is None:
            return self._widget.ShowSystemTime
        else:
            self._widget.ShowSystemTime = show


if __name__ == '__main__':
    root = tk.Tk()
    clock = FlyRadClock()
    clock.pack()
    root.mainloop()