from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from ...grid.grid import Grid


ConnectionPair = tuple[list[tuple], list[tuple], str]


@dataclass(frozen=True)
class FitnessContext:
    """All data available while evaluating one evolution candidate."""

    grid: Grid
    test_connection: bool = True
    connection_pairs: Sequence[ConnectionPair] = ()


class FitnessAspect(ABC):
    """One independently weighted component of a layout fitness score."""

    DEFAULT_WEIGHT: int | float = 1

    def __init__(self, weight: int | float | None = None) -> None:
        self.weight = self.DEFAULT_WEIGHT if weight is None else weight

    @abstractmethod
    def evaluate(self, context: FitnessContext) -> int | float:
        ...
