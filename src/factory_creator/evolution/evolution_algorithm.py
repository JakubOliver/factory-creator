from abc import ABC, abstractmethod
from collections.abc import Callable, Hashable, Sequence

from .mutations.mutation import Mutation
from .fitness import ConnectionPair, Fitness
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
        self._fitness_cache: dict[Hashable, int | float] = {}

    def _reset_fitness_cache(self) -> None:
        self._fitness_cache.clear()

    def _evaluate_fitness(
        self,
        grid: Grid,
        cache_key: Hashable | None = None,
        connection_pair: Sequence[ConnectionPair] = (),
    ) -> int | float:
        if cache_key is None:
            return self.fitness.evaluate(
                grid,
                connection_pair=connection_pair,
            )

        if cache_key not in self._fitness_cache:
            self._fitness_cache[cache_key] = self.fitness.evaluate(
                grid,
                connection_pair=connection_pair,
            )
            
        return self._fitness_cache[cache_key]

    @abstractmethod
    def evolve(
        self,
        grid: Grid,
        iteration: int | float = float("inf"),
        stagnation_break: int = 10,
        create_presentation: bool = False,
        report_method: Callable = print,
        generation_report_method: Callable = print,
        error_report_method: Callable | None = None,
    ) -> Grid | list[Grid]:
        """Optimize and return the supplied layout."""
