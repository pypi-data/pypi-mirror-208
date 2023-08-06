# 基础示例1
import tkfly.telerik2 as tktelerik
from tkinter import Tk

root = Tk()
theme1 = tktelerik.Windows11()

button = tktelerik.Button(text="button1")
button.configure(theme="Windows11")
button.pack(fill="both", expand="yes", padx=5, pady=5)

list1 = tktelerik.ListBox()
list1.configure(theme="Windows11")
for index in range(4):
    list1.add(list1.create_label("item"+str(index+1)))
    list1.pack(fill="both", expand="yes", padx=5, pady=5)

root.mainloop()