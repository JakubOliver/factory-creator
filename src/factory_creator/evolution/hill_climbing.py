from collections.abc import Callable

from .evolution_algorithm import EvolutionAlgorithm
from .mutations.mutation import Mutation
from ..grid.grid import Grid


class HillClimbing(EvolutionAlgorithm):
    """Coordinates mutation, evaluation, selection, and stopping conditions."""

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
        generation_report_method = generation_report_method or report_method
        error_report_method = error_report_method or report_method
        self._reset_fitness_cache()
        active_iteration = 0
        stagnation_streak = 0
        presentation = []

        while active_iteration < iteration and stagnation_streak < stagnation_break:
            if create_presentation:
                presentation.append(grid)

            current_fitness = self._evaluate_fitness(
                grid,
                cache_key=("current", grid.state_key_memory()),
            )
            if self.generation_print:
                generation_report_method(
                    f"----------- NEXT GENERATION ({active_iteration}) -------------"
                )
                generation_report_method(f"Fitness: {current_fitness}")

            candidate, candidate_fitness = self._select_best_neighbor(
                grid,
                current_fitness,
                report_method,
                error_report_method,
            )
            if candidate_fitness > current_fitness:
                grid = candidate
                stagnation_streak = 0
            else:
                stagnation_streak += 1

            active_iteration += 1

        return presentation if create_presentation else grid

    def _select_best_neighbor(
        self,
        grid: Grid,
        current_fitness: float = -float("inf"),
        report_method: Callable = print,
        error_report_method: Callable | None = None,
    ) -> tuple[Grid, float]:
        best_grid = grid
        best_fitness = current_fitness

        error_report_method = error_report_method or report_method
        for mutation in self.mutations:
            for candidate in mutation.generate(grid, report_method):
                candidate_fitness = self._evaluate_fitness(
                    candidate.grid,
                    cache_key=(type(mutation), candidate.cache_key)
                    if candidate.cache_key is not None
                    else None,
                    connection_pair=candidate.connection_pairs,
                )
                if candidate_fitness > best_fitness:
                    best_grid = candidate.grid
                    best_fitness = candidate_fitness

        return best_grid, best_fitness
