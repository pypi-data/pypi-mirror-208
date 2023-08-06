from tkfly.devexpress import FlyXtraWidget
import tkinter as tk


class FlyXtraButton(FlyXtraWidget):
    def __init__(self, *args, width=100, height=30, text="", style: str = "wxi", command=None, **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        if command is not None:
            self.bind("<<Click>>", lambda _: command())
        self.configure(text=text, style=style)

    def init(self):
        from tkfly.devexpress import FlyXtraLoadBase
        FlyXtraLoadBase()
        from DevExpress.XtraEditors import SimpleButton
        self._widget = SimpleButton()

    def configure(self, **kwargs):
        if "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)


"""


class SimpleButton(BaseButton)
 |  Void .ctor()
 |  
 |  Method resolution order:
 |      SimpleButton
 |      BaseButton
 |      BaseStyleControl
 |      BaseControl
 |      DevExpress.Utils.Controls.ControlBase
 |      XtraControl
 |      System.Windows.Forms.Control
 |      System.ComponentModel.Component
 |      System.MarshalByRefObject
 |      System.Object
 |      builtins.object
 |  
 |  Methods defined here:
 |  
 |  __eq__(self, value, /)
 |      Return self==value.
 |  
 |  __ge__(self, value, /)
 |      Return self>=value.
 |  
 |  __gt__(self, value, /)
 |      Return self>value.
 |  
 |  __hash__(self, /)
 |      Return hash(self).
 |  
 |  __le__(self, value, /)
 |      Return self<=value.
 |  
 |  __lt__(self, value, /)
 |      Return self<value.
 |  
 |  __ne__(self, value, /)
 |      Return self!=value.
 |  
 |  __repr__(self, /)
 |      Return repr(self).
 |  
 |  __str__(self, /)
 |      Return str(self).
 |  
 |  ----------------------------------------------------------------------
 |  Static methods defined here:
 |  
 |  __new__(*args, **kwargs) from clr._internal.CLRMetatype
 |      Create and return a new object.  See help(type) for accurate signature.
 |  
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |  
 |  AllowFocus
 |  
 |  AllowGlyphSkinning
 |  
 |  AllowHtmlDraw
 |  
 |  AutoSize
 |  
 |  AutoSizeInLayoutControl
 |  
 |  AutoWidthInLayoutControl
 |  
 |  GlyphAlignment
 |  
 |  Image
 |  
 |  ImageAlignment
 |  
 |  ImageHelper
 |  
 |  ImageIndex
 |  
 |  ImageList
 |  
 |  ImageLocation
 |  
 |  ImageOptions
 |  
 |  ImageToTextAlignment
 |  
 |  ImageToTextIndent
 |  
 |  ImageUri
 |  
 |  IsTransparentControl
 |  
 |  ShowFocusRectangle
 |  
 |  SizeableIsCaptionVisible
 |  
 |  Text
 |  
 |  ----------------------------------------------------------------------
 |  Data and other attributes defined here:
 |  
 |  AdjustSize = <unbound method 'AdjustSize'>
 |  
 |  BaseCalcBestSize = <unbound method 'BaseCalcBestSize'>
 |  
 |  CalcBestSize = <unbound method 'CalcBestSize'>
 |  
 |  CalcSizeableMaxSize = <unbound method 'CalcSizeableMaxSize'>
 |  
 |  CalcSizeableMinSize = <unbound method 'CalcSizeableMinSize'>
 |  
 |  CanShowDXSkinColorTabCore = <unbound method 'CanShowDXSkinColorTabCore...
 |  
 |  CreateImageOptions = <unbound method 'CreateImageOptions'>
 |  
 |  CreateViewInfo = <unbound method 'CreateViewInfo'>
 |  
 |  Dispose = <unbound method 'Dispose'>
 |  
 |  DoDpiChangeAfterParent = <unbound method 'DoDpiChangeAfterParent'>
 |  
 |  GetButtonViewInfo = <unbound method 'GetButtonViewInfo'>
 |  
 |  GetPreferredSize = <unbound method 'GetPreferredSize'>
 |  
 |  IsInLink = <unbound method 'IsInLink'>
 |  
 |  LayoutChanged = <unbound method 'LayoutChanged'>
 |  
 |  OnAutoSizeChanged = <unbound method 'OnAutoSizeChanged'>
 |  
 |  OnChangeUICues = <unbound method 'OnChangeUICues'>
 |  
 |  OnHandleCreated = <unbound method 'OnHandleCreated'>
 |  
 |  OnImageAnimation = <unbound method 'OnImageAnimation'>
 |  
 |  OnImageOptionsChanged = <unbound method 'OnImageOptionsChanged'>
 |  
 |  OnPaint = <unbound method 'OnPaint'>
 |  
 |  OnPropertiesChanged = <unbound method 'OnPropertiesChanged'>
 |  
 |  OnTextChanged = <unbound method 'OnTextChanged'>
 |  
 |  Overloads = <unbound method '__init__'>
 |  
 |  ProcessMnemonic = <unbound method 'ProcessMnemonic'>
 |  
 |  StartAnimation = <unbound method 'StartAnimation'>
 |  
 |  StopAnimation = <unbound method 'StopAnimation'>
 |  
 |  UpdateCursor = <unbound method 'UpdateCursor'>
 |  
 |  __init__ = <unbound method '__init__'>
 |  
 |  __overloads__ = <unbound method '__init__'>
 |  
 |  get_AllowFocus = <unbound method 'get_AllowFocus'>
 |  
 |  get_AllowGlyphSkinning = <unbound method 'get_AllowGlyphSkinning'>
 |  
 |  get_AllowHtmlDraw = <unbound method 'get_AllowHtmlDraw'>
 |  
 |  get_AutoSize = <unbound method 'get_AutoSize'>
 |  
 |  get_AutoSizeInLayoutControl = <unbound method 'get_AutoSizeInLayoutCon...
 |  
 |  get_AutoWidthInLayoutControl = <unbound method 'get_AutoWidthInLayoutC...
 |  
 |  get_GlyphAlignment = <unbound method 'get_GlyphAlignment'>
 |  
 |  get_Image = <unbound method 'get_Image'>
 |  
 |  get_ImageAlignment = <unbound method 'get_ImageAlignment'>
 |  
 |  get_ImageHelper = <unbound method 'get_ImageHelper'>
 |  
 |  get_ImageIndex = <unbound method 'get_ImageIndex'>
 |  
 |  get_ImageList = <unbound method 'get_ImageList'>
 |  
 |  get_ImageLocation = <unbound method 'get_ImageLocation'>
 |  
 |  get_ImageOptions = <unbound method 'get_ImageOptions'>
 |  
 |  get_ImageToTextAlignment = <unbound method 'get_ImageToTextAlignment'>
 |  
 |  get_ImageToTextIndent = <unbound method 'get_ImageToTextIndent'>
 |  
 |  get_ImageUri = <unbound method 'get_ImageUri'>
 |  
 |  get_IsTransparentControl = <unbound method 'get_IsTransparentControl'>
 |  
 |  get_ShowFocusRectangle = <unbound method 'get_ShowFocusRectangle'>
 |  
 |  get_SizeableIsCaptionVisible = <unbound method 'get_SizeableIsCaptionV...
 |  
 |  get_Text = <unbound method 'get_Text'>
 |  
 |  set_AllowFocus = <unbound method 'set_AllowFocus'>
 |  
 |  set_AllowGlyphSkinning = <unbound method 'set_AllowGlyphSkinning'>
 |  
 |  set_AllowHtmlDraw = <unbound method 'set_AllowHtmlDraw'>
 |  
 |  set_AutoSize = <unbound method 'set_AutoSize'>
 |  
 |  set_AutoSizeInLayoutControl = <unbound method 'set_AutoSizeInLayoutCon...
 |  
 |  set_AutoWidthInLayoutControl = <unbound method 'set_AutoWidthInLayoutC...
 |  
 |  set_GlyphAlignment = <unbound method 'set_GlyphAlignment'>
 |  
 |  set_Image = <unbound method 'set_Image'>
 |  
 |  set_ImageAlignment = <unbound method 'set_ImageAlignment'>
 |  
 |  set_ImageIndex = <unbound method 'set_ImageIndex'>
 |  
 |  set_ImageList = <unbound method 'set_ImageList'>
 |  
 |  set_ImageLocation = <unbound method 'set_ImageLocation'>
 |  
 |  set_ImageToTextAlignment = <unbound method 'set_ImageToTextAlignment'>
 |  
 |  set_ImageToTextIndent = <unbound method 'set_ImageToTextIndent'>
 |  
 |  set_ImageUri = <unbound method 'set_ImageUri'>
 |  
 |  set_ShowFocusRectangle = <unbound method 'set_ShowFocusRectangle'>
 |  
 |  set_Text = <unbound method 'set_Text'>
 |  


"""


if __name__ == '__main__':
    root = tk.Tk()
    button = FlyXtraButton(text="😺Hello World", style="bezier-cherry-ink")
    button.use_directX()
    button.pack()
    root.mainloop()