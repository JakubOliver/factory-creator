from collections.abc import Callable

from .evolution_algorithm import EvolutionAlgorithm
from ..grid.grid import Grid
from ..util.cancellation import never_cancelled


class HillClimbing(EvolutionAlgorithm):
    """Coordinates mutation, evaluation, selection, and stopping conditions."""

    def evolve(
        self,
        grid: Grid,
        iteration: int | float = float("inf"),
        stagnation_break: int = 10,
        create_presentation: bool = False,
        report_method: Callable = print,
        generation_report_method: Callable | None = None,
        error_report_method: Callable | None = None,
        stop_requested: Callable[[], bool] = never_cancelled,
    ) -> Grid | list[Grid]:
        if generation_report_method is None:
            generation_report_method = report_method
        if error_report_method is None:
            error_report_method = report_method

        self._reset_evolution_cache()

        for mutation in self.mutations:
            mutation.set_evolution_cache(
                self._evolution_cache if self.caching_enabled else None
            )
            mutation.set_stop_requested(stop_requested)

        active_iteration = 0
        stagnation_streak = 0
        presentation = []
        current_fitness = None

        while active_iteration < iteration and stagnation_streak < stagnation_break:
            if create_presentation:
                presentation.append(grid)

            if current_fitness is None:
                current_fitness = self._evaluate_fitness(grid)

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
                current_fitness = candidate_fitness
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

        if error_report_method is None:
            error_report_method = report_method

        for mutation in self.mutations:
            for candidate in mutation.generate(grid, report_method):
                if candidate.grid is None:
                    candidate_fitness = -float("inf")
                else:
                    candidate_fitness = self._evaluate_fitness(
                        candidate.grid,
                        connection_pairs=candidate.connection_pairs,
                    )

                self._cache_attempt(
                    mutation,
                    candidate.attempt_key,
                )

                if candidate.grid is not None and candidate_fitness > best_fitness:
                    best_grid = candidate.grid
                    best_fitness = candidate_fitness

        return best_grid, best_fitness
