from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadProgressBar(FlyRadWidget):
    def __init__(self, *args, width=100, height=25, text="", theme: str = "", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text, theme=theme)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadProgressBar
        self._widget = RadProgressBar()

    def configure(self, **kwargs):
        if "value1" in kwargs:
            self._widget.Value1 = kwargs.pop("value1")
        elif "value2" in kwargs:
            self._widget.Value2 = kwargs.pop("value2")
        elif "maximum" in kwargs:
            self._widget.Maximum = kwargs.pop("maximum")
        elif "minimum" in kwargs:
            self._widget.Minimum = kwargs.pop("minimum")
        elif "step" in kwargs:
            self._widget.Step = kwargs.pop("step")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "value1":
            return self._widget.Value1
        elif attribute_name == "value2":
            return self._widget.Value2
        elif attribute_name == "maximum":
            return self._widget.Maximum
        elif attribute_name == "minimum":
            return self._widget.Minimum
        elif attribute_name == "step":
            return self._widget.Step
        else:
            return super().cget(attribute_name)


if __name__ == '__main__':
    root = tk.Tk()
    progressbar = FlyRadProgressBar()
    progressbar.configure(value1=50, value2=25)
    progressbar.pack(fill="x")
    while True:
        progressbar.configure(value1=progressbar.cget("value1")+1)
        if progressbar.cget("value1") >= 100:
            progressbar.configure(value1=0)
        from time import sleep
        sleep(0.01)
        root.update()