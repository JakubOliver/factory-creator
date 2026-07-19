from .fitness_aspect import FitnessAspect, FitnessContext


class PointingToCenterAspect(FitnessAspect):
    DEFAULT_WEIGHT = 10

    def evaluate(self, context: FitnessContext) -> int | float:
        return context.grid.get_number_of_pointing_to_center()
