class FlyTKTheme(object):
    def __init__(self):
        self.init()

    def widget(self):
        return self._widget


class FlyTKWin11Theme(FlyTKTheme):

    name = "Windows11"

    def init(self):
        from tkfly.telerik import FlyTKLoadTheme
        FlyTKLoadTheme()
        from Telerik.WinControls.Themes import Windows11Theme
        self._widget = Windows11Theme()


class FlyTKFluentTheme(FlyTKTheme):

    name = "Fluent"

    def init(self):
        from tkfly.telerik import FlyTKLoadTheme
        FlyTKLoadTheme()
        from Telerik.WinControls.Themes import FluentTheme
        self._widget = FluentTheme()


class FlyTKFluentDarkTheme(FlyTKTheme):

    name = "FluentDark"

    def init(self):
        from tkfly.telerik import FlyTKLoadTheme
        FlyTKLoadTheme()
        from Telerik.WinControls.Themes import FluentDarkTheme
        self._widget = FluentDarkTheme()


class FlyTKMaterialTheme(FlyTKTheme):

    name = "Material"

    def init(self):
        from tkfly.telerik import FlyTKLoadTheme
        FlyTKLoadTheme()
        from Telerik.WinControls.Themes import MaterialTheme
        self._widget = MaterialTheme()


class FlyTKThemes(object):
    def __init__(self):
        from tkfly.telerik.imports import theme
        theme()

    def win11_theme(self):
        return FlyTKWin11Theme

    def load_win11_theme(self):
        self._win11_theme = self.win11_theme()
