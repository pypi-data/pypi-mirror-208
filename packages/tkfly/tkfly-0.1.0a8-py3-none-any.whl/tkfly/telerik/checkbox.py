from tkfly.telerik import FlyRadWidget
import tkinter as tk


class FlyRadCheckBox(FlyRadWidget):
    def __init__(self, *args, width=100, height=30, text="", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text)

    def init(self):
        from tkfly.telerik import FlyRadLoadBase
        FlyRadLoadBase()
        from Telerik.WinControls.UI import RadCheckBox
        self._widget = RadCheckBox()

        def check_state_changed(*args, **kwargs):
            self.event_generate("<<CheckStateChanged>>")

        self._widget.CheckStateChanged += check_state_changed

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        elif "checked" in kwargs:
            self._widget.Checked = kwargs.pop("checked")
        elif "checkstate" in kwargs:
            check_state = kwargs.pop("checkstate")
            if check_state == "indeterminate":
                self._widget.CheckState = CheckState.Indeterminate
            elif check_state == "checked":
                self._widget.CheckState = CheckState.Checked
            elif check_state == "unchecked":
                self._widget.CheckState = CheckState.Unchecked
        elif "checkalign" in kwargs:
            check_align = kwargs.pop("checkalign")
            if check_align == "left":
                self._widget.CheckAlign = ContentAlignment.MiddleLeft
            elif check_align == "right":
                self._widget.CheckAlign = ContentAlignment.MiddleRight
            elif check_align == "top":
                self._widget.CheckState = ContentAlignment.TopCenter
            elif check_align == "bottom":
                self._widget.CheckState = ContentAlignment.BottomCenter
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        elif attribute_name == "checked":
            return self._widget.Checked
        elif attribute_name == "checkstate":
            check_state = self._widget.CheckState
            if check_state == CheckState.Indeterminate:
                return "indeterminate"
            elif check_state == CheckState.Checked:
                return "checked"
            elif check_state == CheckState.Unchecked:
                return "unchecked"
            return
        else:
            return super().cget(attribute_name)


if __name__ == '__main__':
    root = tk.Tk()
    checkbox = FlyRadCheckBox(text="hello")
    checkbox.pack()
    root.mainloop()