import clr
from tkfly.devexpress2 import *
clr.AddReference(xtra_editors_lib)
clr.AddReference(xtra_bonus_skins_lib)
clr.AddReference(xtra_bars_lib)

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
from DevExpress.XtraEditors import (SimpleButton, TextEdit, WindowsFormsSettings)
from DevExpress.LookAndFeel import UserLookAndFeel, DefaultLookAndFeel, SkinStyle, SkinSvgPalette
from DevExpress.XtraBars.Navigation import TabPane, TabNavigationPage
from System.Drawing import Point, Size, ContentAlignment
from System.Windows.Forms import CheckState
from tkfly.devexpress2.base import Widget, Container, Page


def use_directX():
    WindowsFormsSettings.ForceDirectXPaint()


class Style(object):
    def userskin(self, style):
        if style == "wxi":
            _style = SkinStyle.WXI
        elif style == "wxi-freshness":
            _style = SkinSvgPalette.WXI.Freshness
        elif style == "wxi-darkness":
            _style = SkinSvgPalette.WXI.Darkness
        elif style == "wxi-clearness":
            _style = SkinSvgPalette.WXI.Clearness
        elif style == "wxi-sharpness":
            _style = SkinSvgPalette.WXI.Sharpness
        elif style == "wxi-calmness":
            _style = SkinSvgPalette.WXI.Calmness
        if style == "wxicompact":
            _style = SkinStyle.WXICompact
        elif style == "wxicompact-freshness":
            _style = SkinSvgPalette.WXICompact.Freshness
        elif style == "wxicompact-darkness":
            _style = SkinSvgPalette.WXICompact.Darkness
        elif style == "wxicompact-clearness":
            _style = SkinSvgPalette.WXICompact.Clearness
        elif style == "wxicompact-sharpness":
            _style = SkinSvgPalette.WXICompact.Sharpness
        elif style == "wxicompact-calmness":
            _style = SkinSvgPalette.WXICompact.Calmness
        UserLookAndFeel.Default.SetSkinStyle(_style)


class Base(Widget):
    def use_directX(self, on: bool = True):
        self._widget.UseDirectXPaint = on


class Button(Base):
    def __init__(self, *args, width=100, height=30, text="DevExpress.Xtra.Button", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def _init_widget(self):
        self._widget = SimpleButton()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)


class Entry(Base):
    def __init__(self, *args, width=100, height=30, text="DevExpress.Xtra.Entry", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def _init_widget(self):
        self._widget = TextEdit()

    def configure(self, **kwargs):
        if "multiline" in kwargs:
            self._widget.Multiline = kwargs.pop("multiline")
        elif "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "multiline":
            return self._widget.Multiline
        elif attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)


class NavigationPage(Page):
    def _init_widget(self):
        self._widget = TabNavigationPage()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Caption = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Caption
        else:
            return super().cget(attribute_name)


class NoteBook(Base):
    def __init__(self, *args, width=600, height=300, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def _init_widget(self):
        self._widget = TabPane()

    def add_page(self, page):
        self._widget.Pages.Add(page.widget())


if __name__ == '__main__':
    from tkinter import Tk, Frame

    root = Tk()
    root.configure(background="white")

    notebook = NoteBook()
    buttons = NavigationPage(parent=notebook)
    buttons.configure(text="Buttons")

    button1 = Button(buttons.frame(), text="button1")
    button1.pack(fill="both", expand="yes", padx=10, pady=10)

    button2 = Button(buttons.frame(), text="button1")
    button2.use_directX(True)
    button2.pack(fill="both", expand="yes", padx=10, pady=10)

    edit = NavigationPage(parent=notebook)
    edit.configure(text="Buttons")

    entry1 = Entry(edit.frame(), text="entry1")
    entry1.pack(fill="both", expand="yes", padx=10, pady=10)

    notebook.add_page(edit)
    notebook.add_page(buttons)

    notebook.pack(fill="both", expand="yes", padx=10, pady=10)

    Style().userskin("wxi")

    root.mainloop()