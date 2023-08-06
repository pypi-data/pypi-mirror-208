from tkfly.telerik import FlyTKWidget
import tkinter as tk


class FlyTKClock(FlyTKWidget):
    def __init__(self, *args, width=200, height=200,  theme="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(theme=theme)

    def init(self):
        from tkfly.telerik import FlyTKLoadBase
        FlyTKLoadBase()
        from Telerik.WinControls.UI import RadClock
        self._widget = RadClock()


if __name__ == '__main__':
    root = tk.Tk()
    clock = FlyTKClock()
    clock.pack()
    root.mainloop()