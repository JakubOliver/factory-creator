import copy

class Evolution:
    generation_print = True

    @staticmethod
    def evol(grid, iteration = float("inf"), stagnation_break = 10):
        Evolution.hill_climb(
            grid,
            iteration = iteration,
            stagnation_break = stagnation_break
        )

    @staticmethod
    def hill_climb(grid, iteration = float("inf"), stagnation_break = 10):
        active_iteration = 0
        stagnation_streak = 0
        last_fitness = None

        while active_iteration < iteration and stagnation_streak < stagnation_break:
            fitness = Evolution.fitness(grid)

            if Evolution.generation_print:
                print("----------- NEXT GENERATION -------------")
                print(fitness)
                print(grid)
                print([entry.get_detailed_name() for entry in grid.data.values()])

            for cord, factory in grid.get_factories():
                new_grid = copy.deepcopy(grid)

            if fitness == last_fitness:
                stagnation_streak += 1
            else:
                stagnation_streak = 0

            last_fitness = fitness
            active_iteration += 1

    @staticmethod
    def fitness(grid):

        """
        size -> scribed rectangle
        belts -> number of belts (or maybe not only belts but all structures)
        layers -> if factories are int "nice" layers
        belts structure -> if structure of the belts is messy or have "nice" curves
        """

        fitness = 0

        fitness += grid.get_area()
        fitness += grid.get_used_block()

        #return 1 / fitness
        return -fitness