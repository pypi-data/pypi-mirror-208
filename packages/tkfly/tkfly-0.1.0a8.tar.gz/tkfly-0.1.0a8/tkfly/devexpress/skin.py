class FlyXtraSkin(object):
    def getskin(self, style):
        from tkfly.devexpress import FlyXtraLoadSkin
        FlyXtraLoadSkin()
        from DevExpress.LookAndFeel import SkinStyle, SkinSvgPalette
        if style == "basic":
            _style = SkinStyle.Basic
        elif style == "basic-bluedark":
            _style = SkinSvgPalette.DefaultSkin.BlueDark
        elif style == "bezier":
            _style = SkinStyle.Bezier
        elif style == "bezier-crambe":
            _style = SkinSvgPalette.Bezier.Crambe
        elif style == "bezier-cherry-ink":
            _style = SkinSvgPalette.Bezier.CherryInk
        elif style == "sharp":
            _style = SkinStyle.Sharp
        elif style == "light":
            _style = SkinStyle.DevExpress
        elif style == "dark":
            _style = SkinStyle.DevExpressDark
        elif style == "vs2013":
            _style = SkinStyle.VisualStudio2013Light
        elif style == "vs2013-darkness":
            _style = SkinStyle.VisualStudio2013Dark
        elif style == "vs2013-blueness":
            _style = SkinStyle.VisualStudio2013Blue
        elif style == "wxi":
            _style = SkinStyle.WXI
        elif style == "wxi-freshness":
            _style = SkinSvgPalette.WXI.Freshness
        elif style == "wxi-darkness":
            _style = SkinSvgPalette.WXI.Darkness
        elif style == "wxi-clearness":
            _style = SkinSvgPalette.WXI.Clearness
        elif style == "wxi-sharpness":
            _style = SkinSvgPalette.WXI.Sharpness
        elif style == "wxi-calmness":
            _style = SkinSvgPalette.WXI.Calmness
        elif style == "wxi-office-white":
            _style = SkinSvgPalette.WXI.OfficeWhite
        elif style == "wxi-office-black":
            _style = SkinSvgPalette.WXI.OfficeBlack
        elif style == "wxicompact":
            _style = SkinStyle.WXICompact
        elif style == "wxicompact-freshness":
            _style = SkinSvgPalette.WXICompact.Freshness
        elif style == "wxicompact-darkness":
            _style = SkinSvgPalette.WXICompact.Darkness
        elif style == "wxicompact-clearness":
            _style = SkinSvgPalette.WXICompact.Clearness
        elif style == "wxicompact-sharpness":
            _style = SkinSvgPalette.WXICompact.Sharpness
        elif style == "wxicompact-calmness":
            _style = SkinSvgPalette.WXICompact.Calmness
        elif style == "wxicompact-office-white":
            _style = SkinSvgPalette.WXICompact.OfficeWhite
        elif style == "wxicompact-office-black":
            _style = SkinSvgPalette.WXICompact.OfficeBlack
        return _style

    def userskin(self, style):
        from tkfly.devexpress import FlyXtraLoadSkin
        FlyXtraLoadSkin()
        from DevExpress.LookAndFeel import UserLookAndFeel
        UserLookAndFeel.Default.SetSkinStyle(self.getskin(style))

    def userskin_name(self, style: str):
        from tkfly.devexpress import FlyXtraLoadSkin
        FlyXtraLoadSkin()
        from DevExpress.LookAndFeel import UserLookAndFeel, DefaultLookAndFeel, SkinStyle, SkinSvgPalette
        UserLookAndFeel.Default.set_SkinName(style)


