import copy
import itertools
from collections.abc import Callable, Iterator

from networkx.algorithms.reciprocity import overall_reciprocity

from .factory import FactoryUtil
from .graph_to_matrix import GraphToMatrix
from .grid import *

class Evolution:
    GENERATION_PRINT = True
    SHOW_REASONS_FOR_INDIVIDUAL_FAILURE = True

    @staticmethod
    def evol(
        grid: Grid,
        iteration: int | float = float("inf"),
        stagnation_break: int = 10,
        create_presentation = False,
        report_method = print
    ) -> Grid:
        """
        Runs the evolution process over the provided grid.

        :param grid: Grid representation of the factory.
        :param iteration: Maximum number of evolution iterations.
        :param stagnation_break: Number of iterations without improvement before the process stops.
        :return: Grid representation after the evolution process.
        """

        return Evolution.hill_climb(
            grid,
            iteration = iteration,
            stagnation_break = stagnation_break,
            create_presentation = create_presentation,
            report_method = report_method
        )

    @staticmethod
    def get_changed_cords(cord: tuple) -> Iterator[tuple]:
        """
        Iterates over coordinates adjacent to the provided coordinates.

        :param cord: Coordinates whose adjacent coordinates will be generated.
        :return: Iterator over coordinates adjacent to the provided coordinates.
        """

        for dx, dy in Grid.GRID_MOVES:
            yield cord[0] + dx, cord[1] + dy

    @staticmethod
    def hill_climb(
        grid: Grid,
        iteration: int | float = float("inf"),
        stagnation_break: int = 10,
        create_presentation = False,
        report_method = print
    ) -> Grid:
        """
        Improves the grid by repeatedly moving buildings to neighboring coordinates.

        :param grid: Grid representation of the factory.
        :param iteration: Maximum number of hill climbing iterations.
        :param stagnation_break: Number of iterations without improvement before the process stops.
        :return: Grid representation after hill climbing.
        """

        active_iteration = 0
        stagnation_streak = 0
        last_fitness = None

        if create_presentation:
            presentation = []

        while active_iteration < iteration and stagnation_streak < stagnation_break:
            if create_presentation:
                presentation.append(grid)

            fitness = Evolution.fitness(grid)

            if Evolution.GENERATION_PRINT:
                report_method(f"----------- NEXT GENERATION ({active_iteration}) -------------")
                report_method(f"Fitness: {fitness}")

            overall_best_worlds, overall_best_world_fitness = \
                Evolution.hill_climbing_move_around(
                    grid, 
                    overall_best_world_fitness=fitness, 
                    report_method=report_method
                )

            if overall_best_worlds is not None:
                grid = overall_best_worlds

            if overall_best_world_fitness == last_fitness:
                stagnation_streak += 1
            else:
                stagnation_streak = 0

            last_fitness = overall_best_world_fitness
            active_iteration += 1

        if create_presentation:
            return presentation

        return grid
    
    @staticmethod
    def hill_climbing_move_around(
        grid: Grid,
        overall_best_world_fitness: float = -float("inf"),
        report_method = print
    ) -> Grid | None:
        overall_best_worlds = None

        c, n = 0, grid.get_number_of_factories()
        for active_cord, grid_entry in grid.get_factories():
            best_world = Evolution._hill_climbing_move_around_process_building(
                grid,
                active_cord,
                grid_entry,
                report_method=report_method
            )

            if best_world is not None:
                best_world_fitness = Evolution.fitness(best_world)
            else:
                best_world_fitness = -float("inf")

            if best_world_fitness > overall_best_world_fitness:
                overall_best_worlds = best_world

            c += 1
            report_method(f"  Processed: {c/n * 100:.1f}% ({grid_entry.name}: {best_world_fitness})")

        if overall_best_worlds is None:
            return grid, overall_best_world_fitness

        return overall_best_worlds, overall_best_world_fitness

    @staticmethod
    def _hill_climbing_move_around_process_building(
        grid: Grid,
        active_cord: tuple,
        grid_entry: GridEntry,
        report_method = print
    ) -> Grid | None:
        """
        Finds the best neighboring grid produced by moving one building.

        :param grid: Grid representation of the factory.
        :param active_cord: Coordinates of the moved building.
        :param grid_entry: Grid entry of the moved building.
        :return: Best neighboring grid if an improvement exists.
        """

        best_grid = None
        best_world_fitness = Evolution.fitness(grid)

        for new_cord in Evolution.get_changed_cords(active_cord):
            try:
                new_grid = copy.deepcopy(grid)
                neighbors = new_grid.erase_factory(active_cord)

                if grid_entry.entry_type == GridEntryTypes.Factory:
                    new_grid.add_factory(
                        new_cord,
                        grid_entry.name,
                        [sur for sur in FactoryUtil.get_cords(new_cord) if sur != new_cord]
                    )
                else:
                    new_grid.add_source(
                        new_cord,
                        grid_entry.name,
                    )

                if grid_entry.entry_type == GridEntryTypes.Factory:
                    active_cords = [c for c in FactoryUtil.get_cords(new_cord)]
                    active_is_in_cords = FactoryUtil.get_cords_lambda(new_cord)
                else:
                    active_cords = [new_cord]
                    active_is_in_cords = lambda x: x == new_cord

                connection_pairs = []
                for neighbor, direction in neighbors:
                    neighbor_type = new_grid.data[neighbor].entry_type

                    if neighbor_type == GridEntryTypes.Factory:
                        nei_cords = [c for c in FactoryUtil.get_cords(neighbor)]
                        nei_is_in_cords = FactoryUtil.get_cords_lambda(neighbor)
                    else:
                        nei_cords = [neighbor]
                        nei_is_in_cords = lambda x: x == neighbor

                    if direction:
                        GraphToMatrix.find_path(
                            new_cord,
                            active_cords,
                            active_is_in_cords,
                            neighbor,
                            nei_cords,
                            nei_is_in_cords,
                            new_grid
                        )

                        connection_pairs.append((
                            active_cords,
                            nei_cords,
                            GridEntryTransportationId.create_belt_id(
                                new_grid.data[new_cord].get_id_text(),
                                new_grid.data[neighbor].get_id_text()
                            )
                        ))
                    else:
                        GraphToMatrix.find_path(
                            neighbor,
                            nei_cords,
                            nei_is_in_cords,
                            new_cord,
                            active_cords,
                            active_is_in_cords,
                            new_grid
                        )

                        connection_pairs.append((
                            nei_cords,
                            active_cords,
                            GridEntryTransportationId.create_belt_id(
                                new_grid.data[neighbor].get_id_text(),
                                new_grid.data[new_cord].get_id_text()
                            )
                        ))

                new_fitness = Evolution.fitness(
                    grid=new_grid,
                    test_connection=True,
                    connection_pair=connection_pairs
                )

                if best_grid is None or new_fitness > best_world_fitness:
                    best_grid = new_grid
                    best_world_fitness = new_fitness
            except Exception as e:
                if Evolution.SHOW_REASONS_FOR_INDIVIDUAL_FAILURE:
                    report_method(f"  Individual failed because of \"{e}\"")

        return best_grid

    #TODO: maybe add to the GUI characteristic vector of enabled fitness parameters, so user can choose which parameters to use for fitness evaluation, so the evolution can be more flexible and user can choose what is important for him
    @staticmethod
    def fitness(
        grid: Grid,
        test_connection: bool = True,
        connection_pair: list[tuple[list[tuple], list[tuple], str]] = []
    ) -> int | float:
        """
        Computes the fitness value of the provided grid.

        :param grid: Grid representation of the factory.
        :param test_connection: Whether factory connections should be validated.
        :param connection_pair: Connections which should be present in the grid.
        :return: Fitness value of the provided grid.

        size -> scribed rectangle
        belts -> number of belts (or maybe not only belts but all structures)
        layers -> if factories are int "nice" layers
        belts structure -> if structure of the belts is messy or have "nice" curves

        belts should starts from middle -> more esthetic fitness
        """

        fitness = 0

        fitness -= grid.get_area()
        fitness -= grid.get_used_block() / 1.5
        fitness += grid.get_number_of_pointing_to_center() * 10
        fitness -= grid.get_distances_from_center()

        if test_connection:
            if not Evolution.fitness_connection(grid, connection_pair):
                fitness -= float("inf")

        #return 1 / fitness
        return fitness

    @staticmethod
    def fitness_connection(
        grid: Grid,
        connection_pair: list[tuple[list[tuple], list[tuple], str]]
    ) -> bool:
        """
        Returns whether all expected connections exist in the provided grid.

        :param grid: Grid representation of the factory.
        :param connection_pair: Connections which should be present in the grid.
        :return: Whether all expected connections exist in the provided grid.
        """

        #TODO: Add connection checking that if we check for underground, then they are really underground
        for a, b, belt_id in connection_pair:
            if not grid.exists_path(a, b, belt_id):
                return False

        return True


if __name__ == "__main__":
    pass
