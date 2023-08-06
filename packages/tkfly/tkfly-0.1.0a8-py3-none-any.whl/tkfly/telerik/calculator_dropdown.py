from tkfly.telerik.button import FlyRadButton
import tkinter as tk


class FlyRadCalculatorDropDown(FlyRadButton):
    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadCalculatorDropDown
        self._widget = RadCalculatorDropDown()


if __name__ == '__main__':
    root = tk.Tk()
    button = FlyRadCalculatorDropDown()
    button.pack()
    root.mainloop()