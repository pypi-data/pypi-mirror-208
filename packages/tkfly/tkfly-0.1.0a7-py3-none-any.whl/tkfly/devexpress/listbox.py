from tkfly.devexpress import FlyXtraWidget
import tkinter as tk


class FlyXtraListBox(FlyXtraWidget):
    def __init__(self, *args, width=90, height=130, style: str = "wxi", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(style=style)

    def init(self):
        from tkfly.devexpress import FlyXtraLoadBase
        FlyXtraLoadBase()
        from DevExpress.XtraEditors import ListBoxControl
        self._widget = ListBoxControl()

    def add_item(self, list):
        self._widget.Items.Add(list)

    def add(self, text: str = ""):
        self.add_item(text)

    def selection_index(self, index: int = None):
        if index is not None:
            self._widget.SelectedIndex = index
        else:
            return self._widget.SelectedIndex

    def selection_value(self, value: str = None):
        if value is not None:
            self._widget.SelectedValue = value
        else:
            return self._widget.SelectedValue


if __name__ == '__main__':
    root = tk.Tk()
    listbox = FlyXtraListBox()
    listbox.add("xiangqinxi")
    listbox.add("iloy")
    listbox.selection_value("iloy")
    print(listbox.selection_index())
    print(listbox.selection_value())
    listbox.pack()
    root.mainloop()