import os
lib = os.path.dirname(__file__).replace("\\", "//")
telerik_wincontrols_lib = lib + "//Telerik.WinControls.dll"
telerik_wincontrols_ui_lib = lib + "//Telerik.WinControls.UI.dll"
telerik_wincontrols_diagram_lib = lib + "//Telerik.WinControls.RadDiagram.dll"
telerik_wincontrols_syntax_editor_lib = lib + "//Telerik.WinControls.SyntaxEditor.dll"
telerik_wincontrols_themes_win11_lib = lib + "//Telerik.WinControls.Themes.Windows11.dll"
telerik_wincontrols_themes_material_lib = lib + "//Telerik.WinControls.Themes.Material.dll"
telerik_wincontrols_themes_fluent_lib = lib + "//Telerik.WinControls.Themes.Fluent.dll"
telerik_wincontrols_themes_fluent_dark_lib = lib + "//Telerik.WinControls.Themes.FluentDark.dll"
telerik_wincontrols_themes_vs2012_light_lib = lib + "//Telerik.WinControls.Themes.VisualStudio2012Light.dll"
telerik_wincontrols_themes_vs2012_dark_lib = lib + "//Telerik.WinControls.Themes.VisualStudio2012Dark.dll"

telerik_common_lib = lib + "//TelerikCommon.dll"

mscorlib_resources = lib + "//mscorlib.resources.dll"

from tkfly.telerik2.telerik import *