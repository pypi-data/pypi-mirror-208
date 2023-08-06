import contextlib
import os


@contextlib.contextmanager
def chdir(target: str):
    """Context-managed chdir, original implementation by GitHub @Akuli"""
    current = os.getcwd()
    try:
        os.chdir(target)
        yield
    finally:
        os.chdir(current)


def load_winico(window, version: str = "0.7.1"):
    global _load_scrollutil
    local = os.path.abspath(os.path.dirname(__file__))
    with chdir(local):
        window.tk.eval("set dir [file dirname [info script]]")
        window.tk.eval("source pkgIndex.tcl")
        window.tk.eval("package require Winico " + version)