""" UserLookAndFeel

class UserLookAndFeel(System.Object)
 |  Void .ctor(System.Object)
 |
 |  Method resolution order:
 |      UserLookAndFeel
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
 |  ActiveLookAndFeel
 |
 |  ActiveSkinName
 |
 |  ActiveStyle
 |
 |  ActiveSvgPaletteName
 |
 |  AllowParentEvents
 |
 |  CompactUIMode
 |
 |  CompactUIModeForced
 |
 |  HasSubscribers
 |
 |  InStyleChanged
 |
 |  IsColorized
 |
 |  IsDefaultLookAndFeel
 |
 |  IsLookAndFeelHierarchyRoot
 |
 |  OwnerControl
 |
 |  Painter
 |
 |  ParentLookAndFeel
 |
 |  SkinMaskColor
 |
 |  SkinMaskColor2
 |
 |  SkinName
 |
 |  Style
 |
 |  StyleChanged
 |
 |  TouchUIParent
 |
 |  UseDefaultLookAndFeel
 |
 |  UseWindows7Border
 |
 |  UseWindowsXPTheme
 |
 |  fParentLookAndFeel
 |
 |  fStyle
 |
 |  fUseDefaultLookAndFeel
 |
 |  fUseWindowsXPTheme
 |
 |  ----------------------------------------------------------------------
 |  Data and other attributes defined here:
 |
 |  Assign = <unbound method 'Assign'>
 |
 |  CreatePainter = <unbound method 'CreatePainter'>
 |
 |  Default = <DevExpress.LookAndFeel.Design.UserLookAndFeelDefault object...
 |
 |  DefaultSkinName = 'Basic'
 |
 |  DestroyDefaultLookAndFeel = <unbound method 'DestroyDefaultLookAndFeel...
 |
 |  Dispose = <unbound method 'Dispose'>
 |
 |  ForceCompactUIMode = <unbound method 'ForceCompactUIMode'>
 |
 |  GetCompactScaleFactor = <unbound method 'GetCompactScaleFactor'>
 |
 |  GetCompactUI = <unbound method 'GetCompactUI'>
 |
 |  GetIsLookAndFeelHierarchyRoot = <unbound method 'GetIsLookAndFeelHiera...
 |
 |  GetLookAndFeel = <unbound method 'GetLookAndFeel'>
 |
 |  GetMaskColor = <unbound method 'GetMaskColor'>
 |
 |  GetMaskColor2 = <unbound method 'GetMaskColor2'>
 |
 |  GetTouchScaleFactor = <unbound method 'GetTouchScaleFactor'>
 |
 |  GetTouchUI = <unbound method 'GetTouchUI'>
 |
 |  GetTouchUILookAndFeel = <unbound method 'GetTouchUILookAndFeel'>
 |
 |  HasDefaultLookAndFeel = True
 |
 |  IsEquals = <unbound method 'IsEquals'>
 |
 |  OnFirstSubscribe = <unbound method 'OnFirstSubscribe'>
 |
 |  OnLastUnsubscribe = <unbound method 'OnLastUnsubscribe'>
 |
 |  OnParentDisposed = <unbound method 'OnParentDisposed'>
 |
 |  OnParentStyleChanged = <unbound method 'OnParentStyleChanged'>
 |
 |  OnStyleChangeProgress = <unbound method 'OnStyleChangeProgress'>
 |
 |  OnStyleChanged = <unbound method 'OnStyleChanged'>
 |
 |  Overloads = <unbound method '__init__'>
 |
 |  Purge = <unbound method 'Purge'>
 |
 |  Reset = <unbound method 'Reset'>
 |
 |  ResetParentLookAndFeel = <unbound method 'ResetParentLookAndFeel'>
 |
 |  ResetParentLookAndFeelCore = <unbound method 'ResetParentLookAndFeelCo...
 |
 |  ResetSkinMaskColors = <unbound method 'ResetSkinMaskColors'>
 |
 |  SetControlParentLookAndFeel = <unbound method 'SetControlParentLookAnd...
 |
 |  SetDefaultStyle = <unbound method 'SetDefaultStyle'>
 |
 |  SetFlatStyle = <unbound method 'SetFlatStyle'>
 |
 |  SetOffice2003Style = <unbound method 'SetOffice2003Style'>
 |
 |  SetParentLookAndFeel = <unbound method 'SetParentLookAndFeel'>
 |
 |  SetParentLookAndFeelCore = <unbound method 'SetParentLookAndFeelCore'>
 |
 |  SetSkinMaskColors = <unbound method 'SetSkinMaskColors'>
 |
 |  SetSkinPalette = <unbound method 'SetSkinPalette'>
 |
 |  SetSkinStyle = <unbound method 'SetSkinStyle'>
 |
 |  SetStyle = <unbound method 'SetStyle'>
 |
 |  SetStyle3D = <unbound method 'SetStyle3D'>
 |
 |  SetUltraFlatStyle = <unbound method 'SetUltraFlatStyle'>
 |
 |  SetWindowsXPStyle = <unbound method 'SetWindowsXPStyle'>
 |
 |  ShouldSerialize = <unbound method 'ShouldSerialize'>
 |
 |  StyleChangedEventHandler`1 = <class 'DevExpress.LookAndFeel.StyleChang...
 |
 |  SubscribeDefaultChanged = <unbound method 'SubscribeDefaultChanged'>
 |
 |  SubscribeParentStyleChanged = <unbound method 'SubscribeParentStyleCha...
 |
 |  ToString = <unbound method 'ToString'>
 |
 |  UnsubscribeDefaultChanged = <unbound method 'UnsubscribeDefaultChanged...
 |
 |  UnsubscribeParentStyleChanged = <unbound method 'UnsubscribeParentStyl...
 |
 |  UpdateStyleSettings = <unbound method 'UpdateStyleSettings'>
 |
 |  __init__ = <unbound method '__init__'>
 |
 |  __overloads__ = <unbound method '__init__'>
 |
 |  add_StyleChanged = <unbound method 'add_StyleChanged'>
 |
 |  get_ActiveLookAndFeel = <unbound method 'get_ActiveLookAndFeel'>
 |
 |  get_ActiveSkinName = <unbound method 'get_ActiveSkinName'>
 |
 |  get_ActiveStyle = <unbound method 'get_ActiveStyle'>
 |
 |  get_ActiveSvgPaletteName = <unbound method 'get_ActiveSvgPaletteName'>
 |
 |  get_AllowParentEvents = <unbound method 'get_AllowParentEvents'>
 |
 |  get_CompactUIMode = <unbound method 'get_CompactUIMode'>
 |
 |  get_CompactUIModeForced = <unbound method 'get_CompactUIModeForced'>
 |
 |  get_Default = <unbound method 'get_Default'>
 |
 |  get_HasDefaultLookAndFeel = <unbound method 'get_HasDefaultLookAndFeel...
 |
 |  get_HasSubscribers = <unbound method 'get_HasSubscribers'>
 |
 |  get_InStyleChanged = <unbound method 'get_InStyleChanged'>
 |
 |  get_IsColorized = <unbound method 'get_IsColorized'>
 |
 |  get_IsDefaultLookAndFeel = <unbound method 'get_IsDefaultLookAndFeel'>
 |
 |  get_IsLookAndFeelHierarchyRoot = <unbound method 'get_IsLookAndFeelHie...
 |
 |  get_OwnerControl = <unbound method 'get_OwnerControl'>
 |
 |  get_Painter = <unbound method 'get_Painter'>
 |
 |  get_ParentLookAndFeel = <unbound method 'get_ParentLookAndFeel'>
 |
 |  get_SkinMaskColor = <unbound method 'get_SkinMaskColor'>
 |
 |  get_SkinMaskColor2 = <unbound method 'get_SkinMaskColor2'>
 |
 |  get_SkinName = <unbound method 'get_SkinName'>
 |
 |  get_Style = <unbound method 'get_Style'>
 |
 |  get_TouchUIParent = <unbound method 'get_TouchUIParent'>
 |
 |  get_UseDefaultLookAndFeel = <unbound method 'get_UseDefaultLookAndFeel...
 |
 |  get_UseWindows7Border = <unbound method 'get_UseWindows7Border'>
 |
 |  get_UseWindowsXPTheme = <unbound method 'get_UseWindowsXPTheme'>
 |
 |  remove_StyleChanged = <unbound method 'remove_StyleChanged'>
 |
 |  set_CompactUIMode = <unbound method 'set_CompactUIMode'>
 |
 |  set_InStyleChanged = <unbound method 'set_InStyleChanged'>
 |
 |  set_ParentLookAndFeel = <unbound method 'set_ParentLookAndFeel'>
 |
 |  set_SkinMaskColor = <unbound method 'set_SkinMaskColor'>
 |
 |  set_SkinMaskColor2 = <unbound method 'set_SkinMaskColor2'>
 |
 |  set_SkinName = <unbound method 'set_SkinName'>
 |
 |  set_Style = <unbound method 'set_Style'>
 |
 |  set_TouchUIParent = <unbound method 'set_TouchUIParent'>
 |
 |  set_UseDefaultLookAndFeel = <unbound method 'set_UseDefaultLookAndFeel...
 |
 |  set_UseWindows7Border = <unbound method 'set_UseWindows7Border'>
 |
 |  set_UseWindowsXPTheme = <unbound method 'set_UseWindowsXPTheme'>
"""


