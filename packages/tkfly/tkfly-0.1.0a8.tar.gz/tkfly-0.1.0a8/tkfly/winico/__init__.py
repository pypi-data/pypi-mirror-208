from tkfly._winico import *


class FlyWinico(object):
    def default_event(self, Message, X, Y):
        if Message == "WM_RBUTTONDOWN":
            from tkinter import Menu, _default_root
            Menu = Menu(tearoff=False)
            Menu.add_command(label="Quit", command=_default_root.quit)
            Menu.tk_popup(X, Y)

    def create(self, icon=None, event=None):
        from tkfly._winico import taskbar, createfrom
        from tkinter import _default_root
        if icon is None:
            from tkfly._winico import load
            icon = load("application")
        else:
            icon = createfrom(icon)

        if event is None:
            event = self.default_event
        taskbar("add", icon, (_default_root.register(event), "%m", "%x", "%y"))
        return icon

    def delete(self, icon):
        from tkfly._winico import taskbar
        taskbar("delete", icon)
