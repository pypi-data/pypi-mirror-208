from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadDesktopAlert(object):
    def __init__(self, master=None, bindTkDestory=True, theme="", title: str = None, message: str = ""):
        self.init()
        self.configure(theme=theme, title=title, message=message)

        if bindTkDestory:
            from tkfly.core import fly_root
            def _():
                self._widget.Hide()
                fly_root().destroy()
            fly_root().protocol("WM_DELETE_WINDOW", _)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadDesktopAlert
        self._widget = RadDesktopAlert()

    def configure(self, **kwargs):
        if "theme" in kwargs:
            self._widget.ThemeName = kwargs.pop("theme").title()
        elif "title" in kwargs:
            self._widget.CaptionText = kwargs.pop("title")
        elif "message" in kwargs:
            self._widget.ContentText = kwargs.pop("message")

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "theme":
            return self._widget.ThemeName
        elif attribute_name == "title":
            return self._widget.CaptionText
        elif attribute_name == "message":
            return self._widget.ContentText

    def widget(self):
        return self._widget

    def show(self):
        self._widget.Show()


if __name__ == '__main__':
    root = tk.Tk()
    alert = FlyRadDesktopAlert()
    alert.show()
    root.mainloop()