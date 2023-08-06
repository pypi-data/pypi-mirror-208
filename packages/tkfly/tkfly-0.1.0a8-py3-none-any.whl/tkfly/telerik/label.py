from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadLabel(FlyRadWidget):
    def __init__(self, *args, width=100, height=30, text="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadLabel
        self._widget = RadLabel()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)


if __name__ == '__main__':
    root = tk.Tk()
    label = FlyRadLabel(text="Label")
    label.pack()
    root.mainloop()