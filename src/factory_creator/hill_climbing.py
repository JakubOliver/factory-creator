from collections.abc import Callable

from .evolution_algorithm import EvolutionAlgorithm
from .grid import Grid


class HillClimbing(EvolutionAlgorithm):
    """Coordinates mutation, evaluation, selection, and stopping conditions."""

    def evolve(
        self,
        grid: Grid,
        iteration: int | float = float("inf"),
        stagnation_break: int = 10,
        create_presentation: bool = False,
        report_method: Callable[[str], None] = print,
    ) -> Grid | list[Grid]:
        active_iteration = 0
        stagnation_streak = 0
        presentation = []

        while active_iteration < iteration and stagnation_streak < stagnation_break:
            if create_presentation:
                presentation.append(grid)

            current_fitness = self.fitness.evaluate(grid)
            if self.generation_print:
                report_method(
                    f"----------- NEXT GENERATION ({active_iteration}) -------------"
                )
                report_method(f"Fitness: {current_fitness}")

            candidate, candidate_fitness = self._select_best_neighbor(
                grid,
                current_fitness,
                report_method,
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
        report_method: Callable[[str], None] = print,
    ) -> tuple[Grid, float]:
        best_grid = grid
        best_fitness = current_fitness

        for mutation in self.mutations:
            for candidate in mutation.generate(grid, report_method):
                candidate_fitness = self.fitness.evaluate(
                    candidate.grid,
                    connection_pair=candidate.connection_pairs,
                )
                if candidate_fitness > best_fitness:
                    best_grid = candidate.grid
                    best_fitness = candidate_fitness

        return best_grid, best_fitness