#######################################################################################################################


""" SkinSvgPalette
class SkinSvgPalette(System.Object)
 |  Python wrapper for .NET type DevExpress.LookAndFeel.SkinSvgPalette
 |  
 |  Method resolution order:
 |      SkinSvgPalette
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
 |  CategoryName
 |  
 |  SkinStyle
 |  
 |  ----------------------------------------------------------------------
 |  Data and other attributes defined here:
 |  
 |  Bezier = <DevExpress.LookAndFeel.Bezier object>
 |  
 |  DefaultSkin = <DevExpress.LookAndFeel.Basic object>
 |  
 |  HighContrast = <DevExpress.LookAndFeel.HighContrast object>
 |  
 |  Office2019Black = <DevExpress.LookAndFeel.Office2019Black object>
 |  
 |  Office2019Colorful = <DevExpress.LookAndFeel.Office2019Colorful object...
 |  
 |  Office2019White = <DevExpress.LookAndFeel.Office2019White object>
 |  
 |  WXI = <DevExpress.LookAndFeel.WXI object>
 |  
 |  WXICompact = <DevExpress.LookAndFeel.WXICompact object>
 |  
 |  __init__ = <unbound method '__init__'>
 |  
 |  get_CategoryName = <unbound method 'get_CategoryName'>
 |  
 |  get_SkinStyle = <unbound method 'get_SkinStyle'>
 |  
 |  op_Implicit = <unbound method 'op_Implicit'>
"""

