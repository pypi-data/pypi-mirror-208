import tkinter as tk
import clr
from tkfly.telerik2 import *

clr.AddReference(telerik_wincontrols_lib)
clr.AddReference(telerik_wincontrols_ui_lib)

clr.AddReference(telerik_common_lib)

clr.AddReference(mscorlib_resources)

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
from Telerik.WinControls.UI import (RadSplitButton, RadDirection, RadChat, RibbonTab,
                                    RadRibbonBarGroup, RadButtonElement, RadButtonElement, RadTextBoxElement,
                                    RadTextBox, RadNavigationView, RadPageViewPage, RadClock, RadScrollablePanel,
                                    RadRibbonBar, RadMenu, RadPageView, PageViewMode, RadMenuItem, RadStatusStrip,
                                    RadLabelElement, RadCheckBox, RadRadioButton, RadProgressBar,
                                    RadPropertyGrid, RadOpenFileDialog, RadDesktopAlert, RadCalculatorDropDown)
from System.Drawing import Point, Size, ContentAlignment
from System.Windows.Forms import CheckState
from tkfly.telerik2.base import Widget, Container


PAGEVIEW_STRIP = "strip"
PAGEVIEW_STACK = "stack"


def openfile_dialog():
    _ = RadOpenFileDialog()
    return _.ShowDialog(), _.FileName, _


class Windows11(object):
    def __init__(self):
        self._init_widget()

    def widget(self):
        return self._widget

    def _init_widget(self):
        clr.AddReference(telerik_wincontrols_themes_win11_lib)
        from Telerik.WinControls.Themes import Windows11Theme
        self._widget = Windows11Theme()

    def __str__(self):
        return "Windows11"


class Material(object):
    def __init__(self):
        self._init_widget()

    def widget(self):
        return self._widget

    def _init_widget(self):
        clr.AddReference(telerik_wincontrols_themes_material_lib)
        from Telerik.WinControls.Themes import MaterialTheme
        self._widget = MaterialTheme()


class Fluent(object):
    def __init__(self):
        self._init_widget()

    def widget(self):
        return self._widget

    def _init_widget(self):
        clr.AddReference(telerik_wincontrols_themes_fluent_lib)
        from Telerik.WinControls.Themes import FluentTheme
        self._widget = FluentTheme()


class FluentDark(object):
    def __init__(self):
        self._init_widget()

    def widget(self):
        return self._widget

    def _init_widget(self):
        clr.AddReference(telerik_wincontrols_themes_fluent_dark_lib)
        from Telerik.WinControls.Themes import FluentDarkTheme
        self._widget = FluentDarkTheme()


class VisualStudio2012Light(object):
    def __init__(self):
        self._init_widget()

    def widget(self):
        return self._widget

    def _init_widget(self):
        clr.AddReference(telerik_wincontrols_themes_vs2012_light_lib)
        from Telerik.WinControls.Themes import VisualStudio2012LightTheme
        self._widget = VisualStudio2012LightTheme()


class VisualStudio2012Dark(object):
    def __init__(self):
        self._init_widget()

    def widget(self):
        return self._widget

    def _init_widget(self):
        clr.AddReference(telerik_wincontrols_themes_vs2012_dark_lib)
        from Telerik.WinControls.Themes import VisualStudio2012DarkTheme
        self._widget = VisualStudio2012DarkTheme()


class Base(Widget):
    def configure(self, **kwargs):
        if "theme" in kwargs:
            self._widget.ThemeName = kwargs.pop("theme").title()
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "theme":
            return self._widget.ThemeName
        else:
            return super().cget(attribute_name)


