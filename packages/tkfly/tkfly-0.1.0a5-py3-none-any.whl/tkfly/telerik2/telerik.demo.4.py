import tkfly.telerik2 as tktelerik
from tkinter import Tk

root = Tk()
theme1 = tktelerik.Windows11()

qrcode1 = tktelerik.BarcodeView()
qrcode1.configure(theme="Windows11")
qrcode1.pack(fill="both", expand="yes", padx=5, pady=5)

root.mainloop()