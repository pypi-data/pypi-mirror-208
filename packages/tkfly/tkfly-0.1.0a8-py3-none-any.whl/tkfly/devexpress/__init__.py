import tkfly._devexpress
import os

_lib = os.path.dirname(__file__).replace("\\", "//")
xtra_editors_lib = _lib + "//DevExpress.XtraEditors.v22.2.dll"
xtra_bars_lib = _lib + "//DevExpress.XtraBars.v22.2.dll"
xtra_bonus_skins_lib = _lib + "//DevExpress.BonusSkins.v22.2.dll"
xtra_utils_lib = _lib + "//DevExpress.Utils.v22.2.dll"

mscorlib_resources = _lib + "//mscorlib.resources.dll"

from tkfly._devexpress._winform import FlyXtraFrame, FlyXtraWidget

from tkfly.devexpress.imports import base as FlyXtraLoadBase
from tkfly.devexpress.imports import theme as FlyXtraLoadSkin

from tkfly.devexpress.skin import FlyXtraSkin

from tkfly.devexpress.button import FlyXtraButton
from tkfly.devexpress.entry import FlyXtraEntry
from tkfly.devexpress.notebook import FlyXtraNoteBook, FlyXtraNoteBookTab


def launch_vb_demo():
    from os import system
    system(f"{_lib+'//ApplicationUIMainDemo.exe'}")


if __name__ == '__main__':
    FlyXtraLoadBase()
    import DevExpress.XtraEditors
    help(DevExpress.XtraEditors)
    launch_vb_demo()