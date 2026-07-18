from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass

from .fitness import ConnectionPair
from ..grid.grid import Grid


@dataclass(frozen=True)
class MutationCandidate:
    grid: Grid
    connection_pairs: tuple[ConnectionPair, ...] = ()


class Mutation(ABC):
    """Produces neighboring layouts from one immutable generation state."""

    @abstractmethod
    def generate(
        self,
        grid: Grid,
        report_method: Callable[[str], None] = print,
    ) -> Iterator[MutationCandidate]:
        ...
