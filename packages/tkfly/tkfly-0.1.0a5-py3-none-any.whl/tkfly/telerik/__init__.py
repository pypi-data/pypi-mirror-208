import tkfly._telerik
import os

_lib = os.path.dirname(__file__).replace("\\", "//")
telerik_wincontrols_lib = _lib + "//Telerik.WinControls.dll"
telerik_wincontrols_ui_lib = _lib + "//Telerik.WinControls.UI.dll"
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

from tkfly._telerik._winform import FlyTKWidget, FlyTKFrame
from tkfly.telerik.imports import base as FlyTKLoadBase
from tkfly.telerik.imports import theme as FlyTKLoadTheme

from tkfly.telerik.themes import FlyTKThemes, FlyTKWin11Theme, FlyTKFluentTheme, FlyTKFluentDarkTheme, \
    FlyTKMaterialTheme
from tkfly.telerik.button import FlyTKButton
from tkfly.telerik.calculator_dropdown import FlyTKCalculatorDropDown
from tkfly.telerik.calculator import FlyTKCalculator
from tkfly.telerik.clock import FlyTKClock
from tkfly.telerik.desktop_alert import FlyTKDesktopAlert
