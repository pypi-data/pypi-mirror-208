import tktelerik
from tkinter import Tk

root = Tk()
theme1 = tktelerik.Windows11()

button = tktelerik.Button(text="Open")
button.configure(theme="Windows11")
alert = tktelerik.DesktopAlert()
alert.configure(theme="Windows", title="DesktopAlert", message="Message")
button.bind("<<Click>>", lambda _: alert.show())
button.pack(fill="x")

root.mainloop()
