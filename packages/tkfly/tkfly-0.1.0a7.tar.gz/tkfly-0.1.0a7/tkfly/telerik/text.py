from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadText(FlyRadWidget):
    def __init__(self, *args, width=100, height=30, text="", theme="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text, theme=theme)

    def init(self):
        from tkfly import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadTextBox
        self._widget = RadTextBox()

    def configure(self, **kwargs):
        if "multiline" in kwargs:
            self._widget.Multiline = kwargs.pop("multiline")
        elif "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        elif "tip_text" in kwargs:
            self._widget.NullText = kwargs.pop("tip_text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "multiline":
            return self._widget.Multiline
        elif attribute_name == "text":
            return self._widget.Text
        elif attribute_name == "tip_text":
            return self._widget.NullText
        else:
            return super().cget(attribute_name)


if __name__ == '__main__':
    root = tk.Tk()
    text = FlyRadText()
    text.pack(fill="x")
    root.mainloop()