from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadTitleBar(FlyRadWidget):
    def __init__(self, *args, width=200, height=25, theme="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(theme=theme)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadTitleBar
        self._widget = RadTitleBar()


if __name__ == '__main__':
    root = tk.Tk()
    titlebar = FlyRadTitleBar()
    titlebar.pack()
    root.mainloop()