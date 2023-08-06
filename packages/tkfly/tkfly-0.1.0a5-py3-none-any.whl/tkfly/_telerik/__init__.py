version = "v4.0_2023.1.314.40__5bb2a467cbec794e"

from os import path, mkdir

def init():
    if not path.exists("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls"):
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls\\")
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls\\{version}")
        _ = open(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls\\{version}\\Telerik.WinControls.dll", "wb+")
        from tkfly._telerik._controls_lib import telerik_wincontrols_base64
        _.write(telerik_wincontrols_base64)

    if not path.exists("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.UI"):
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.UI\\")
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.UI\\{version}")
        _ = open(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.UI\\{version}\\Telerik.WinControls.UI.dll", "wb+")
        from tkfly._telerik._controls_ui_lib import telerik_wincontrols_ui_base64
        _.write(telerik_wincontrols_ui_base64)

    if not path.exists("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\TelerikCommon"):
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\TelerikCommon\\")
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\TelerikCommon\\{version}")
        _ = open(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\TelerikCommon\\{version}\\TelerikCommon.dll", "wb+")
        from tkfly._telerik._common import telerik_common_base64
        _.write(telerik_common_base64)

    if not path.exists("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Windows11"):
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Windows11\\")
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Windows11\\{version}")
        _ = open(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Windows11\\{version}\\Telerik.WinControls.Themes.Windows11.dll", "wb+")
        from tkfly._telerik._common import telerik_common_base64

        _.write(telerik_common_base64)

    if not path.exists("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Material"):
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Material\\")
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Material\\{version}")
        _ = open(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Material\\{version}\\Telerik.WinControls.Themes.Material.dll", "wb+")
        from tkfly._telerik._common import telerik_common_base64

        _.write(telerik_common_base64)

    if not path.exists("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Fluent"):
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Fluent\\")
        mkdir(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Fluent\\{version}")
        _ = open(f"C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\Telerik.WinControls.Themes.Fluent\\{version}\\Telerik.WinControls.Themes.Fluent.dll", "wb+")
        from tkfly._telerik._common import telerik_common_base64

        _.write(telerik_common_base64)


init()