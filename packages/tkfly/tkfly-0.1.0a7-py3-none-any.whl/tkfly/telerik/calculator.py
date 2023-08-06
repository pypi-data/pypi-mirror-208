from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadCalculator(FlyRadWidget):
    def __init__(self, *args, width=240, height=360, theme="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(theme=theme)

        def value_changed(sender, e):
            self.event_generate("<<ValueChanged>>")

        self._widget.ValueChanged += value_changed

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadCalculator
        self._widget = RadCalculator()

    def configure(self, **kwargs):
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "value":
            return self._widget.Value
        else:
            return super().cget(attribute_name)


if __name__ == '__main__':
    root = tk.Tk()
    calc = FlyRadCalculator(value=5)
    calc.pack()
    root.mainloop()