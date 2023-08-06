import clr
from tkfly.devexpress import xtra_editors_lib, xtra_bars_lib, xtra_bonus_skins_lib, xtra_utils_lib


def base():
    clr.AddReference(xtra_editors_lib)
    clr.AddReference(xtra_bars_lib)

    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Drawing")


def com():
    clr.AddReference(xtra_utils_lib)


def theme():
    clr.AddReference(xtra_bonus_skins_lib)
