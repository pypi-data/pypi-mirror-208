import tkfly.telerik2 as tktelerik
from tkinter import Tk


root = Tk()
theme1 = tktelerik.Windows11()

button = tktelerik.Button()
button.configure(theme="Windows11")
button.pack()

root.mainloop()
