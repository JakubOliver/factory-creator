from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass

from ..fitness_aspects import ConnectionPair
from ...grid.grid import Grid
from ...util.cancellation import never_cancelled, raise_if_cancelled


@dataclass(frozen=True)
class MutationCandidate:
    grid: Grid
    connection_pairs: tuple[ConnectionPair, ...] = ()
    cache_key: int | None = None


class Mutation(ABC):
    """Produces neighboring layouts from one immutable generation state."""

    def __init__(
        self,
        start_generation: int = 0,
        end_generation: int | float = float("inf"),
    ) -> None:
        self.start_generation = start_generation
        self.end_generation = end_generation
        self._generation = 0
        self._stop_requested = never_cancelled

    def set_stop_requested(self, stop_requested) -> None:
        self._stop_requested = stop_requested

    def stop_requested(self) -> bool:
        return self._stop_requested()

    def generate(
        self,
        grid: Grid,
        report_method: Callable = print,
        error_report_method: Callable | None = None,
    ) -> Iterator[MutationCandidate]:
        raise_if_cancelled(self.stop_requested)
        generation = self._generation
        self._generation += 1

        if not self.start_generation <= generation < self.end_generation:
            yield from Mutation._unchanged_grid(grid)
            return

        for candidate in self._generate(
            grid,
            report_method,
            error_report_method=error_report_method or report_method,
        ):
            raise_if_cancelled(self.stop_requested)
            yield candidate

        raise_if_cancelled(self.stop_requested)

    @staticmethod
    def _unchanged_grid(grid: Grid) -> Iterator[MutationCandidate]:
        yield MutationCandidate(grid)

    @abstractmethod
    def _generate(
        self,
        grid: Grid,
        report_method: Callable = print,
        error_report_method: Callable | None = None,
    ) -> Iterator[MutationCandidate]:
        ...

    @abstractmethod
    def get_cache_key(self, value: object) -> int:
        ...
