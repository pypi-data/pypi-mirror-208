from tkfly.telerik import FlyRadWidget
from tkfly.telerik.elements import FlyRadElement
import tkinter as tk


class FlyRadTaskCardElement(FlyRadElement):
    def __init__(self, title: str = "", description: str = ""):
        super().__init__()
        self.configure(title=title, description=description)

    def init(self):
        from tkfly import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadTaskCardElement
        self._widget = RadTaskCardElement()

    def configure(self, **kwargs):
        if "title" in kwargs:
            self._widget.TitleText = kwargs.pop("title")
        elif "description" in kwargs:
            self._widget.DescriptionText = kwargs.pop("description")

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "title":
            return self._widget.TitleText
        elif attribute_name == "description":
            return self._widget.DescriptionText


class FlyRadTaskBoardColumnElement(FlyRadElement):
    def __init__(self):
        super().__init__()

    def init(self):
        from tkfly import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadTaskBoardColumnElement
        self._widget = RadTaskBoardColumnElement()

    def add_card(self, card: FlyRadTaskCardElement):
        self._widget.TaskCardCollection.AddRange(card.widget())


class FlyRadTaskBoard(FlyRadWidget):
    def __init__(self, *args, width=300, height=425, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

    def init(self):
        from tkfly import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadTaskBoard
        self._widget = RadTaskBoard()

    def add_column(self, column: FlyRadTaskBoardColumnElement):
        self._widget.Columns.AddRange(column.widget())


if __name__ == '__main__':
    root = tk.Tk()
    taskboard = FlyRadTaskBoard()
    taskcolumn = FlyRadTaskBoardColumnElement()
    taskcard = FlyRadTaskCardElement("Hello!")
    taskcolumn.add_card(taskcard)
    taskboard.add_column(taskcolumn)
    taskboard.pack(fill="both", expand="yes")
    root.mainloop()