from tkfly.telerik.button import FlyTKButton
import tkinter as tk


class FlyTKCalculatorDropDown(FlyTKButton):
    def init(self):
        from tkfly.telerik import FlyTKLoadBase
        FlyTKLoadBase()
        from Telerik.WinControls.UI import RadCalculatorDropDown
        self._widget = RadCalculatorDropDown()


if __name__ == '__main__':
    root = tk.Tk()
    button = FlyTKCalculatorDropDown()
    button.pack()
    root.mainloop()