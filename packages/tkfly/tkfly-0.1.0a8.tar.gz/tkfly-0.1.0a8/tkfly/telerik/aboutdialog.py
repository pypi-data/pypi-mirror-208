from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadAboutBox(object):
    def __init__(self):
        self.init()

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadAboutBox
        self._widget = RadAboutBox()

    def widget(self):
        return self._widget

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")

    def show(self):
        self._widget.ShowDialog()


if __name__ == '__main__':
    root = tk.Tk()

    dialog = FlyRadAboutBox()
    dialog.show()

    root.mainloop()