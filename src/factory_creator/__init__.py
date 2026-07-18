from typing import TYPE_CHECKING as _TYPE_CHECKING, Any as _Any

if _TYPE_CHECKING:
    from .cli import CLI
    from .gui import MainWindow

__all__ = ["CLI", "MainWindow"]


def __getattr__(name: str) -> _Any:
    """Load the public user interfaces only when they are requested."""
    if name == "CLI":
        from .cli import CLI

        return CLI
    if name == "MainWindow":
        from .gui import MainWindow

        return MainWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
