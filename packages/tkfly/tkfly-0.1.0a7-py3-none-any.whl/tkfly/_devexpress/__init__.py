version = "v4.0_22.2.4.0__b88d1754d700e49a"

from os import path, mkdir


def init():
    if not path.exists("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.BonusSkins.v22.2"):
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.BonusSkins.v22.2\\")
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.BonusSkins.v22.2\\{version}")
        _ = open(
            f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.BonusSkins.v22.2\\{version}\\DevExpress.BonusSkins.v22.2.dll",
            "wb+")
        from tkfly._devexpress._skins_lib import devexpress_bonus_skins_base64
        _.write(devexpress_bonus_skins_base64)

    if not path.exists("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.XtraEditors.v22.2"):
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.XtraEditors.v22.2\\")
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.XtraEditors.v22.2\\{version}")
        _ = open(
            f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.XtraEditors.v22.2\\{version}\\DevExpress.XtraEditors.v22.2.dll",
            "wb+")
        from tkfly._devexpress._controls_lib import devexpress_xtra_editors_base64
        _.write(devexpress_xtra_editors_base64)

    if not path.exists("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.XtraBars.v22.2"):
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.XtraBars.v22.2\\")
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.XtraBars.v22.2\\{version}")
        _ = open(
            f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\DevExpress.XtraBars.v22.2\\{version}\\DevExpress.XtraBars.v22.2.dll",
            "wb+")
        from tkfly._devexpress._controls2_lib import devexpress_xtra_bars_base64
        _.write(devexpress_xtra_bars_base64)


init()
