def addMouseWheelSupport(tag="all"):
    from tkinter import _default_root
    _default_root.eval("scrollutil::addMouseWheelSupport " + tag)


def createWheelEventBindings(tag="all"):
    from tkinter import _default_root
    _default_root.eval("scrollutil::createWheelEventBindings " + tag)


def enableScrollingByWheel(scrollableWidgetContainer=""):
    from tkinter import _default_root
    _default_root.eval("scrollutil::enableScrollingByWheel " + scrollableWidgetContainer)


def disableScrollingByWheel(scrollableWidgetContainer=""):
    from tkinter import _default_root
    _default_root.eval("scrollutil::disableScrollingByWheel " + scrollableWidgetContainer)


def adaptWheelEventHandling(ignorefocus="", widget=""):
    from tkinter import _default_root
    _default_root.eval("scrollutil::adaptWheelEventHandling " + ignorefocus + " " + widget)


def setFocusCheckWindow(widget=""):
    from tkinter import _default_root
    _default_root.eval("scrollutil::setFocusCheckWindow " + widget)


def focusCheckWindow(widget=""):
    from tkinter import _default_root
    _default_root.eval("scrollutil::focusCheckWindow " + widget)


def addclosetab(style):
    from tkinter import _default_root
    _default_root.eval("scrollutil::addclosetab " + style)


def removeclosetab(style):
    from tkinter import _default_root
    _default_root.eval("scrollutil::removeclosetab " + style)
