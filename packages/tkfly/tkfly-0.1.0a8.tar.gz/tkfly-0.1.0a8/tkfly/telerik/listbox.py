from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadListBox(FlyRadWidget):
    def __init__(self, *args, width=90, height=130, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadListControl
        self._widget = RadListControl()

    def create_label(self, text=""):
        from Telerik.WinControls.UI import RadListDataItem
        _list = RadListDataItem()
        _list.Text = text
        return _list

    def add_item(self, list):
        self._widget.Items.Add(list)

    def add(self, text: str = ""):
        self.add_item(self.create_label(text=text))

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
    listbox = FlyRadListBox()
    listbox.add("xiangqinxi")
    listbox.add("iloy")
    listbox.selection_value("iloy")
    print(listbox.selection_index())
    print(listbox.selection_value())
    listbox.pack()
    root.mainloop()