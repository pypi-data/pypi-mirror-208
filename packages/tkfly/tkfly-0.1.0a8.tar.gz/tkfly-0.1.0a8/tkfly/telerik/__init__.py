import tkfly._telerik
import os

_lib = os.path.dirname(__file__).replace("\\", "//")
telerik_wincontrols_lib = _lib + "//Telerik.WinControls.dll"
telerik_wincontrols_ui_lib = _lib + "//Telerik.WinControls.UI.dll"
telerik_wincontrols_toast_notification_lib = _lib + "//Telerik.WinControls.RadToastNotification"
telerik_wincontrols_diagram_lib = _lib + "//Telerik.WinControls.RadDiagram.dll"
telerik_wincontrols_syntax_editor_lib = _lib + "//Telerik.WinControls.SyntaxEditor.dll"
telerik_wincontrols_themes_win11_lib = _lib + "//Telerik.WinControls.Themes.Windows11.dll"
telerik_wincontrols_themes_material_lib = _lib + "//Telerik.WinControls.Themes.Material.dll"
telerik_wincontrols_themes_fluent_lib = _lib + "//Telerik.WinControls.Themes.Fluent.dll"
telerik_wincontrols_themes_fluent_dark_lib = _lib + "//Telerik.WinControls.Themes.FluentDark.dll"
telerik_wincontrols_themes_vs2012_light_lib = _lib + "//Telerik.WinControls.Themes.VisualStudio2012Light.dll"
telerik_wincontrols_themes_vs2012_dark_lib = _lib + "//Telerik.WinControls.Themes.VisualStudio2012Dark.dll"

telerik_common_lib = _lib + "//TelerikCommon.dll"

mscorlib_resources = _lib + "//mscorlib.resources.dll"

from tkfly._telerik._winform import FlyRadWidget, FlyRadFrame

from tkfly.telerik.imports import base as FlyRadLoadBase
from tkfly.telerik.imports import theme as FlyRadLoadTheme

from tkfly.telerik.themes import FlyRadThemes, FlyRadWin11Theme, FlyRadFluentTheme, FlyRadFluentDarkTheme, \
    FlyRadMaterialTheme
from tkfly.telerik.button import FlyRadButton
from tkfly.telerik.calculator_dropdown import FlyRadCalculatorDropDown
from tkfly.telerik.calculator import FlyRadCalculator
from tkfly.telerik.calendar import FlyRadCalendar
from tkfly.telerik.clock import FlyRadClock
from tkfly.telerik.desktop_alert import FlyRadDesktopAlert
from tkfly.telerik.elements import FlyRadElement, FlyRadButtonElement, FlyRadTextElement, FlyRadLabelElement
from tkfly.telerik.label import FlyRadLabel
from tkfly.telerik.listbox import FlyRadListBox
from tkfly.telerik.menus import FlyRadMenuItem, FlyRadMenuBar, FlyRadContextMenu
from tkfly.telerik.progressbar import FlyRadProgressBar
from tkfly.telerik.statusbar import FlyRadStatusBar
from tkfly.telerik.taskcards import FlyRadTaskBoard, FlyRadTaskBoardColumnElement, FlyRadTaskCardElement
from tkfly.telerik.text import FlyRadText
from tkfly.telerik.titlebar import FlyRadTitleBar