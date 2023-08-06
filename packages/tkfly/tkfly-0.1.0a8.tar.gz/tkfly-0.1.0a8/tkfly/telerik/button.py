from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadButton(FlyRadWidget):
    def __init__(self, *args, width=100, height=30, text: str = "", tooltip: str = "", theme: str = "", command=None, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        if command is not None:
            self.bind("<<Click>>", lambda _: command())
        self.configure(text=text, theme=theme, tooltip=tooltip)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadButton
        self._widget = RadButton()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)

    def perform(self):
        self._widget.PerformClick()


if __name__ == '__main__':
    root = tk.Tk()
    button = FlyRadButton(text="<html><size=12>RadButton")
    button.pack()
    root.mainloop()