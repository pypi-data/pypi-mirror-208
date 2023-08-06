import tkfly.telerik2 as tktelerik
from tkinter import Tk

root = Tk()
theme1 = tktelerik.Fluent()

list1 = tktelerik.ListBox()
list1.configure(theme="Fluent")
for index in range(4):
    list1.add(list1.create_label("item"+str(index+1)))
list1.pack(fill="both", expand="yes", padx=5, pady=5)

root.mainloop()