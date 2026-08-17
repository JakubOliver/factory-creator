from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    description: str
    run: Callable[[], None]
