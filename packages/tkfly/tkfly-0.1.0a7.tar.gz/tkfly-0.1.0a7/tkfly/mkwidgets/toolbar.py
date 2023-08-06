from tkfly import fly_local, fly_load4, fly_root, fly_chdir
from tkfly.mkwidgets import load_mkwidget
from tkinter import Widget, ttk, Frame, PhotoImage, BitmapImage


def toolbar_demo():
    load_mkwidget()
    with fly_chdir(fly_local() + "\\_mkwidgets\\"):
        fly_root().eval("""
    wm minsize . 320 250
    
    image create photo p1 -file ./demos/images/Notebook.gif
    image create photo p2 -file ./demos/images/Compass.gif
    
    pack [frame .work -bg gray50] -fill both -expand 1
    grid [frame .test] -in .work
    
    pack [text .test.text -width 40 -height 10 -wrap word]
    toolbar .test.tbar -state fixed -side bottom -relief sunken
    .test.text insert end "Above are regular buttons, checkbuttons and radiobuttons."
    .test.text insert end "The Toolbars can be dragged to the four window sides."
    .test.text insert end "The right mouse button will invoke a menu.\n"
    
    .test.tbar add button b1 -image p1 -command {.test.text delete 1.0 end }
    .test.tbar add check  b2 -image p2 -command {
    if { [.test.tbar get b2] } {
      .test.text config -bg black -fg white
    } else {
      .test.text config -bg white -fg black
    }
    }
    
    toolbar .tbar1
    .tbar1 add button button1 -image p2 -command {.test.text insert end "button1 clicked\n"; .test.text see end }
    .tbar1 add button button2 -image p2 -command {.test.text insert end "button2 clicked\n"; .test.text see end }
    .tbar1 add separator s1
    .tbar1 add checkbutton check1 -image p1 -command {.test.text insert end "check1 clicked\n"; .test.text see end }
    .tbar1 add checkbutton check2 -image p1 -command {.test.text insert end "check2 clicked\n"; .test.text see end }
    .tbar1 add separator s2
    .tbar1 add radiobutton radio1 -image p1 -command {.test.text insert end "radio1 clicked\n"; .test.text see end }
    .tbar1 add radiobutton radio2 -image p2 -command {.test.text insert end "radio2 clicked\n"; .test.text see end }
    .tbar1 add radiobutton radio3 -image p1 -command {.test.text insert end "radio3 clicked\n"; .test.text see end }
    .tbar1 add radiobutton radio4 -image p2 -command {.test.text insert end "radio4 clicked\n"; .test.text see end }
    
    toolbar .t2 -side bottom
    .t2 add button b1 -image p1 -bg red
    .t2 add button b2 -image p2 -bg green
    .t2 add button b3 -image p1 -bg yellow
    .t2 add button b4 -image p2 -bg blue
    .t2 add button b5 -image p1 -bg white
    .t2 add button b6 -image p2 -bg black
        """)


from enum import Enum


class TOOLBAR_STATE_TYPE:
    NORMAL = "normal"
    FIXED = "fixed"
    WITHDRAWN = "withdrawn"


class TOOLBAR_ADD_TYPE:
    BUTTON = "button"
    CHECKBUTTON = "checkbutton"
    RADIOBUTTON = "radiobutton"
    SEPARATOR = "separator"


class Toolbar(Frame):
    def __init__(self, master=None):
        load_mkwidget()
        Widget.__init__(self, master, "toolbar")

    def configure(self, **kwargs):
        """
        x : 文档窗口x坐标
        y : 文档窗口y坐标
        title : 文档窗口标题

        :return:
        """

        super().configure(**kwargs)

    def add(self, type, name=False, command=None, image: PhotoImage = None, bg="whitesmoke", fg="black"):
        if not name:
            name = self.__class__.__name__.lower()
            if self.master._last_child_ids is None:
                self.master._last_child_ids = {}
            count = self.master._last_child_ids.get(name, 0) + 1
            self.master._last_child_ids[name] = count
            if count == 1:
                name = '!%s' % (name,)
            else:
                name = '!%s%d' % (name, count)
        if image is None:
            with fly_chdir(fly_local() + "\\_mkwidgets\\"):
                self.tk.eval("image create photo !photoimage -file ./demos/images/Notebook.gif")
                image = "!photoimage"
        if command is None:
            def _e():
                pass

            command = _e
        if type is TOOLBAR_ADD_TYPE.BUTTON or type is TOOLBAR_ADD_TYPE.RADIOBUTTON or type is TOOLBAR_ADD_TYPE.CHECKBUTTON:
            self.tk.call(self._w, "add", type, name, "-command", self.register(command), "-image", image,
                         "-bg", bg, "-fg", fg)
        else:
            self.tk.call(self._w, "add", type, name)
        return name

    def delete(self, name):
        """
        删除工具栏组件

        :param name: 工具栏组件
        :return:
        """
        self.tk.call(self._w, "delete", name)

    def invoke(self, name, newstate):
        """
        设置工具栏组件状态

        :param name: 工具栏组件
        :param newstate: 新状态
        :return:
        """
        self.tk.call(self._w, "invoke", name, newstate)

    set = invoke

    def get(self, name):
        """
        获取工具栏组件状态

        :param name: 工具栏组件
        :return:
        """
        self.tk.call(self._w, "get", name)


ToolBar = Toolbar

if __name__ == '__main__':
    from tkinter import Tk, Button

    root = Tk()

    toolbar = ToolBar()
    toolbar.configure(side="top", state=TOOLBAR_STATE_TYPE.FIXED)

    button1 = toolbar.add(TOOLBAR_ADD_TYPE.BUTTON)
    button2 = toolbar.add(TOOLBAR_ADD_TYPE.BUTTON)
    toolbar.delete(button2)
    separator1 = toolbar.add(TOOLBAR_ADD_TYPE.SEPARATOR)
    checkbutton1 = toolbar.add(TOOLBAR_ADD_TYPE.CHECKBUTTON)

    toolbar.invoke(checkbutton1, True)

    toolbar.pack(fill="x", side="top")

    root.mainloop()
