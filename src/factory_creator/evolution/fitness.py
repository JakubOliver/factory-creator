from collections.abc import Sequence

from .fitness_aspects import FitnessAspect, FitnessContext


class Fitness:
    """Evaluates factory layouts independently of the evolution strategy."""

    def __init__(self, aspects: Sequence[FitnessAspect]) -> None:
        self.aspects = list(aspects)

    def evaluate(self, context: FitnessContext) -> int | float:
        fitness = 0

        for aspect in self.aspects:
            if aspect.weight == 0:
                continue

            fitness += aspect.weight * aspect.evaluate(context)

        return fitness
