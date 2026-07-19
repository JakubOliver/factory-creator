from .fitness_aspect import FitnessAspect, FitnessContext


class InserterCostAspect(FitnessAspect):
    DEFAULT_WEIGHT = -1

    def evaluate(self, context: FitnessContext) -> int | float:
        return context.grid.get_inserter_cost()
