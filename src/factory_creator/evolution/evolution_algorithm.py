from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence

from .mutation import Mutation
from .fitness import Fitness
from ..grid.grid import Grid


class EvolutionAlgorithm(ABC):
    """Common interface for algorithms that optimize a factory layout."""

    def __init__(
        self,
        mutations: Sequence[Mutation],
        fitness: Fitness,
        generation_print: bool = True,
    ) -> None:
        self.mutations = mutations
        self.fitness = fitness
        self.generation_print = generation_print

    @abstractmethod
    def evolve(
        self,
        grid: Grid,
        iteration: int | float = float("inf"),
        stagnation_break: int = 10,
        create_presentation: bool = False,
        report_method: Callable[[str], None] = print,
    ) -> Grid | list[Grid]:
        """Optimize and return the supplied layout."""
