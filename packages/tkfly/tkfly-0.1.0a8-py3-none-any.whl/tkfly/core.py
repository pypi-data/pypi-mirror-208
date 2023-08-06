import contextlib
import os

__all__ = [
    "fly_chdir",
    "fly_local",
    "fly_root",
    "fly_load1",
    "fly_load2",
    "fly_load3",
    "fly_load4",
    "fly_load5"
]


def _chdir(target: str):
    @contextlib.contextmanager
    def chdir(taget: str):
        current = os.getcwd()
        try:
            os.chdir(target)
            yield
        finally:
            os.chdir(current)

    return chdir(target)


fly_chdir = _chdir


def _local():
    return os.path.abspath(os.path.dirname(__file__))


fly_local = _local

from tkinter import Tk


def _root() -> Tk:
    from tkinter import _default_root
    return _default_root


fly_root = _root


def _load1(package: str):
    """
    导入指定库

    :param package: 包名
    :return:
    """

    fly_root().eval(f"package require {package}")


fly_load1 = _load1


def _load2(pkg_index: str = "pkgIndex.tcl"):
    """
    加载库

    :param pkg_index: 包索引
    :return:
    """
    fly_root().eval("set dir [file dirname [info script]]")
    fly_root().eval(f"source {pkg_index}")


fly_load2 = _load2


def _load3(package: str, pkg_index: str = "pkgIndex.tcl"):
    """
    加载并导入库

    :param package: 包名
    :param pkg_index: 包索引
    :return:
    """
    _load2(pkg_index)
    _load1(package)


fly_load3 = _load3


def _load4(package: str, local, pkg_index: str = "pkgIndex.tcl"):
    """
    加载指定位置下的包

    :param package: 包名
    :param local: 包位置
    :param pkg_index: 包索引
    :return:
    """

    with fly_chdir(local):
        _load3(package, pkg_index)


fly_load4 = _load4


def _load5(local, pkg_index: str = "pkgIndex.tcl"):
    """
    仅加载不导入

    :param local: 包位置
    :param pkg_index: 包索引
    :return:
    """
    with fly_chdir(local):
        _load2(pkg_index)


fly_load5 = _load5


def _load6(package: str, local):
    """
    仅加载不导入

    :param local: 包位置
    :param package: 包名
    :return:
    """
    with fly_chdir(local):
        _load1(package)


fly_load6 = _load6
