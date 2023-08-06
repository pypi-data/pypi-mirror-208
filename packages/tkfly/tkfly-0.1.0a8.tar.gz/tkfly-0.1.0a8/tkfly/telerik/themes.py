class FlyRadTheme(object):
    def __init__(self):
        self.init()

    def widget(self):
        return self._widget


class FlyRadWin11Theme(FlyRadTheme):

    name = "Windows11"

    def init(self):
        from tkfly.telerik import FlyRadLoadTheme
        FlyRadLoadTheme()
        from Telerik.WinControls.Themes import Windows11Theme
        self._widget = Windows11Theme()


class FlyRadFluentTheme(FlyRadTheme):

    name = "Fluent"

    def init(self):
        from tkfly.telerik import FlyRadLoadTheme
        FlyRadLoadTheme()
        from Telerik.WinControls.Themes import FluentTheme
        self._widget = FluentTheme()


class FlyRadFluentDarkTheme(FlyRadTheme):

    name = "FluentDark"

    def init(self):
        from tkfly.telerik import FlyRadLoadTheme
        FlyRadLoadTheme()
        from Telerik.WinControls.Themes import FluentDarkTheme
        self._widget = FluentDarkTheme()


class FlyRadMaterialTheme(FlyRadTheme):

    name = "Material"

    def init(self):
        from tkfly.telerik import FlyRadLoadTheme
        FlyRadLoadTheme()
        from Telerik.WinControls.Themes import MaterialTheme
        self._widget = MaterialTheme()


class FlyRadThemes(object):
    def __init__(self):
        from tkfly.telerik.imports import theme
        theme()

    def win11_theme(self):
        return FlyRadWin11Theme

    def load_win11_theme(self):
        self._win11_theme = self.win11_theme()
