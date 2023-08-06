from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadToastNotification(object):
    def __init__(self, master=None, theme=""):
        self.init()
        self.configure(theme=theme)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        from tkfly.telerik.imports import toast_notification
        FlyRadLoadBase()
        toast_notification()
        from Telerik.RadToastNotification import RadToastNotification
        self._widget = RadToastNotification()

    def configure(self, **kwargs):
        if "theme" in kwargs:
            self._widget.ThemeName = kwargs.pop("theme").title()

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "theme":
            return self._widget.ThemeName

    def widget(self):
        return self._widget

    def show(self):
        self._widget.Show()


if __name__ == '__main__':
    root = tk.Tk()
    alert = FlyRadToastNotification()
    alert.show()
    root.mainloop()