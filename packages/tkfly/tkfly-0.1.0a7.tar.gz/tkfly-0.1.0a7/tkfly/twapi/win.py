from tkfly.twapi import load_twapi
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def getWindowLong():
    load_twapi()
    return


if __name__ == '__main__':
    from tkinter import Tk

    root = Tk()

    load_twapi()

    root.eval("""
package require twapi

# 获取窗口句柄
set hwnd [twapi::find_window -class "TkTopLevel" -toplevel]

# 将窗口句柄转换为 TcL 解释器中的句柄类型
set hwin [hwin $hwnd]

# 在窗口上显示MessageBox
set lpText "Hello

    """)

    root.mainloop()