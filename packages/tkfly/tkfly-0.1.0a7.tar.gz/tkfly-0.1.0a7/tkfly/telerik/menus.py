from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadMenuItem(object):
    def __init__(self, text="", command=None):
        self.init()
        if command is not None:
            self._widget.Click += lambda sender, e: command()
        self.configure(text=text)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadMenuItem
        self._widget = RadMenuItem()

    def widget(self):
        return self._widget

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")

    def add(self, item):
        self._widget.Items.AddRange(item.widget())


class FlyRadContextMenu(object):
    def __init__(self):
        self.init()

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadContextMenu
        self._widget = RadContextMenu()

    def widget(self):
        return self._widget

    def add(self, item):
        self._widget.Items.AddRange(item.widget())

    def show(self, x: int, y: int):
        self._widget.Show(x, y)


class FlyRadMenuBar(FlyRadWidget):
    def __init__(self, *args, width=100, height=30, text="Telerik.WinControls.TitleBar", theme: str = "", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text, theme=theme)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadMenu
        self._widget = RadMenu()

    def configure(self, **kwargs):
        if "theme" in kwargs:
            self._widget.ThemeName = kwargs.pop("theme")

    def add(self, item):
        self._widget.Items.AddRange(item.widget())


if __name__ == '__main__':
    root = tk.Tk()
    menubar = FlyRadMenuBar()
    menufile = FlyRadMenuItem("File")
    menufile.add(FlyRadMenuItem("Open.."))
    menubar.add(menufile)
    menubar.pack(fill="x", side="top")
    contextmenu = FlyRadContextMenu()
    contextmenu.add(menufile)
    contextmenu.show(10, 10)
    root.mainloop()