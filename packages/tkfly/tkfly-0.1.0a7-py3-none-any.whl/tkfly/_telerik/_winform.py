import clr

clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
from System.Drawing import Point, Size, Color, Font
from System.Windows.Forms import Panel

from tkinter import Frame


class _Widget(Frame):
    def __init__(self, *args, width=100, height=30, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.init()
        from tkinter import _default_root
        from threading import Thread
        self.bind("<Configure>", self._configure_widget)
        self.bind("<Map>", self._map)
        self.bind("<Unmap>", self._unmap)

        def click(sender, e):
            self.event_generate("<<Click>>")

        def double_click(sender, e):
            self.event_generate("<<DoubleClick>>")

        def enter(sender, e):
            self.event_generate("<<Enter>>")

        def leave(sender, e):
            self.event_generate("<<Leave>>", )

        def up(sender, e):
            self.event_generate("<<Up>>")

        def down(sender, e):
            self.event_generate("<<Down>>")

        self._widget.Click += click
        self._widget.DoubleClick += double_click
        self._widget.MouseEnter += enter
        self._widget.MouseLeave += leave
        self._widget.MouseDown += down
        self._widget.MouseUp += up

        self.tk_forms(self, self._widget)
        self._widget.Visible = False

    def widget(self):
        return self._widget

    def tk_forms(self, parent, child):  # 将Winform组件添加入Tkinter组件
        from ctypes import windll
        windll.user32.SetParent(int(str(child.Handle)),
                                windll.user32.GetParent(parent.winfo_id()))  # 调用win32设置winform组件的父组件

    def forms_tk(self, parent, child):  # 将Tkinter组件添加入Winform组件
        from ctypes import windll
        windll.user32.SetParent(int(str(parent.Handle)),
                                windll.user32.GetParent(child.winfo_id()))  # 调用win32设置tkinter组件的父组件

    def state(self, state=None):
        if state == "active":
            self._widget.Enabled = True
        elif state == "disabled":
            self._widget.Enabled = False
        else:
            return self._widget.Enabled

    def configure(self, **kwargs):
        if "background" in kwargs:
            color = kwargs.pop("background")
            self._widget.FillColor = Color.FromArgb(color[0], color[1], color[2], color[3])
        if "foreground" in kwargs:
            color = kwargs.pop("foreground")
            self._widget.FillColor = Color.FromArgb(color[0], color[1], color[2], color[3])
        elif "border_color" in kwargs:
            color = kwargs.pop("border_color")
            self._widget.RectColor = Color.FromArgb(color[0], color[1], color[2], color[3])
        elif "auto_scroll" in kwargs:
            self._widget.AutoScroll = kwargs.pop("auto_scroll")
        elif "text_anchor" in kwargs:
            anchor = kwargs.pop("text_anchor")
            from System.Drawing import ContentAlignment
            if anchor == "center":
                self._widget.TextAlign = ContentAlignment.MiddleCenter
            elif anchor == "w":
                self._widget.TextAlign = ContentAlignment.MiddleLeft
            elif anchor == "e":
                self._widget.TextAlign = ContentAlignment.MiddleRight
            elif anchor == "n":
                self._widget.TextAlign = ContentAlignment.MiddleTop
            elif anchor == "s":
                self._widget.TextAlign = ContentAlignment.MiddleBottom
            elif anchor == "nw":
                self._widget.TextAlign = ContentAlignment.TopLeft
            elif anchor == "ne":
                self._widget.TextAlign = ContentAlignment.TopRight
            elif anchor == "sw":
                self._widget.TextAlign = ContentAlignment.BottomLeft
            elif anchor == "se":
                self._widget.TextAlign = ContentAlignment.BottomRight
        elif "text_anchor_ment" in kwargs:
            anchor = kwargs.pop("text_anchor_ment")
            from System.Drawing import ContentAlignment
            if anchor == "center":
                self._widget.TextAlignment = ContentAlignment.MiddleCenter
            elif anchor == "w":
                self._widget.TextAlignment = ContentAlignment.MiddleLeft
            elif anchor == "e":
                self._widget.TextAlignment = ContentAlignment.MiddleRight
            elif anchor == "n":
                self._widget.TextAlignment = ContentAlignment.MiddleTop
            elif anchor == "s":
                self._widget.TextAlignment = ContentAlignment.MiddleBottom
            elif anchor == "nw":
                self._widget.TextAlignment = ContentAlignment.TopLeft
            elif anchor == "ne":
                self._widget.TextAlignment = ContentAlignment.TopRight
            elif anchor == "sw":
                self._widget.TextAlignment = ContentAlignment.BottomLeft
            elif anchor == "se":
                self._widget.TextAlignment = ContentAlignment.BottomRight
        try:
            super().configure(**kwargs)
        except:
            pass

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "background":
            return self._widget.BackColor.A, self._widget.BackColor.R, self._widget.BackColor.G, self._widget.BackColor.B
        elif attribute_name == "border_color":
            return self._widget.RectColor.A, self._widget.RectColor.R, self._widget.RectColor.G, self._widget.RectColor.B
        elif attribute_name == "state":
            state = self._widget.Enabled
            if state:
                return "active"
            else:
                return "disabled"
        else:
            return super().cget(attribute_name)

    def font(self, name: str = "Sego UI", size: int = 9):
        try:
            font = Font(name, size)
        except TypeError:
            pass
        else:
            self._widget.Font = font

    def _map(self, _=None):
        self._widget.Visible = True

    def _unmap(self, _=None):
        self._widget.Visible = False

    def _configure_widget(self, _=None):
        from threading import Thread

        def resize():
            self._widget.Location = Point(self.winfo_x(), self.winfo_y())
            self._widget.Size = Size(self.winfo_width(), self.winfo_height())

        Thread(target=resize).run()

    def init(self):
        self._widget = None


class _Base(_Widget):
    def configure(self, **kwargs):
        if "theme" in kwargs:
            self._widget.ThemeName = kwargs.pop("theme").title()
        elif "tooltip" in kwargs:
            print(kwargs.pop("tooltip"))
            self._widget.ButtonElement.ToolTipText = kwargs.pop("tooltip")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "theme":
            return self._widget.ThemeName
        elif attribute_name == "tooltip":
            return self._widget.ButtonElement.ToolTipText
        else:
            return super().cget(attribute_name)


class _Container(_Widget):
    def __init__(self, *args, parent=None, width=500, height=200, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        from tkinter import Frame
        self._page_frame = Frame()
        self.forms_tk(self._widget, self._page_frame)

        def resize(_1, _2=None):
            from threading import Thread

            def show():
                if self._widget.Visible:
                    self._page_frame.place(
                        x=self._widget.Location.X + parent.winfo_x(),
                        y=self._widget.Location.Y,
                        width=self._widget.Size.Width,
                        height=self._widget.Size.Height
                    )
                elif not self._widget.Visible:
                    self._page_frame.place_forget()

            Thread(target=show).run()

        self._widget.VisibleChanged += resize

        self._widget.Resize += resize
        self._widget.Move += resize
        parent.widget().Resize += resize
        parent.widget().Move += resize

    def _init_widget(self):
        self._widget = Panel()

    def frame(self):
        return self._page_frame


FlyRadWidget = _Base
FlyRadFrame = _Container


if __name__ == '__main__':
    from tkinter import Tk, Frame, Button

    root = Tk()
    root.mainloop()
