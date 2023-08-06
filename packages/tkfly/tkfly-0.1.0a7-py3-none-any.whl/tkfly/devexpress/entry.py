from tkfly.devexpress import FlyXtraWidget
import tkinter as tk


class FlyXtraEntry(FlyXtraWidget):
    def __init__(self, *args, width=100, height=30, text="", style: str = "wxi", **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)
        self.configure(text=text, style=style)

    def init(self):
        from tkfly.devexpress import FlyXtraLoadBase
        FlyXtraLoadBase()
        from DevExpress.XtraEditors import TextEdit
        self._widget = TextEdit()

    def configure(self, **kwargs):
        if "multiline" in kwargs:
            self._widget.Multiline = kwargs.pop("multiline")
        elif "text" in kwargs:
            self._widget.Text = kwargs.pop("text")
        super().configure(**kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "multiline":
            return self._widget.Multiline
        elif attribute_name == "text":
            return self._widget.Text
        else:
            return super().cget(attribute_name)

    def advanced_label(self, text: str = None):
        if text is not None:
            self._widget.Properties.AdvancedModeOptions.Label = text
        else:
            return self._widget.Properties.AdvancedModeOptions.Label

"""
class TextEdit(BaseEdit)
 |  Void .ctor()
 |  
 |  Method resolution order:
 |      TextEdit
 |      BaseEdit
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
 |  AcceptsReturn
 |  
 |  AcceptsSpace
 |  
 |  AcceptsTab
 |  
 |  AdvancedMode
 |  
 |  AllowEmptyStringToNullValue
 |  
 |  AllowPaintBackground
 |  
 |  AllowSmartMouseWheel
 |  
 |  AllowTransparency
 |  
 |  AllowValidateOnEnterKey
 |  
 |  BackColor
 |  
 |  BackgroundImage
 |  
 |  BackgroundImageLayout
 |  
 |  CanTabStop
 |  
 |  CanUndo
 |  
 |  CreateParams
 |  
 |  CustomHighlightText
 |  
 |  CustomTextLineHeight
 |  
 |  CustomizeAutoCompleteSource
 |  
 |  DXAccessible
 |  
 |  DefaultCursor
 |  
 |  DefaultSize
 |  
 |  EditorTypeName
 |  
 |  InnerControl
 |  
 |  IsAllowMaskBoxPropertiesUpdate
 |  
 |  IsEditorActive
 |  
 |  IsExistsNullValuePrompt
 |  
 |  IsMaskBoxAvailable
 |  
 |  IsMaskBoxUpdate
 |  
 |  IsMatch
 |  
 |  IsNeedFocus
 |  
 |  IsNullValuePromptVisible
 |  
 |  IsWindowsXPStyle
 |  
 |  MaskBox
 |  
 |  MaskBoxInternal
 |  
 |  Menu
 |  
 |  MouseHere
 |  
 |  PaintEx
 |  
 |  Properties
 |  
 |  QueryAdvancedMode
 |  
 |  SelectedText
 |  
 |  SelectionLength
 |  
 |  SelectionStart
 |  
 |  Spin
 |  
 |  TabStop
 |  
 |  Text
 |  
 |  UseParentOnTransparentPaintBackground
 |  
 |  ViewInfo
 |  
 |  WorkingStrategy
 |  
 |  ----------------------------------------------------------------------
 |  Data and other attributes defined here:
 |  
 |  AccessibilityNotifyTextChanged = <unbound method 'AccessibilityNotifyT...
 |  
 |  AdvTextEditWorkingStrategy = <class 'DevExpress.XtraEditors.AdvTextEdi...
 |      Void .ctor(DevExpress.XtraEditors.TextEdit)
 |  
 |  
 |  AppendText = <unbound method 'AppendText'>
 |  
 |  BaseEditWndProc = <unbound method 'BaseEditWndProc'>
 |  
 |  BeginInternalTextChange = <unbound method 'BeginInternalTextChange'>
 |  
 |  Block = <class 'DevExpress.XtraEditors.Block'>
 |      Void .ctor(Int32, Int32)
 |  
 |  
 |  CalcSizeableMaxSize = <unbound method 'CalcSizeableMaxSize'>
 |  
 |  CalcSizeableMinSize = <unbound method 'CalcSizeableMinSize'>
 |  
 |  CheckIfNullString = <unbound method 'CheckIfNullString'>
 |  
 |  CheckMouseHere = <unbound method 'CheckMouseHere'>
 |  
 |  Clear = <unbound method 'Clear'>
 |  
 |  CompareFonts = <unbound method 'CompareFonts'>
 |  
 |  Copy = <unbound method 'Copy'>
 |  
 |  CreateAdvancedStrategy = <unbound method 'CreateAdvancedStrategy'>
 |  
 |  CreateEditController = <unbound method 'CreateEditController'>
 |  
 |  CreateEditControllerInstance = <unbound method 'CreateEditControllerIn...
 |  
 |  CreateMaskBox = <unbound method 'CreateMaskBox'>
 |  
 |  CreateMaskBoxInstance = <unbound method 'CreateMaskBoxInstance'>
 |  
 |  CreateMaskManager = <unbound method 'CreateMaskManager'>
 |  
 |  CreateMenu = <unbound method 'CreateMenu'>
 |  
 |  Cut = <unbound method 'Cut'>
 |  
 |  DXMenuItemTextEdit = <class 'DevExpress.XtraEditors.DXMenuItemTextEdit...
 |      Void .ctor(DevExpress.XtraEditors.Controls.StringId, System.EventHandler, System.Drawing.Image)
 |      Void .ctor(DevExpress.XtraEditors.Controls.StringId, System.EventHandler, System.Drawing.Image, DevExpress.Utils.Svg.SvgImage)
 |  
 |  
 |  DeselectAll = <unbound method 'DeselectAll'>
 |  
 |  DestroyMaskBox = <unbound method 'DestroyMaskBox'>
 |  
 |  Dispose = <unbound method 'Dispose'>
 |  
 |  DoDpiChange = <unbound method 'DoDpiChange'>
 |  
 |  DoIsMatchValidating = <unbound method 'DoIsMatchValidating'>
 |  
 |  DoNullInputKeysCore = <unbound method 'DoNullInputKeysCore'>
 |  
 |  DoSpin = <unbound method 'DoSpin'>
 |  
 |  EndInternalTextChange = <unbound method 'EndInternalTextChange'>
 |  
 |  EnsureInnerEditorFocused = <unbound method 'EnsureInnerEditorFocused'>
 |  
 |  ExecInnerEditMouseDown = <unbound method 'ExecInnerEditMouseDown'>
 |  
 |  FireSpinRequest = <unbound method 'FireSpinRequest'>
 |  
 |  FlushPendingEditActions = <unbound method 'FlushPendingEditActions'>
 |  
 |  GetAccessibilityObjectById = <unbound method 'GetAccessibilityObjectBy...
 |  
 |  GetAccessibleToNotify = <unbound method 'GetAccessibleToNotify'>
 |  
 |  GetCharFromPosition = <unbound method 'GetCharFromPosition'>
 |  
 |  GetCharIndexFromPosition = <unbound method 'GetCharIndexFromPosition'>
 |  
 |  GetFirstCharIndexFromLine = <unbound method 'GetFirstCharIndexFromLine...
 |  
 |  GetFirstCharIndexOfCurrentLine = <unbound method 'GetFirstCharIndexOfC...
 |  
 |  GetLineFromCharIndex = <unbound method 'GetLineFromCharIndex'>
 |  
 |  GetPositionFromCharIndex = <unbound method 'GetPositionFromCharIndex'>
 |  
 |  HideCaret = <unbound method 'HideCaret'>
 |  
 |  InnerEditorPaste = <unbound method 'InnerEditorPaste'>
 |  
 |  InnerEditorSpin = <unbound method 'InnerEditorSpin'>
 |  
 |  IsInnerEditorReadOnly = <unbound method 'IsInnerEditorReadOnly'>
 |  
 |  IsInputChar = <unbound method 'IsInputChar'>
 |  
 |  IsInputKey = <unbound method 'IsInputKey'>
 |  
 |  IsNeededCursorKey = <unbound method 'IsNeededCursorKey'>
 |  
 |  IsNeededExtraKey = <unbound method 'IsNeededExtraKey'>
 |  
 |  IsShowNullValuePrompt = <unbound method 'IsShowNullValuePrompt'>
 |  
 |  IsTextCommand = <unbound method 'IsTextCommand'>
 |  
 |  LayoutChanged = <unbound method 'LayoutChanged'>
 |  
 |  LayoutChangedCore = <unbound method 'LayoutChangedCore'>
 |  
 |  LockMaskBoxPropertiesUpdate = <unbound method 'LockMaskBoxPropertiesUp...
 |  
 |  MaskBoxGetEditValue = <unbound method 'MaskBoxGetEditValue'>
 |  
 |  MenuItemUpdateElement = <class 'DevExpress.XtraEditors.MenuItemUpdateE...
 |      Void .ctor(DXMenuItemTextEdit, MenuItemUpdateHandler)
 |  
 |  
 |  MenuItemUpdateHandler = <class 'DevExpress.XtraEditors.MenuItemUpdateH...
 |  
 |  NeedLayoutUpdateValidating = <unbound method 'NeedLayoutUpdateValidati...
 |  
 |  OnAfterUpdateViewInfo = <unbound method 'OnAfterUpdateViewInfo'>
 |  
 |  OnAppearancePaintChanged = <unbound method 'OnAppearancePaintChanged'>
 |  
 |  OnBeforeUpdateViewInfo = <unbound method 'OnBeforeUpdateViewInfo'>
 |  
 |  OnClientSizeChanged = <unbound method 'OnClientSizeChanged'>
 |  
 |  OnControllerValueChanged = <unbound method 'OnControllerValueChanged'>
 |  
 |  OnControllerValueChanging = <unbound method 'OnControllerValueChanging...
 |  
 |  OnCreateControl = <unbound method 'OnCreateControl'>
 |  
 |  OnEditValueChanged = <unbound method 'OnEditValueChanged'>
 |  
 |  OnEditValueChanging = <unbound method 'OnEditValueChanging'>
 |  
 |  OnEditorEnter = <unbound method 'OnEditorEnter'>
 |  
 |  OnEditorKeyDown = <unbound method 'OnEditorKeyDown'>
 |  
 |  OnEditorKeyDownProcessNullInputKeys = <unbound method 'OnEditorKeyDown...
 |  
 |  OnEditorKeyPress = <unbound method 'OnEditorKeyPress'>
 |  
 |  OnEditorLeave = <unbound method 'OnEditorLeave'>
 |  
 |  OnEnableNonMaskedInput = <unbound method 'OnEnableNonMaskedInput'>
 |  
 |  OnEnabledChanged = <unbound method 'OnEnabledChanged'>
 |  
 |  OnEndIme = <unbound method 'OnEndIme'>
 |  
 |  OnEnter = <unbound method 'OnEnter'>
 |  
 |  OnGlassMaskBoxPreWndProc = <unbound method 'OnGlassMaskBoxPreWndProc'>
 |  
 |  OnGlassMaskBoxWndProc = <unbound method 'OnGlassMaskBoxWndProc'>
 |  
 |  OnGotFocus = <unbound method 'OnGotFocus'>
 |  
 |  OnHandleCreated = <unbound method 'OnHandleCreated'>
 |  
 |  OnHandleDestroyed = <unbound method 'OnHandleDestroyed'>
 |  
 |  OnImeModeChanged = <unbound method 'OnImeModeChanged'>
 |  
 |  OnKeyDown = <unbound method 'OnKeyDown'>
 |  
 |  OnKeyPress = <unbound method 'OnKeyPress'>
 |  
 |  OnKeyUp = <unbound method 'OnKeyUp'>
 |  
 |  OnLeave = <unbound method 'OnLeave'>
 |  
 |  OnLoaded = <unbound method 'OnLoaded'>
 |  
 |  OnLookAndFeelChanged = <unbound method 'OnLookAndFeelChanged'>
 |  
 |  OnLostFocus = <unbound method 'OnLostFocus'>
 |  
 |  OnMaskBoxMouseSelection = <unbound method 'OnMaskBoxMouseSelection'>
 |  
 |  OnMaskBoxPreWndProc = <unbound method 'OnMaskBoxPreWndProc'>
 |  
 |  OnMaskBoxTextResetToNullValuePromptOrNullText = <unbound method 'OnMas...
 |  
 |  OnMaskBoxWndProc = <unbound method 'OnMaskBoxWndProc'>
 |  
 |  OnMaskBox_Click = <unbound method 'OnMaskBox_Click'>
 |  
 |  OnMaskBox_DoubleClick = <unbound method 'OnMaskBox_DoubleClick'>
 |  
 |  OnMaskBox_GotFocus = <unbound method 'OnMaskBox_GotFocus'>
 |  
 |  OnMaskBox_KeyDown = <unbound method 'OnMaskBox_KeyDown'>
 |  
 |  OnMaskBox_KeyPress = <unbound method 'OnMaskBox_KeyPress'>
 |  
 |  OnMaskBox_KeyUp = <unbound method 'OnMaskBox_KeyUp'>
 |  
 |  OnMaskBox_LostFocus = <unbound method 'OnMaskBox_LostFocus'>
 |  
 |  OnMaskBox_MouseDown = <unbound method 'OnMaskBox_MouseDown'>
 |  
 |  OnMaskBox_MouseEnter = <unbound method 'OnMaskBox_MouseEnter'>
 |  
 |  OnMaskBox_MouseLeave = <unbound method 'OnMaskBox_MouseLeave'>
 |  
 |  OnMaskBox_MouseMove = <unbound method 'OnMaskBox_MouseMove'>
 |  
 |  OnMaskBox_MouseUp = <unbound method 'OnMaskBox_MouseUp'>
 |  
 |  OnMaskBox_MouseWheel = <unbound method 'OnMaskBox_MouseWheel'>
 |  
 |  OnMaskBox_TextValidated = <unbound method 'OnMaskBox_TextValidated'>
 |  
 |  OnMaskBox_ValueChanged = <unbound method 'OnMaskBox_ValueChanged'>
 |  
 |  OnMaskBox_ValueChanging = <unbound method 'OnMaskBox_ValueChanging'>
 |  
 |  OnMouseDown = <unbound method 'OnMouseDown'>
 |  
 |  OnMouseEnter = <unbound method 'OnMouseEnter'>
 |  
 |  OnMouseLeave = <unbound method 'OnMouseLeave'>
 |  
 |  OnMouseMove = <unbound method 'OnMouseMove'>
 |  
 |  OnMouseUp = <unbound method 'OnMouseUp'>
 |  
 |  OnMouseWheel = <unbound method 'OnMouseWheel'>
 |  
 |  OnPaint = <unbound method 'OnPaint'>
 |  
 |  OnPaintBackground = <unbound method 'OnPaintBackground'>
 |  
 |  OnPreviewKeyDown = <unbound method 'OnPreviewKeyDown'>
 |  
 |  OnPropertiesChanged = <unbound method 'OnPropertiesChanged'>
 |  
 |  OnResize = <unbound method 'OnResize'>
 |  
 |  OnSizeChanged = <unbound method 'OnSizeChanged'>
 |  
 |  OnSpin = <unbound method 'OnSpin'>
 |  
 |  OnStyleControllerChanged = <unbound method 'OnStyleControllerChanged'>
 |  
 |  OnTabStopChanged = <unbound method 'OnTabStopChanged'>
 |  
 |  OnTextChanged = <unbound method 'OnTextChanged'>
 |  
 |  OnTextEditPropertiesChanged = <unbound method 'OnTextEditPropertiesCha...
 |  
 |  OnValidated = <unbound method 'OnValidated'>
 |  
 |  OnValidating = <unbound method 'OnValidating'>
 |  
 |  Overloads = <unbound method '__init__'>
 |  
 |  PaintErrorIconBackground = <unbound method 'PaintErrorIconBackground'>
 |  
 |  Paste = <unbound method 'Paste'>
 |  
 |  PendingEditActionPerformed = <unbound method 'PendingEditActionPerform...
 |  
 |  ProcessCmdKey = <unbound method 'ProcessCmdKey'>
 |  
 |  ProcessDialogKey = <unbound method 'ProcessDialogKey'>
 |  
 |  ProcessDialogKeyCore = <unbound method 'ProcessDialogKeyCore'>
 |  
 |  ProcessRemoveWord = <unbound method 'ProcessRemoveWord'>
 |  
 |  QueryAdvancedModeEventArgs = <class 'DevExpress.XtraEditors.QueryAdvan...
 |      Python wrapper for .NET type DevExpress.XtraEditors.TextEdit+QueryAdvancedModeEventArgs
 |  
 |  
 |  QueryEditorModeFromSkin = <unbound method 'QueryEditorModeFromSkin'>
 |  
 |  RaisePaintEvent = <unbound method 'RaisePaintEvent'>
 |  
 |  RaisePaintExEvent = <unbound method 'RaisePaintExEvent'>
 |  
 |  RaiseQueryAdvancedMode = <unbound method 'RaiseQueryAdvancedMode'>
 |  
 |  RaiseQueryCompletion = <unbound method 'RaiseQueryCompletion'>
 |  
 |  RefreshEnabledState = <unbound method 'RefreshEnabledState'>
 |  
 |  Reset = <unbound method 'Reset'>
 |  
 |  ResetSelection = <unbound method 'ResetSelection'>
 |  
 |  ScaleFont = <unbound method 'ScaleFont'>
 |  
 |  ScrollToCaret = <unbound method 'ScrollToCaret'>
 |  
 |  Segment = <class 'DevExpress.XtraEditors.Segment'>
 |      Void .ctor()
 |  
 |  
 |  Select = <unbound method 'Select'>
 |  
 |  SelectAll = <unbound method 'SelectAll'>
 |  
 |  SetTextCore = <unbound method 'SetTextCore'>
 |  
 |  ShouldSuppressFormDeactivation = <unbound method 'ShouldSuppressFormDe...
 |  
 |  ShowCaret = <unbound method 'ShowCaret'>
 |  
 |  ShowMenu = <unbound method 'ShowMenu'>
 |  
 |  ShowMenuCore = <unbound method 'ShowMenuCore'>
 |  
 |  SwitchModeAccordingToSkinSettings = <unbound method 'SwitchModeAccordi...
 |  
 |  TextEditBlockPainter = <class 'DevExpress.XtraEditors.TextEditBlockPai...
 |      Void .ctor()
 |  
 |  
 |  TextEditWorkingStrategy = <class 'DevExpress.XtraEditors.TextEditWorki...
 |      Void .ctor(DevExpress.XtraEditors.TextEdit)
 |  
 |  
 |  Undo = <unbound method 'Undo'>
 |  
 |  UnlockMaskBoxPropertiesUpdate = <unbound method 'UnlockMaskBoxProperti...
 |  
 |  UpdateDisplayText = <unbound method 'UpdateDisplayText'>
 |  
 |  UpdateEditControllerProperties = <unbound method 'UpdateEditController...
 |  
 |  UpdateHideSelection = <unbound method 'UpdateHideSelection'>
 |  
 |  UpdateInactiveInnerEditorProperties = <unbound method 'UpdateInactiveI...
 |  
 |  UpdateMaskBox = <unbound method 'UpdateMaskBox'>
 |  
 |  UpdateMaskBoxBounds = <unbound method 'UpdateMaskBoxBounds'>
 |  
 |  UpdateMaskBoxDisplayText = <unbound method 'UpdateMaskBoxDisplayText'>
 |  
 |  UpdateMaskBoxFontByScaleDpi = <unbound method 'UpdateMaskBoxFontByScal...
 |  
 |  UpdateMaskBoxProperties = <unbound method 'UpdateMaskBoxProperties'>
 |  
 |  UpdateMaskBoxPropertiesCore = <unbound method 'UpdateMaskBoxProperties...
 |  
 |  UpdateMenu = <unbound method 'UpdateMenu'>
 |  
 |  UpdateMenuCoords = <unbound method 'UpdateMenuCoords'>
 |  
 |  UpdatePasswordChar = <unbound method 'UpdatePasswordChar'>
 |  
 |  UpdateTextHighlight = <unbound method 'UpdateTextHighlight'>
 |  
 |  WndProc = <unbound method 'WndProc'>
 |  
 |  __init__ = <unbound method '__init__'>
 |  
 |  __overloads__ = <unbound method '__init__'>
 |  
 |  add_CustomHighlightText = <unbound method 'add_CustomHighlightText'>
 |  
 |  add_CustomTextLineHeight = <unbound method 'add_CustomTextLineHeight'>
 |  
 |  add_CustomizeAutoCompleteSource = <unbound method 'add_CustomizeAutoCo...
 |  
 |  add_PaintEx = <unbound method 'add_PaintEx'>
 |  
 |  add_QueryAdvancedMode = <unbound method 'add_QueryAdvancedMode'>
 |  
 |  add_Spin = <unbound method 'add_Spin'>
 |  
 |  get_AcceptsReturn = <unbound method 'get_AcceptsReturn'>
 |  
 |  get_AcceptsSpace = <unbound method 'get_AcceptsSpace'>
 |  
 |  get_AcceptsTab = <unbound method 'get_AcceptsTab'>
 |  
 |  get_AdvancedMode = <unbound method 'get_AdvancedMode'>
 |  
 |  get_AllowEmptyStringToNullValue = <unbound method 'get_AllowEmptyStrin...
 |  
 |  get_AllowPaintBackground = <unbound method 'get_AllowPaintBackground'>
 |  
 |  get_AllowSmartMouseWheel = <unbound method 'get_AllowSmartMouseWheel'>
 |  
 |  get_AllowTransparency = <unbound method 'get_AllowTransparency'>
 |  
 |  get_AllowValidateOnEnterKey = <unbound method 'get_AllowValidateOnEnte...
 |  
 |  get_BackColor = <unbound method 'get_BackColor'>
 |  
 |  get_BackgroundImage = <unbound method 'get_BackgroundImage'>
 |  
 |  get_BackgroundImageLayout = <unbound method 'get_BackgroundImageLayout...
 |  
 |  get_CanTabStop = <unbound method 'get_CanTabStop'>
 |  
 |  get_CanUndo = <unbound method 'get_CanUndo'>
 |  
 |  get_CreateParams = <unbound method 'get_CreateParams'>
 |  
 |  get_DXAccessible = <unbound method 'get_DXAccessible'>
 |  
 |  get_DefaultCursor = <unbound method 'get_DefaultCursor'>
 |  
 |  get_DefaultSize = <unbound method 'get_DefaultSize'>
 |  
 |  get_EditorTypeName = <unbound method 'get_EditorTypeName'>
 |  
 |  get_InnerControl = <unbound method 'get_InnerControl'>
 |  
 |  get_IsAllowMaskBoxPropertiesUpdate = <unbound method 'get_IsAllowMaskB...
 |  
 |  get_IsEditorActive = <unbound method 'get_IsEditorActive'>
 |  
 |  get_IsExistsNullValuePrompt = <unbound method 'get_IsExistsNullValuePr...
 |  
 |  get_IsMaskBoxAvailable = <unbound method 'get_IsMaskBoxAvailable'>
 |  
 |  get_IsMaskBoxUpdate = <unbound method 'get_IsMaskBoxUpdate'>
 |  
 |  get_IsMatch = <unbound method 'get_IsMatch'>
 |  
 |  get_IsNeedFocus = <unbound method 'get_IsNeedFocus'>
 |  
 |  get_IsNullValuePromptVisible = <unbound method 'get_IsNullValuePromptV...
 |  
 |  get_IsWindowsXPStyle = <unbound method 'get_IsWindowsXPStyle'>
 |  
 |  get_MaskBox = <unbound method 'get_MaskBox'>
 |  
 |  get_MaskBoxInternal = <unbound method 'get_MaskBoxInternal'>
 |  
 |  get_Menu = <unbound method 'get_Menu'>
 |  
 |  get_MouseHere = <unbound method 'get_MouseHere'>
 |  
 |  get_Properties = <unbound method 'get_Properties'>
 |  
 |  get_SelectedText = <unbound method 'get_SelectedText'>
 |  
 |  get_SelectionLength = <unbound method 'get_SelectionLength'>
 |  
 |  get_SelectionStart = <unbound method 'get_SelectionStart'>
 |  
 |  get_TabStop = <unbound method 'get_TabStop'>
 |  
 |  get_Text = <unbound method 'get_Text'>
 |  
 |  get_UseParentOnTransparentPaintBackground = <unbound method 'get_UsePa...
 |  
 |  get_ViewInfo = <unbound method 'get_ViewInfo'>
 |  
 |  get_WorkingStrategy = <unbound method 'get_WorkingStrategy'>
 |  
 |  remove_CustomHighlightText = <unbound method 'remove_CustomHighlightTe...
 |  
 |  remove_CustomTextLineHeight = <unbound method 'remove_CustomTextLineHe...
 |  
 |  remove_CustomizeAutoCompleteSource = <unbound method 'remove_Customize...
 |  
 |  remove_PaintEx = <unbound method 'remove_PaintEx'>
 |  
 |  remove_QueryAdvancedMode = <unbound method 'remove_QueryAdvancedMode'>
 |  
 |  remove_Spin = <unbound method 'remove_Spin'>
 |  
 |  set_AllowTransparency = <unbound method 'set_AllowTransparency'>
 |  
 |  set_BackColor = <unbound method 'set_BackColor'>
 |  
 |  set_BackgroundImage = <unbound method 'set_BackgroundImage'>
 |  
 |  set_BackgroundImageLayout = <unbound method 'set_BackgroundImageLayout...
 |  
 |  set_MouseHere = <unbound method 'set_MouseHere'>
 |  
 |  set_SelectedText = <unbound method 'set_SelectedText'>
 |  
 |  set_SelectionLength = <unbound method 'set_SelectionLength'>
 |  
 |  set_SelectionStart = <unbound method 'set_SelectionStart'>
 |  
 |  set_TabStop = <unbound method 'set_TabStop'>
 |  
 |  set_Text = <unbound method 'set_Text'>
 |  
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited from BaseEdit:
 |  
 |  AccessibleDefaultActionDescription
 |  
 |  AccessibleDescription
 |  
 |  AccessibleName
 |  
 |  AccessibleRole
 |  
 |  AdvancedAutoWidthInLayoutControl
 |  
 |  AllowFireEditValueChanged
 |  
 |  AllowUpdateIsModifiedOnValueChanging
 |  
 |  BackColorChanged
 |  
 |  BindingManager
 |  
 |  BorderStyle
 |  
 |  CanShowDialog
 |  
 |  ContextMenu
 |  
 |  ContextMenuStrip
 |  
 |  CustomDisplayText
 |  
 |  EditValue
 |  
 |  EditValueChanged
 |  
 |  EditValueChanging
 |  
 |  EditValueDataBindingType
 |  
 |  EditViewInfo
 |  
 |  EditorClassInfo
 |  
 |  EditorContainer
 |  
 |  EditorContainsFocus
 |  
 |  EnterMoveNextControl
 |  
 |  ErrorIcon
 |  
 |  ErrorIconAlignment
 |  
 |  ErrorImageOptions
 |  
 |  ErrorText
 |  
 |  EventSender
 |  
 |  Font
 |  
 |  FontChanged
 |  
 |  ForeColor
 |  
 |  ForeColorChanged
 |  
 |  FormatEditValue
 |  
 |  InplaceType
 |  
 |  InvalidValue
 |  
 |  IsAcceptingEditValue
 |  
 |  IsAllowValidate
 |  
 |  IsDrawing
 |  
 |  IsLayoutLocked
 |  
 |  IsLoading
 |  
 |  IsModified
 |  
 |  IsVisualLayoutUpdate
 |  
 |  LookAndFeel
 |  
 |  MenuManager
 |  
 |  Modified
 |  
 |  OldEditValue
 |  
 |  Padding
 |  
 |  Painter
 |  
 |  ParseEditValue
 |  
 |  PreferredHeight
 |  
 |  ProcessInplaceEditValueChangedEventCore
 |  
 |  PropertiesChanged
 |  
 |  QueryAccessibilityHelp
 |  
 |  QueryProcessKey
 |  
 |  ReadOnly
 |  
 |  ServiceObject
 |  
 |  ShouldProcessMouseWheelInPopup
 |  
 |  ShowToolTipsCore
 |  
 |  SizeableIsCaptionVisible
 |  
 |  SuppressSelectAll
 |  
 |  ToolTipAnchor
 |  
 |  fEditValue
 |  
 |  fOldEditValue
 |  
 |  fProperties
 |  
 |  lastChangedEditValue
 |  
 |  ----------------------------------------------------------------------
 |  Data and other attributes inherited from BaseEdit:
 |  
 |  About = <unbound method 'About'>
 |  
 |  AllowMouseClick = <unbound method 'AllowMouseClick'>
 |  
 |  BeginAcceptEditValue = <unbound method 'BeginAcceptEditValue'>
 |  
 |  BeginUpdate = <unbound method 'BeginUpdate'>
 |  
 |  CalcDefaultSizeableMinWidth = <unbound method 'CalcDefaultSizeableMinW...
 |  
 |  CalcMinHeight = <unbound method 'CalcMinHeight'>
 |  
 |  CalcPreferredHeight = <unbound method 'CalcPreferredHeight'>
 |  
 |  CanHandleKeyMessage = <unbound method 'CanHandleKeyMessage'>
 |  
 |  CanValidateObjectViaAnnotationAttributes = <unbound method 'CanValidat...
 |  
 |  CanValidateValueViaAnnotationAttributes = <unbound method 'CanValidate...
 |  
 |  CanValidateViaAnnotationAttributesCore = <unbound method 'CanValidateV...
 |  
 |  CancelUpdate = <unbound method 'CancelUpdate'>
 |  
 |  CheckAutoHeight = <unbound method 'CheckAutoHeight'>
 |  
 |  CheckDoubleClick = <unbound method 'CheckDoubleClick'>
 |  
 |  CheckEnabled = <unbound method 'CheckEnabled'>
 |  
 |  CheckErrorIcon = <unbound method 'CheckErrorIcon'>
 |  
 |  ClearHotPressed = <unbound method 'ClearHotPressed'>
 |  
 |  ClearHotPressedCore = <unbound method 'ClearHotPressedCore'>
 |  
 |  ClearHotPressedOnLostFocus = <unbound method 'ClearHotPressedOnLostFoc...
 |  
 |  ClearPreferredHeight = <unbound method 'ClearPreferredHeight'>
 |  
 |  CompareEditValue = <unbound method 'CompareEditValue'>
 |  
 |  CompareEditValueOnChange = <unbound method 'CompareEditValueOnChange'>
 |  
 |  CompleteChanges = <unbound method 'CompleteChanges'>
 |  
 |  ControlOnGotFocus = <unbound method 'ControlOnGotFocus'>
 |  
 |  ControlOnLostFocus = <unbound method 'ControlOnLostFocus'>
 |  
 |  CreateAccessibleInstance = <unbound method 'CreateAccessibleInstance'>
 |  
 |  CreateEventSender = <unbound method 'CreateEventSender'>
 |  
 |  CreateHandle = <unbound method 'CreateHandle'>
 |  
 |  CreateLookAndFeel = <unbound method 'CreateLookAndFeel'>
 |  
 |  CreateRepositoryItem = <unbound method 'CreateRepositoryItem'>
 |  
 |  CreateRepositoryItemCore = <unbound method 'CreateRepositoryItemCore'>
 |  
 |  DefaultErrorIcon = <System.Drawing.Bitmap object>
 |  
 |  DefaultErrorIconAlignment = <System.Windows.Forms.ErrorIconAlignment o...
 |  
 |  DefaultErrorImageOptions = <DevExpress.XtraEditors.BaseEditErrorImageO...
 |  
 |  DestroyHandleCore = <unbound method 'DestroyHandleCore'>
 |  
 |  DoBaseSetBoundsCore = <unbound method 'DoBaseSetBoundsCore'>
 |  
 |  DoValidate = <unbound method 'DoValidate'>
 |  
 |  DoValidateOnEnterKey = <unbound method 'DoValidateOnEnterKey'>
 |  
 |  EndAcceptEditValue = <unbound method 'EndAcceptEditValue'>
 |  
 |  EndUpdate = <unbound method 'EndUpdate'>
 |  
 |  EnsureAnnotationAttributes = <unbound method 'EnsureAnnotationAttribut...
 |  
 |  ExtractParsedValue = <unbound method 'ExtractParsedValue'>
 |  
 |  GetChangingOldEditValue = <unbound method 'GetChangingOldEditValue'>
 |  
 |  GetObjectToValidate = <unbound method 'GetObjectToValidate'>
 |  
 |  GetPreferredSize = <unbound method 'GetPreferredSize'>
 |  
 |  GetScaledBounds = <unbound method 'GetScaledBounds'>
 |  
 |  GetToolTipInfo = <unbound method 'GetToolTipInfo'>
 |  
 |  GetValidationCanceled = <unbound method 'GetValidationCanceled'>
 |  
 |  InitializeDefault = <unbound method 'InitializeDefault'>
 |  
 |  InitializeDefaultProperties = <unbound method 'InitializeDefaultProper...
 |  
 |  IsBindingDataAccessible = <unbound method 'IsBindingDataAccessible'>
 |  
 |  IsBindingManagerPositionValid = <unbound method 'IsBindingManagerPosit...
 |  
 |  IsInputKeyCore = <unbound method 'IsInputKeyCore'>
 |  
 |  IsNeededKey = <unbound method 'IsNeededKey'>
 |  
 |  IsNotLoadedValue = <unbound method 'IsNotLoadedValue'>
 |  
 |  IsNullValue = <unbound method 'IsNullValue'>
 |  
 |  IsTextEditor = <unbound method 'IsTextEditor'>
 |  
 |  LockEditValueChanged = <unbound method 'LockEditValueChanged'>
 |  
 |  OnAutoHeightChanged = <unbound method 'OnAutoHeightChanged'>
 |  
 |  OnCancelEditValueChanging = <unbound method 'OnCancelEditValueChanging...
 |  
 |  OnContextMenuChanged = <unbound method 'OnContextMenuChanged'>
 |  
 |  OnContextMenuStripChanged = <unbound method 'OnContextMenuStripChanged...
 |  
 |  OnEditorKeyUp = <unbound method 'OnEditorKeyUp'>
 |  
 |  OnErrorInfoChanged = <unbound method 'OnErrorInfoChanged'>
 |  
 |  OnErrorTextChanged = <unbound method 'OnErrorTextChanged'>
 |  
 |  OnInvalidValue = <unbound method 'OnInvalidValue'>
 |  
 |  OnProperties_PropertiesChanged = <unbound method 'OnProperties_Propert...
 |  
 |  OnScaleControl = <unbound method 'OnScaleControl'>
 |  
 |  OnValidatingCore = <unbound method 'OnValidatingCore'>
 |  
 |  OnVisibleChanged = <unbound method 'OnVisibleChanged'>
 |  
 |  ParseEditorValue = <unbound method 'ParseEditorValue'>
 |  
 |  PopupServiceControl = <DevExpress.Utils.Win.IPopupServiceControl objec...
 |  
 |  ProcessPopupMouseWheel = <unbound method 'ProcessPopupMouseWheel'>
 |  
 |  RaiseEditValueChanged = <unbound method 'RaiseEditValueChanged'>
 |  
 |  RaiseInvalidValue = <unbound method 'RaiseInvalidValue'>
 |  
 |  RaiseModified = <unbound method 'RaiseModified'>
 |  
 |  RefreshVisualLayout = <unbound method 'RefreshVisualLayout'>
 |  
 |  RefreshVisualLayoutCore = <unbound method 'RefreshVisualLayoutCore'>
 |  
 |  ResetBackColor = <unbound method 'ResetBackColor'>
 |  
 |  ResetEvents = <unbound method 'ResetEvents'>
 |  
 |  ResetForeColor = <unbound method 'ResetForeColor'>
 |  
 |  SendKey = <unbound method 'SendKey'>
 |  
 |  SendKeyUp = <unbound method 'SendKeyUp'>
 |  
 |  SendMouse = <unbound method 'SendMouse'>
 |  
 |  SendMouseUp = <unbound method 'SendMouseUp'>
 |  
 |  SetBoundsCore = <unbound method 'SetBoundsCore'>
 |  
 |  SetEmptyEditValue = <unbound method 'SetEmptyEditValue'>
 |  
 |  SetErrorIcon = <unbound method 'SetErrorIcon'>
 |  
 |  StringStartsWidth = <unbound method 'StringStartsWidth'>
 |  
 |  SuppressMouseWheel = <unbound method 'SuppressMouseWheel'>
 |  
 |  UnLockEditValueChanged = <unbound method 'UnLockEditValueChanged'>
 |  
 |  UpdateFixedHeight = <unbound method 'UpdateFixedHeight'>
 |  
 |  UpdateViewInfoEditValue = <unbound method 'UpdateViewInfoEditValue'>
 |  
 |  add_BackColorChanged = <unbound method 'add_BackColorChanged'>
 |  
 |  add_CustomDisplayText = <unbound method 'add_CustomDisplayText'>
 |  
 |  add_EditValueChanged = <unbound method 'add_EditValueChanged'>
 |  
 |  add_EditValueChanging = <unbound method 'add_EditValueChanging'>
 |  
 |  add_FontChanged = <unbound method 'add_FontChanged'>
 |  
 |  add_ForeColorChanged = <unbound method 'add_ForeColorChanged'>
 |  
 |  add_FormatEditValue = <unbound method 'add_FormatEditValue'>
 |  
 |  add_InvalidValue = <unbound method 'add_InvalidValue'>
 |  
 |  add_Modified = <unbound method 'add_Modified'>
 |  
 |  add_ParseEditValue = <unbound method 'add_ParseEditValue'>
 |  
 |  add_PropertiesChanged = <unbound method 'add_PropertiesChanged'>
 |  
 |  add_QueryAccessibilityHelp = <unbound method 'add_QueryAccessibilityHe...
 |  
 |  add_QueryProcessKey = <unbound method 'add_QueryProcessKey'>
 |  
 |  get_AccessibleDefaultActionDescription = <unbound method 'get_Accessib...
 |  
 |  get_AccessibleDescription = <unbound method 'get_AccessibleDescription...
 |  
 |  get_AccessibleName = <unbound method 'get_AccessibleName'>
 |  
 |  get_AccessibleRole = <unbound method 'get_AccessibleRole'>
 |  
 |  get_AllowFireEditValueChanged = <unbound method 'get_AllowFireEditValu...
 |  
 |  get_AllowUpdateIsModifiedOnValueChanging = <unbound method 'get_AllowU...
 |  
 |  get_BindingManager = <unbound method 'get_BindingManager'>
 |  
 |  get_BorderStyle = <unbound method 'get_BorderStyle'>
 |  
 |  get_CanShowDialog = <unbound method 'get_CanShowDialog'>
 |  
 |  get_ContextMenu = <unbound method 'get_ContextMenu'>
 |  
 |  get_ContextMenuStrip = <unbound method 'get_ContextMenuStrip'>
 |  
 |  get_DefaultErrorIcon = <unbound method 'get_DefaultErrorIcon'>
 |  
 |  get_DefaultErrorIconAlignment = <unbound method 'get_DefaultErrorIconA...
 |  
 |  get_DefaultErrorImageOptions = <unbound method 'get_DefaultErrorImageO...
 |  
 |  get_EditValue = <unbound method 'get_EditValue'>
 |  
 |  get_EditValueDataBindingType = <unbound method 'get_EditValueDataBindi...
 |  
 |  get_EditViewInfo = <unbound method 'get_EditViewInfo'>
 |  
 |  get_EditorClassInfo = <unbound method 'get_EditorClassInfo'>
 |  
 |  get_EditorContainer = <unbound method 'get_EditorContainer'>
 |  
 |  get_EditorContainsFocus = <unbound method 'get_EditorContainsFocus'>
 |  
 |  get_EnterMoveNextControl = <unbound method 'get_EnterMoveNextControl'>
 |  
 |  get_ErrorIcon = <unbound method 'get_ErrorIcon'>
 |  
 |  get_ErrorIconAlignment = <unbound method 'get_ErrorIconAlignment'>
 |  
 |  get_ErrorImageOptions = <unbound method 'get_ErrorImageOptions'>
 |  
 |  get_ErrorText = <unbound method 'get_ErrorText'>
 |  
 |  get_EventSender = <unbound method 'get_EventSender'>
 |  
 |  get_Font = <unbound method 'get_Font'>
 |  
 |  get_ForeColor = <unbound method 'get_ForeColor'>
 |  
 |  get_InplaceType = <unbound method 'get_InplaceType'>
 |  
 |  get_IsAcceptingEditValue = <unbound method 'get_IsAcceptingEditValue'>
 |  
 |  get_IsAllowValidate = <unbound method 'get_IsAllowValidate'>
 |  
 |  get_IsDrawing = <unbound method 'get_IsDrawing'>
 |  
 |  get_IsLayoutLocked = <unbound method 'get_IsLayoutLocked'>
 |  
 |  get_IsLoading = <unbound method 'get_IsLoading'>
 |  
 |  get_IsModified = <unbound method 'get_IsModified'>
 |  
 |  get_IsVisualLayoutUpdate = <unbound method 'get_IsVisualLayoutUpdate'>
 |  
 |  get_LookAndFeel = <unbound method 'get_LookAndFeel'>
 |  
 |  get_MenuManager = <unbound method 'get_MenuManager'>
 |  
 |  get_OldEditValue = <unbound method 'get_OldEditValue'>
 |  
 |  get_Padding = <unbound method 'get_Padding'>
 |  
 |  get_Painter = <unbound method 'get_Painter'>
 |  
 |  get_PopupServiceControl = <unbound method 'get_PopupServiceControl'>
 |  
 |  get_PreferredHeight = <unbound method 'get_PreferredHeight'>
 |  
 |  get_ProcessInplaceEditValueChangedEventCore = <unbound method 'get_Pro...
 |  
 |  get_ReadOnly = <unbound method 'get_ReadOnly'>
 |  
 |  get_ServiceObject = <unbound method 'get_ServiceObject'>
 |  
 |  get_ShouldProcessMouseWheelInPopup = <unbound method 'get_ShouldProces...
 |  
 |  get_ShowToolTipsCore = <unbound method 'get_ShowToolTipsCore'>
 |  
 |  get_SizeableIsCaptionVisible = <unbound method 'get_SizeableIsCaptionV...
 |  
 |  get_SuppressSelectAll = <unbound method 'get_SuppressSelectAll'>
 |  
 |  get_ToolTipAnchor = <unbound method 'get_ToolTipAnchor'>
 |  
 |  remove_BackColorChanged = <unbound method 'remove_BackColorChanged'>
 |  
 |  remove_CustomDisplayText = <unbound method 'remove_CustomDisplayText'>
 |  
 |  remove_EditValueChanged = <unbound method 'remove_EditValueChanged'>
 |  
 |  remove_EditValueChanging = <unbound method 'remove_EditValueChanging'>
 |  
 |  remove_FontChanged = <unbound method 'remove_FontChanged'>
 |  
 |  remove_ForeColorChanged = <unbound method 'remove_ForeColorChanged'>
 |  
 |  remove_FormatEditValue = <unbound method 'remove_FormatEditValue'>
 |  
 |  remove_InvalidValue = <unbound method 'remove_InvalidValue'>
 |  
 |  remove_Modified = <unbound method 'remove_Modified'>
 |  
 |  remove_ParseEditValue = <unbound method 'remove_ParseEditValue'>
 |  
 |  remove_PropertiesChanged = <unbound method 'remove_PropertiesChanged'>
 |  
 |  remove_QueryAccessibilityHelp = <unbound method 'remove_QueryAccessibi...
 |  
 |  remove_QueryProcessKey = <unbound method 'remove_QueryProcessKey'>
 |  
 |  set_AccessibleDefaultActionDescription = <unbound method 'set_Accessib...
 |  
 |  set_AccessibleDescription = <unbound method 'set_AccessibleDescription...
 |  
 |  set_AccessibleName = <unbound method 'set_AccessibleName'>
 |  
 |  set_AccessibleRole = <unbound method 'set_AccessibleRole'>
 |  
 |  set_BorderStyle = <unbound method 'set_BorderStyle'>
 |  
 |  set_ContextMenu = <unbound method 'set_ContextMenu'>
 |  
 |  set_ContextMenuStrip = <unbound method 'set_ContextMenuStrip'>
 |  
 |  set_DefaultErrorIcon = <unbound method 'set_DefaultErrorIcon'>
 |  
 |  set_DefaultErrorIconAlignment = <unbound method 'set_DefaultErrorIconA...
 |  
 |  set_EditValue = <unbound method 'set_EditValue'>
 |  
 |  set_EnterMoveNextControl = <unbound method 'set_EnterMoveNextControl'>
 |  
 |  set_ErrorIcon = <unbound method 'set_ErrorIcon'>
 |  
 |  set_ErrorIconAlignment = <unbound method 'set_ErrorIconAlignment'>
 |  
 |  set_ErrorText = <unbound method 'set_ErrorText'>
 |  
 |  set_Font = <unbound method 'set_Font'>
 |  
 |  set_ForeColor = <unbound method 'set_ForeColor'>
 |  
 |  set_InplaceType = <unbound method 'set_InplaceType'>
 |  
 |  set_IsDrawing = <unbound method 'set_IsDrawing'>
 |  
 |  set_IsModified = <unbound method 'set_IsModified'>
 |  
 |  set_MenuManager = <unbound method 'set_MenuManager'>
 |  
 |  set_Padding = <unbound method 'set_Padding'>
 |  
 |  set_ReadOnly = <unbound method 'set_ReadOnly'>
 |  
 |  set_ServiceObject = <unbound method 'set_ServiceObject'>
 |  
 |  set_SuppressSelectAll = <unbound method 'set_SuppressSelectAll'>
 |  
 |  set_ToolTipAnchor = <unbound method 'set_ToolTipAnchor'>
"""


if __name__ == '__main__':
    root = tk.Tk()

    entry1 = FlyXtraEntry()
    entry1.pack(fill="x")
    entry2 = FlyXtraEntry()
    entry2.advanced_label("entry your name")
    entry2.pack(fill="x")

    root.mainloop()