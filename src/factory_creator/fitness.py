from collections.abc import Sequence

from .grid import Grid


ConnectionPair = tuple[list[tuple], list[tuple], str]


class Fitness:
    """Evaluates factory layouts independently of the evolution strategy."""

    def evaluate(
        self,
        grid: Grid,
        test_connection: bool = True,
        connection_pair: Sequence[ConnectionPair] = (),
    ) -> int | float:
        fitness = 0

        fitness -= grid.get_area()
        fitness -= grid.get_used_block() / 1.5
        fitness += grid.get_number_of_pointing_to_center() * 10
        fitness -= grid.get_distances_from_center()
        fitness -= grid.get_inserter_cost()

        if test_connection and not self._connections_are_valid(grid, connection_pair):
            return -float("inf")

        return fitness

    def _connections_are_valid(
        self,
        grid: Grid,
        connection_pairs: Sequence[ConnectionPair],
    ) -> bool:
        # TODO: Verify that expected underground connections are really underground.
        return all(
            grid.exists_path(start, end, belt_id)
            for start, end, belt_id in connection_pairs
        )
