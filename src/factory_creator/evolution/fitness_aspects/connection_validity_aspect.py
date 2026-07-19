from .fitness_aspect import FitnessAspect, FitnessContext


class ConnectionValidityAspect(FitnessAspect):
    DEFAULT_WEIGHT = 1

    def evaluate(self, context: FitnessContext) -> int | float:
        if not context.test_connection:
            return 0
        valid = all(
            context.grid.exists_path(start, end, belt_id)
            for start, end, belt_id in context.connection_pairs
        )
        return 0 if valid else -float("inf")
