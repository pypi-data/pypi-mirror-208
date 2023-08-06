import clr
from tkfly.telerik import telerik_wincontrols_lib, telerik_wincontrols_ui_lib, telerik_common_lib, mscorlib_resources, \
    telerik_wincontrols_themes_win11_lib, telerik_wincontrols_themes_fluent_lib, telerik_wincontrols_themes_fluent_dark_lib, \
    telerik_wincontrols_themes_material_lib, telerik_wincontrols_toast_notification_lib


def base():
    clr.AddReference(telerik_wincontrols_lib)
    clr.AddReference(telerik_wincontrols_ui_lib)

    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Drawing")


def com():
    clr.AddReference(telerik_common_lib)
    clr.AddReference(mscorlib_resources)


def theme():
    clr.AddReference(telerik_wincontrols_themes_win11_lib)
    clr.AddReference(telerik_wincontrols_themes_fluent_lib)
    clr.AddReference(telerik_wincontrols_themes_fluent_dark_lib)
    clr.AddReference(telerik_wincontrols_themes_material_lib)


def toast_notification():
    clr.AddReference(telerik_wincontrols_toast_notification_lib)
