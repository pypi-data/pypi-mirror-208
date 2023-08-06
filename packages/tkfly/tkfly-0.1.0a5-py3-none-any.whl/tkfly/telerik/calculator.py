from tkfly.telerik import FlyTKWidget
import tkinter as tk


class FlyTKCalculator(FlyTKWidget):
    def __init__(self, *args, width=240, height=360, theme="", command=None, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        if command is not None:
            self.bind("<<Click>>", lambda _: command())
        self.configure(theme=theme)

    def init(self):
        from tkfly.telerik import FlyTKLoadBase
        FlyTKLoadBase()
        from Telerik.WinControls.UI import RadCalculator
        self._widget = RadCalculator()


if __name__ == '__main__':
    root = tk.Tk()
    button = FlyTKCalculator()
    button.pack()
    root.mainloop()