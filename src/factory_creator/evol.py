class Evolution:
    @staticmethod
    def evol(grid, iteration = float("inf"), stagnation_break = 10):
        Evolution.hill_climb(
            grid,
            iteration = iteration,
            stagnation_break = stagnation_break
        )

    @staticmethod
    def hill_climb(grid, iteration = float("inf"), stagnation_break = 10):
        pass

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

    @staticmethod
    def get_area(grid):
        return grid.get_area()