class Element(object):
    def __init__(self):
        self._init_widget()

    def onclick(self, func):
        self._widget.Click += lambda _1, _2: func()

    def ondown(self, func):
        self._widget.MouseDown += lambda _1, _2: func()

    def onup(self, func):
        self._widget.MouseUp += lambda _1, _2: func()

    def _init_widget(self):
        pass

    def widget(self):
        return self._widget

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        elif "anchor" in kwargs:
            anchor = kwargs.pop("anchor")
            from System.Drawing import ContentAlignment
            if anchor == "center":
                self._widget.Alignment = ContentAlignment.MiddleCenter
            elif anchor == "w":
                self._widget.Alignment = ContentAlignment.MiddleLeft
            elif anchor == "e":
                self._widget.Alignment = ContentAlignment.MiddleRight
            elif anchor == "n":
                self._widget.Alignment = ContentAlignment.MiddleTop
            elif anchor == "s":
                self._widget.Alignment = ContentAlignment.MiddleBottom
            elif anchor == "nw":
                self._widget.Alignment = ContentAlignment.TopLeft
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

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text


class BarcodeView(Base):
    def __init__(self, *args, width=100, height=30, value="Telerik.WinControls.BarcodeView", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(value=value)

    def _init_widget(self):
        from Telerik.WinControls.UI.Barcode import RadBarcodeView, QRCode
        self._widget = RadBarcodeView()
        self._qr = QRCode()
        self._qr.Version = 1
        self._widget.Symbology = self._qr

    def configure(self, **kwargs):
        if "value" in kwargs:
            self._widget.Value = kwargs.pop("value")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "value":
            return self._widget.Value
        else:
            return super().cget(attribute_name)


class Button(Base):
    def __init__(self, *args, width=100, height=30, text="Telerik.WinControls.Button", theme="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text, theme=theme)

    def _init_widget(self):
        from Telerik.WinControls.UI import RadButton
        self._widget = RadButton()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)


class Calculator(Base):
    def __init__(self, *args, width=220, height=360, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def _init_widget(self):
        from Telerik.WinControls.UI import RadCalculator
        self._widget = RadCalculator()


class CalculatorDropDown(Button):
    def _init_widget(self):
        self._widget = RadCalculatorDropDown()


class Chat(Base):
    def __init__(self, *args, width=220, height=360, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def _init_widget(self):
        self._widget = RadChat()


class Clock(Base):
    def __init__(self, *args, width=200, height=200, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def _init_widget(self):
        self._widget = RadClock()


class CheckBox(Base):
    def __init__(self, *args, width=100, height=30, text="Telerik.WinControls.CheckBox", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def _init_widget(self):
        self._widget = RadCheckBox()

        def check_state_changed(*args, **kwargs):
            self.event_generate("<<CheckStateChanged>>")

        self._widget.CheckStateChanged += check_state_changed

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        elif "checked" in kwargs:
            self._widget.Checked = kwargs.pop("checked")
        elif "checkstate" in kwargs:
            check_state = kwargs.pop("checkstate")
            if check_state == "indeterminate":
                self._widget.CheckState = CheckState.Indeterminate
            elif check_state == "checked":
                self._widget.CheckState = CheckState.Checked
            elif check_state == "unchecked":
                self._widget.CheckState = CheckState.Unchecked
        elif "checkalign" in kwargs:
            check_align = kwargs.pop("checkalign")
            if check_align == "left":
                self._widget.CheckAlign = ContentAlignment.MiddleLeft
            elif check_align == "right":
                self._widget.CheckAlign = ContentAlignment.MiddleRight
            elif check_align == "top":
                self._widget.CheckState = ContentAlignment.TopCenter
            elif check_align == "bottom":
                self._widget.CheckState = ContentAlignment.BottomCenter
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        elif attribute_name == "checked":
            return self._widget.Checked
        elif attribute_name == "checkstate":
            check_state = self._widget.CheckState
            if check_state == CheckState.Indeterminate:
                return "indeterminate"
            elif check_state == CheckState.Checked:
                return "checked"
            elif check_state == CheckState.Unchecked:
                return "unchecked"
            return
        else:
            return super().cget(attribute_name)


class DesktopAlert(object):
    def __init__(self):
        self._init_widget()

    def _init_widget(self):
        self._widget = RadDesktopAlert()

    def configure(self, **kwargs):
        if "theme" in kwargs:
            self._widget.ThemeName = kwargs.pop("theme").title()
        elif "title" in kwargs:
            self._widget.CaptionText = kwargs.pop("title")
        elif "message" in kwargs:
            self._widget.ContentText = kwargs.pop("message")

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "theme":
            return self._widget.ThemeName
        elif attribute_name == "title":
            return self._widget.CaptionText
        elif attribute_name == "message":
            return self._widget.ContentText

    def widget(self):
        return self._widget

    def show(self):
        self._widget.Show()


class Label(Base):
    def __init__(self, *args, width=100, height=30, text="Telerik.WinControls.Label", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def _init_widget(self):
        from Telerik.WinControls.UI import RadLabel
        self._widget = RadLabel()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)


class ListBox(Base):
    def __init__(self, *args, width=100, height=30, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def _init_widget(self):
        from Telerik.WinControls.UI import RadListControl
        self._widget = RadListControl()

    def create_label(self, text=""):
        from Telerik.WinControls.UI import RadListDataItem
        _list = RadListDataItem()
        _list.Text = text
        return _list

    def add(self, list):
        self._widget.Items.Add(list)


class MenuItem(object):
    def __init__(self, text="Telerik.WinControls.MenuItem"):
        self._init_widget()
        self.configure(text=text)

    def _init_widget(self):
        self._widget = RadMenuItem()

    def widget(self):
        return self._widget

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")

    def add(self, item):
        self._widget.Items.AddRange(item.widget())

    def show(self, x: int, y: int):
        self._widget.Show(x, y)


class MenuBar(Base):
    def __init__(self, *args, width=100, height=30, text="Telerik.WinControls.TitleBar", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def _init_widget(self):
        self._widget = RadMenu()

    def add(self, item):
        self._widget.Items.AddRange(item.widget())


class PageViewPage(Container):
    def _init_widget(self):
        self._widget = RadPageViewPage()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)


class PropertyGrid(Base):
    def __init__(self, *args, width=220, height=360, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def _init_widget(self):
        self._widget = RadPropertyGrid()
        self._widget.ToolbarVisible = True

    def object(self, obj):
        self._widget.SelectedObject = obj


class ProgressBar(Base):
    def __init__(self, *args, width=100, height=25, text="Telerik.WinControls.ProgressBar", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def _init_widget(self):
        self._widget = RadProgressBar()

    def step(self):
        self._widget.PerformStep()

    def configure(self, **kwargs):
        if "value1" in kwargs:
            self._widget.Value1 = kwargs.pop("value1")
        elif "value2" in kwargs:
            self._widget.Value2 = kwargs.pop("value2")
        elif "maximum" in kwargs:
            self._widget.Maximum = kwargs.pop("maximum")
        elif "minimum" in kwargs:
            self._widget.Minimum = kwargs.pop("minimum")
        elif "step" in kwargs:
            self._widget.Step = kwargs.pop("step")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "value1":
            return self._widget.Value1
        elif attribute_name == "value2":
            return self._widget.Value2
        elif attribute_name == "maximum":
            return self._widget.Maximum
        elif attribute_name == "minimum":
            return self._widget.Minimum
        elif attribute_name == "step":
            return self._widget.Step
        else:
            return super().cget(attribute_name)


class PageView(Base):
    def __init__(self, *args, width=600, height=300, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def _init_widget(self):
        self._widget = RadPageView()

    def configure(self, **kwargs):
        if "view" in kwargs:
            view = kwargs.pop("view")
            if view == "strip":
                self._widget.ViewMode = PageViewMode.Strip
            elif view == "stack":
                self._widget.ViewMode = PageViewMode.Stack
            elif view == "outlook":
                self._widget.ViewMode = PageViewMode.Outlook
            elif view == "explorerbar":
                self._widget.ViewMode = PageViewMode.ExplorerBar
            elif view == "backstage":
                self._widget.ViewMode = PageViewMode.Backstage
            elif view == "navigation":
                self._widget.ViewMode = PageViewMode.NavigationView
            elif view == "office_navigation":
                self._widget.ViewMode = PageViewMode.OfficeNavigationBar
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)

    def add_page(self, page: PageViewPage):
        self._widget.Controls.Add(page.widget())


class NavigationView(PageView):
    def _init_widget(self):
        self._widget = RadNavigationView()


class RadioButton(CheckBox):
    def __init__(self, *args, width=100, height=30, text="Telerik.WinControls.RadioButton", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def _init_widget(self):
        self._widget = RadRadioButton()

        def check_state_changed(*args, **kwargs):
            self.event_generate("<<CheckStateChanged>>")

        self._widget.CheckStateChanged += check_state_changed


class TaskCardElement(Element):
    def __init__(self, title: str = "Telerik.WinControls.TaskCardElement", description: str = ""):
        super().__init__()
        self.configure(title=title, description=description)

    def _init_widget(self):
        from Telerik.WinControls.UI import RadTaskCardElement
        self._widget = RadTaskCardElement()

    def configure(self, **kwargs):
        if "title" in kwargs:
            self._widget.TitleText = kwargs.pop("title")
        elif "description" in kwargs:
            self._widget.DescriptionText = kwargs.pop("description")

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "title":
            return self._widget.TitleText
        elif attribute_name == "description":
            return self._widget.DescriptionText


class TaskBoardColumnElement(Element):
    def __init__(self):
        super().__init__()

    def _init_widget(self):
        from Telerik.WinControls.UI import RadTaskBoardColumnElement
        self._widget = RadTaskBoardColumnElement()

    def add_card(self, card: TaskCardElement):
        self._widget.TaskCardCollection.AddRange(card.widget())


class TaskBoard(Base):
    def __init__(self, *args, width=300, height=425, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def _init_widget(self):
        from Telerik.WinControls.UI import RadTaskBoard
        self._widget = RadTaskBoard()

    def add_column(self, column: TaskBoardColumnElement):
        self._widget.Columns.AddRange(column.widget())


class TextBox(Base):
    def __init__(self, *args, width=100, height=30, text="Telerik.WinControls.TextBox", theme="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text, theme=theme)

    def _init_widget(self):
        self._widget = RadTextBox()

    def configure(self, **kwargs):
        if "multiline" in kwargs:
            self._widget.Multiline = kwargs.pop("multiline")
        elif "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        elif "tip_text" in kwargs:
            self._widget.NullText = kwargs.pop("tip_text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "multiline":
            return self._widget.Multiline
        elif attribute_name == "text":
            return self._widget.Text
        elif attribute_name == "tip_text":
            return self._widget.NullText
        else:
            return super().cget(attribute_name)


class LabelElement(Element, Label):
    def __init__(self, text="Telerik.WinControls.LabelElement"):
        super().__init__()
        self.configure(text=text)

    def _init_widget(self):
        self._widget = RadLabelElement()


class ButtonElement(Element, Button):
    def __init__(self, text="Telerik.WinControls.ButtonElement"):
        super().__init__()
        self.configure(text=text)

    def _init_widget(self):
        self._widget = RadButtonElement()


class TextBoxElement(Element, TextBox):
    def __init__(self, text="Telerik.WinControls.TextBoxElement"):
        super().__init__()
        self.configure(text=text)

    def _init_widget(self):
        self._widget = RadTextBoxElement()


class RibbonGroup(object):
    def __init__(self):
        self._init_widget()

    def widget(self):
        return self._widget

    def _init_widget(self):
        self._widget = RadRibbonBarGroup()

    def add(self, item):
        self._widget.Items.AddRange(item.widget())

    def remove(self, item):
        self._widget.Items.Remove(item.widget())

    def clear(self):
        self._widget.Items.Clear()


class RibbonTabbed(object):
    def __init__(self, text="Telerik.WinControls.RibbonTabbed"):
        self._init_widget()
        self.configure(text=text)

    def widget(self):
        return self._widget

    def _init_widget(self):
        self._widget = RibbonTab()

    def add(self, item: RibbonGroup):
        self._widget.Items.AddRange(item.widget())

    def remove(self, item: RibbonGroup):
        self._widget.Items.Remove(item.widget())

    def clear(self):
        self._widget.Items.Clear()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text


class RibbonBar(Base):
    def __init__(self, *args, width=640, height=165, text="Telerik.WinControls.RibbonBar", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)
        self._widget.CloseButton = False
        self._widget.MaximizeButton = False
        self._widget.MinimizeButton = False

    def _init_widget(self):
        self._widget = RadRibbonBar()

    def add(self, item: RibbonTabbed):
        self._widget.CommandTabs.AddRange(item.widget())

    def add_item(self, item):
        self._widget.QuickAccessToolBarItems.AddRange(item.widget())

    def remove(self, item: RibbonTabbed):
        self._widget.CommandTabs.Remove(item.widget())

    def clear(self):
        self._widget.CommandTabs.Clear()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text


class DiagramRibbonBar(RibbonBar):
    def _init_widget(self):
        clr.AddReference(telerik_wincontrols_diagram_lib)
        from Telerik.WinControls.Ui import RadDiagramRibbonBar
        self._widget = RadDiagramRibbonBar()


class TitleBar(Base):
    def __init__(self, *args, width=100, height=30, text="Telerik.WinControls.TitleBar", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def _init_widget(self):
        from Telerik.WinControls.UI import RadTitleBar
        self._widget = RadTitleBar()


class StatusBar(Base):
    def __init__(self, *args, width=300, height=30, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def _init_widget(self):
        self._widget = RadStatusStrip()

    def configure(self, **kwargs):
        if "sizegrip" in kwargs:
            self._widget.SizingGrip = kwargs.pop("sizegrip")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "sizegrip":
            return self._widget.SizingGrip
        else:
            return super().cget(attribute_name)

    def add(self, item: Element):
        self._widget.Items.AddRange(item.widget())


class SyntaxEditor(TextBox):
    def __init__(self, *args, width=100, height=30, text="Telerik.WinControls.SyntaxEditor", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def _init_widget(self):
        clr.AddReference(telerik_wincontrols_syntax_editor_lib)
        from Telerik.WinControls.UI import RadSyntaxEditor
        self._widget = RadSyntaxEditor()


class ScrollablePanel(Base):
    def __init__(self, *args, nav, width=500, height=200, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        from tkinter import Frame
        self._page_frame = Frame()
        self.forms_tk(self._widget, self._page_frame)

        def resize(_1, _2=None):
            from threading import Thread

            def show():
                if self._widget.Visible:
                    self._page_frame.place(
                        x=self._widget.Location.X + nav.winfo_x(),
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
        nav.widget().Resize += resize
        nav.widget().Move += resize

    def _init_widget(self):
        self._widget = RadScrollablePanel()

    def frame(self):
        return self._page_frame


class SplitButton(Button):
    def __init__(self, *args, width=100, height=30, text="Telerik.WinControls.SplitButton", **kwargs):
        Widget.__init__(self, *args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def _init_widget(self):
        self._widget = RadSplitButton()

        def dropdown_opening(*args, **kwargs):
            self.event_generate("<<DropDownOpening>>")

        def dropdown_opened(*args, **kwargs):
            self.event_generate("<<DropDownOpened>>")

        def dropdown_closed(*args, **kwargs):
            self.event_generate("<<DropDownClosed>>")

        self._widget.DropDownOpening += dropdown_opening

        self._widget.DropDownOpened += dropdown_opened

        self._widget.DropDownClosed += dropdown_closed

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        elif "direction" in kwargs:
            direction = kwargs.pop("direction")
            if direction == "up":
                self._widget.DropDownDirection = RadDirection.Up
            elif direction == "down":
                self._widget.DropDownDirection = RadDirection.Down
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)

    def add(self, item):
        self._widget.Items.AddRange(item.widget())


if __name__ == '__main__':
    # 高级示例1
    from tkinter import Tk

    root = Tk()
    theme1 = Material()

    root.mainloop()
