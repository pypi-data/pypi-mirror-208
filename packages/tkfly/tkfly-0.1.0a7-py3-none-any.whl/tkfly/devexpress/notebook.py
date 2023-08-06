from tkfly.devexpress import FlyXtraWidget, FlyXtraFrame
import tkinter as tk


class FlyXtraNoteBookTab(FlyXtraFrame):
    def __init__(self, *args, parent=None, width=500, height=200, text: str = "", style: str = "wxi", **kwargs):
        super().__init__(*args, parent=parent, width=width, height=height, **kwargs)
        self.configure(text=text, style=style)

    def init(self):
        from DevExpress.XtraBars.Navigation import TabNavigationPage
        self._widget = TabNavigationPage()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Caption = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Caption
        else:
            return super().cget(attribute_name)


class FlyXtraNoteBook(FlyXtraWidget):
    def __init__(self, *args, width=600, height=300, style: str = "wxi", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(style=style)

    def init(self):
        from tkfly.devexpress import FlyXtraLoadBase
        FlyXtraLoadBase()
        from DevExpress.XtraBars.Navigation import TabPane
        self._widget = TabPane()

    def add_page(self, page):
        self._widget.Pages.Add(page.widget())


if __name__ == '__main__':
    from tkfly import FlyXtraButton
    root = tk.Tk()
    notebook = FlyXtraNoteBook()
    page1 = FlyXtraNoteBookTab(parent=notebook, text="Page1")
    button1 = FlyXtraButton(page1.frame(), text="Button1")
    button1.pack(fill="both", expand="yes", padx=5, pady=(5, 20))
    page2 = FlyXtraNoteBookTab(parent=notebook, text="Page2")
    button2 = FlyXtraButton(page2.frame(), text="Button2")
    button2.pack(fill="both", expand="yes", padx=5, pady=(5, 20))
    notebook.add_page(page1)
    notebook.add_page(page2)
    notebook.pack(fill="both", expand="yes")
    root.mainloop()
