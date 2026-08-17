from abc import ABC, abstractmethod
from collections.abc import Callable, Hashable, Sequence

from .mutations.mutation import Mutation
from .fitness import Fitness
from .fitness_aspects import ConnectionPair, FitnessContext
from ..grid.grid import Grid


class EvolutionAlgorithm(ABC):
    """Common interface for algorithms that optimize a factory layout."""

    def __init__(
        self,
        mutations: Sequence[Mutation],
        fitness: Fitness,
        generation_print: bool = True,
        caching_enabled: bool = True,
    ) -> None:
        self.mutations = mutations
        self.fitness = fitness
        self.generation_print = generation_print
        self.caching_enabled = caching_enabled
        self._evolution_cache: set[Hashable] = set()

    def _reset_evolution_cache(self) -> None:
        self._evolution_cache.clear()

    def _cache_attempt(
        self,
        mutation: Mutation,
        attempt_key: Hashable | None,
    ) -> None:
        if not self.caching_enabled or attempt_key is None:
            return

        self._evolution_cache.add(mutation._get_attempt_cache_key(attempt_key))

    def _evaluate_fitness(
        self,
        grid: Grid,
        connection_pairs: Sequence[ConnectionPair] = (),
    ) -> int | float:
        return self.fitness.evaluate(
            FitnessContext(
                grid,
                connection_pairs=connection_pairs,
            )
        )

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
