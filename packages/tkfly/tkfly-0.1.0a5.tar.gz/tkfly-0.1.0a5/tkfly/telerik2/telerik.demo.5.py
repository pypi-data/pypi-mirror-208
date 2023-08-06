import tkfly.telerik2 as tktelerik
from tkinter import Tk

root = Tk()
theme1 = tktelerik.Material()

nav = tktelerik.PageView()
nav.configure(theme="Material")

controls = tktelerik.PageViewPage(parent=nav)
controls.configure(text="Controls")

button1 = tktelerik.Button(controls.frame())
button1.configure(theme="Material", text_anchor_ment="w")
button1.pack(fill="x", padx=10, pady=10)

nav.add_page(controls)
nav.pack(fill="both", expand="yes")

root.mainloop()
