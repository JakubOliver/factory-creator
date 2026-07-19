from collections.abc import Callable


class ComputationCancelled(Exception):
    """Raised when a running factory computation is cancelled cooperatively."""


def never_cancelled() -> bool:
    """Default cancellation predicate for non-GUI callers."""
    return False


def raise_if_cancelled(stop_requested: Callable[[], bool]) -> None:
    """Abort at an explicit cancellation checkpoint."""
    if stop_requested():
        raise ComputationCancelled("Factory computation was cancelled.")
