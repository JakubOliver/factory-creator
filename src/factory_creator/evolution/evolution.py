from collections.abc import Callable

from collections.abc import Sequence

from .fitness import Fitness
from .fitness_aspects import FitnessAspect
from .hill_climbing import HillClimbing
from .mutations.mutation import Mutation
from ..grid.grid import Grid
from ..util.output import OutputLevel, OutputReporter


class Evolution:
    """Entry point for factory layout evolution."""

    @staticmethod
    def evolve(
        grid: Grid,
        mutations: Sequence[Mutation],
        fitness_aspects: Sequence[FitnessAspect],
        iteration: int | float = float("inf"),
        stagnation_break: int = 10,
        create_presentation: bool = False,
        report_method: Callable = print,
        output_level: OutputLevel = OutputLevel.MEDIUM,
        caching_enabled: bool = True,
    ) -> Grid | list[Grid]:
        # TODO: As its is currently implemented, the computation can be parallelized by running multipler hill climbs or mayber better parts of hill climbs in different threads and then combining the results.
        # TODO: it makes sense to use reflection for fitness and also for mutations etc. so in the gui can user select which want to use or add own.
        reporter = OutputReporter(report_method, output_level)
        reporter.low("Evolution started.")
        
        algorithm = HillClimbing(
            mutations=list(mutations),
            fitness=Fitness(fitness_aspects),
            generation_print=True,
            caching_enabled=caching_enabled,
        )
        
        return algorithm.evolve(
            grid,
            iteration=iteration,
            stagnation_break=stagnation_break,
            create_presentation=create_presentation,
            report_method=reporter.high,
            generation_report_method=reporter.low,
            error_report_method=reporter.medium,
        )
