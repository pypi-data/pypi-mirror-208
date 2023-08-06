# manually ordered to prevent loops
from importlib.metadata import version
from logging import getLevelName


def libsrg_version():
    ver = version('libsrg')
    return f"libsrg {ver} {__file__} "


def level2str(lev) -> str:
    if not isinstance(lev, str):
        lev = getLevelName(lev)
    return lev


def level2int(lev) -> int:
    if isinstance(lev, str):
        lev = getLevelName(lev)
    return lev