#######################################################################################################################

""" SkinStyle

class SkinStyle(System.Object)
 |  Python wrapper for .NET type DevExpress.LookAndFeel.SkinStyle
 |  
 |  Method resolution order:
 |      SkinStyle
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
 |  CompactUIModeForced
 |  
 |  ----------------------------------------------------------------------
 |  Data and other attributes defined here:
 |  
 |  Basic = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Bezier = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Black = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Blue = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Blueprint = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Caramel = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Coffee = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  DarkSide = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Darkroom = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  DevExpress = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  DevExpressDark = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Foggy = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  GlassOceans = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  HighContrast = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  HighContrastClassic = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Lilian = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  LiquidSky = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  LondonLiquidSky = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  McSkin = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Metropolis = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  MetropolisDark = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  MoneyTwins = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2007Black = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2007Blue = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2007Green = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2007Pink = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2007Silver = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2010Black = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2010Blue = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2010Silver = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2013 = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2013DarkGray = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2013LightGray = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2016Black = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2016Colorful = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2016Dark = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2019Black = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2019Colorful = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2019DarkGray = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Office2019White = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Pumpkin = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Seven = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  SevenClassic = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Sharp = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  SharpPlus = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Springtime = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Stardust = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Summer2008 = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  TheAsphaltWorld = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Valentine = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  VisualStudio2010 = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  VisualStudio2013Blue = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  VisualStudio2013Dark = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  VisualStudio2013Light = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  WXI = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  WXICompact = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Whiteprint = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  Xmas2008Blue = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  __init__ = <unbound method '__init__'>
 |  
 |  get_CompactUIModeForced = <unbound method 'get_CompactUIModeForced'>
 |  
 |  iMaginary = <DevExpress.LookAndFeel.SkinStyle object>
 |  
 |  op_Implicit = <unbound method 'op_Implicit'>
"""

