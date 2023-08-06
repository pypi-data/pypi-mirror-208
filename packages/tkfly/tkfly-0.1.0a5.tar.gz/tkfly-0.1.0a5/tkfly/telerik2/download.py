import os
import requests


def gets(path):
    if not os.path.exists("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls"):
        from tkinter.messagebox import showinfo
        showinfo("Info", "Getting Telerik.zip")
        print(f"Get: {path}")
        try:
            telerik = requests.get(path)
        except:
            from tkinter.messagebox import showerror
            showerror("Error", "Get Telerik.zip is fail")
            print("Error: Get Telerik.zip is fail")
        else:
            print("Write: C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.zip")
            open("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.zip", "w+").write(telerik.content)
            print("Zip: C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.zip")
    else:
        from tkinter.messagebox import showerror
        print("Error: Telerik.zip is downloaded")
        showerror("Error", "Telerik.zip is downloaded")

if __name__ == '__main__':
    import tkinter as tk
    import tkinter.ttk as ttk

    root = tk.Tk()

    caption = ttk.Label(root, text="Telerik.zip", anchor="center")
    caption.pack(fill="both", expand=True, side="top", padx=5, pady=5, ipadx=10, ipady=5)

    path_var = tk.StringVar()
    path_var.set("https://xiangqinxi-development-resourse.netlify.app/_downloads/ad7db9792726d7e4da1f051978522ad3/Telerik.zip")

    def get():
        from threading import Thread
        Thread(target=lambda: gets(path_var.get())).run()

    get = ttk.Button(root, text="Get", command=get)
    get.pack(fill="x", side="bottom", padx=10, pady=10, ipadx=10, ipady=5)

    path = ttk.Entry(root, textvariable=path_var)
    path.pack(fill="x", side="bottom", padx=10, pady=10, ipadx=10, ipady=5)

    root.mainloop()