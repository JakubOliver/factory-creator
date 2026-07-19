from .fitness_aspect import FitnessAspect, FitnessContext


class UsedBlockAspect(FitnessAspect):
    DEFAULT_WEIGHT = -1 / 1.5

    def evaluate(self, context: FitnessContext) -> int | float:
        return context.grid.get_used_block()