#######################################################################################################################

""" WXI

class WXI(SkinSvgPalette)
 |  Python wrapper for .NET type DevExpress.LookAndFeel.WXI
 |  
 |  Method resolution order:
 |      WXI
 |      SkinSvgPalette
 |      System.Object
 |      builtins.object
 |  
 |  Data descriptors defined here:
 |  
 |  Calmness
 |  
 |  Clearness
 |  
 |  Darkness
 |  
 |  Default
 |  
 |  OfficeBlack
 |  
 |  OfficeColorful
 |  
 |  OfficeDarkGray
 |  
 |  OfficeWhite
 |  
 |  PaletteSet
 |  
 |  Sharpness
 |  

"""


#######################################################################################################################


""" Basic

class Basic(SkinSvgPalette)
 |  Python wrapper for .NET type DevExpress.LookAndFeel.Basic
 |  
 |  Method resolution order:
 |      Basic
 |      SkinSvgPalette
 |      System.Object
 |      builtins.object
 |  
 |  Data descriptors defined here:
 |  
 |  BlueDark
 |  
 |  Default
 |  
 |  PaletteSet
 |  
 |  PineDark
 |  
 |  PineLight
 |  
 |  VioletDark
 |  
 |  VioletLight
 |  
 
"""


#######################################################################################################################


"""
class Bezier(SkinSvgPalette)
 |  Python wrapper for .NET type DevExpress.LookAndFeel.Bezier
 |  
 |  Method resolution order:
 |      Bezier
 |      SkinSvgPalette
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
 |  Aquarelle
 |  
 |  ArtHouse
 |  
 |  BW
 |  
 |  BlackberryShake
 |  
 |  BlueVelvet
 |  
 |  CherryInk
 |  
 |  Crambe
 |  
 |  DarkTurquoise
 |  
 |  DateFruit
 |  
 |  Default
 |  
 |  Dragonfly
 |  
 |  Fireball
 |  
 |  GhostShark
 |  
 |  GloomGloom
 |  
 |  Grasshopper
 |  
 |  HighContrastBlack
 |  
 |  HighContrastWhite
 |  
 |  LeafRustle
 |  
 |  MercuryIce
 |  
 |  MilkSnake
 |  
 |  MorayEel
 |  
 |  Nebula
 |  
 |  NeonLollipop
 |  
 |  NorwegianWood
 |  
 |  OfficeBlack
 |  
 |  OfficeColorful
 |  
 |  OfficeDarkGray
 |  
 |  OfficeWhite
 |  
 |  Oxygen3
 |  
 |  PaletteSet
 |  
 |  PlasticSpace
 |  
 |  Prometheus
 |  
 |  Starshine
 |  
 |  Tokyo
 |  
 |  Twenty
 |  
 |  TwentyGold
 |  
 |  VS2019Blue
 |  
 |  VSBlue
 |  
 |  VSDark
 |  
 |  VSLight
 |  
 |  Vacuum
 |  
 |  Volcano
 |  
 |  WitchRave
"""

if __name__ == '__main__':
    from tkfly.devexpress import FlyXtraLoadSkin

    FlyXtraLoadSkin()
    from DevExpress.LookAndFeel import UserLookAndFeel, DefaultLookAndFeel, SkinStyle, SkinSvgPalette, WXI

    help(SkinSvgPalette.Bezier)
