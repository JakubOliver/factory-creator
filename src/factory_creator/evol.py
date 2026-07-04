import copy
import itertools

from .graph_to_matrix import GraphToMatrix
from .grid import *

class Evolution:
    generation_print = True

    @staticmethod
    def evol(
        grid,
        iteration = float("inf"),
        stagnation_break = 10
    ) -> Grid:
        return Evolution.hill_climb(
            grid,
            iteration = iteration,
            stagnation_break = stagnation_break
        )


    # TODO: REPAIR!!!!!! GET CORDS EXISTS AS CLASS FUNCTION IN FACTORY CLASS BUT AT THIS STAGE
    # I DO NOT HAVE ANY REFERENCES TO THEM
    # !!! THIS IS ONLY TEMPORARY SOLUTION TO SEE IF THE HILL CLIMBING WORKS
    @staticmethod
    def get_cords(cords):
        x, y = cords

        for dx, dy in itertools.product(range(0, 3), range(0, 3)):
            yield x + dx, y + dy

    @staticmethod
    def get_cords_lambda(cord):
        return lambda new_cord : any(new_cord == building_cord for building_cord in Evolution.get_cords(cord))

    @staticmethod
    def get_changed_cords(cord):
        for dx, dy in [(1,0), (0,1), (-1,0), (0,-1)]:
            yield cord[0] + dx, cord[1] + dy

    @staticmethod
    def hill_climb(grid: Grid, iteration = float("inf"), stagnation_break = 10) -> Grid:
        active_iteration = 0
        stagnation_streak = 0
        last_fitness = None

        while active_iteration < iteration and stagnation_streak < stagnation_break:
            fitness = Evolution.fitness(grid)

            if Evolution.generation_print:
                print("----------- NEXT GENERATION -------------")
                print(fitness)
                print(grid)
                #print([entry.get_detailed_name() for entry in grid.data.values()])

            best_worlds = None
            best_world_fitness = fitness
            for active_cord, grid_entry in grid.get_factories():
                #TODO: Add mechanism to do not allow merging or overlying of buildings
                for new_cord in Evolution.get_changed_cords(active_cord):
                    try:
                        new_grid = copy.deepcopy(grid)
                        neighbors = new_grid.erase_factory(active_cord)

                        #print(active_cord, new_cord)
                        if grid_entry.entry_type == GridEntryTypes.Factory:
                            new_grid.add_factory(
                                new_cord,
                                grid_entry.name,
                                [sur for sur in Evolution.get_cords(new_cord) if sur != new_cord]
                            )
                        else:
                            new_grid.add_source(
                                new_cord,
                                grid_entry.name,
                            )

                        if grid_entry.entry_type == GridEntryTypes.Factory:
                            active_cords = [c for c in Evolution.get_cords(new_cord)]
                            active_is_in_cords = Evolution.get_cords_lambda(new_cord)
                        else:
                            active_cords = [new_cord]
                            active_is_in_cords = lambda x: x == new_cord

                        connection_pairs = []
                        for neighbor, direction in neighbors:
                            neighbor_type = new_grid.data[neighbor].entry_type

                            if neighbor_type == GridEntryTypes.Factory:
                                nei_cords = [c for c in Evolution.get_cords(neighbor)]
                                nei_is_in_cords = Evolution.get_cords_lambda(neighbor)
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

                        #print(new_grid)
                        new_fitness = Evolution.fitness(
                            grid = new_grid,
                            test_connection = True,
                            connection_pair = connection_pairs
                        )
                        #print(new_fitness)
                        #print("--------------------")
                        if new_fitness > best_world_fitness:
                            best_worlds = new_grid
                    except Exception as e:
                        print(e)

            if best_worlds is not None:
                grid = best_worlds

            if best_world_fitness == last_fitness:
                stagnation_streak += 1
            else:
                stagnation_streak = 0

            last_fitness = best_world_fitness
            active_iteration += 1

        return grid

    @staticmethod
    def fitness(
        grid,
        test_connection = True,
        connection_pair = [] #TODO
    ):

        """
        size -> scribed rectangle
        belts -> number of belts (or maybe not only belts but all structures)
        layers -> if factories are int "nice" layers
        belts structure -> if structure of the belts is messy or have "nice" curves
        """

        fitness = 0

        fitness += grid.get_area()
        fitness += grid.get_used_block()

        if test_connection:
            if not Evolution.fitness_connection(grid, connection_pair):
                fitness += float("inf")

        #return 1 / fitness
        return -fitness

    @staticmethod
    def fitness_connection(grid, connection_pair):
        for a, b, id in connection_pair:
            if not grid.exists_path(a, b, id):
                return False

        return True

        #TODO: now tests only without underground block