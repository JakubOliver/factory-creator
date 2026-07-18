import copy

from factory_creator.evolution import Evolution
from factory_creator.evolution.mutation import MoveBuildingMutation, MutationCandidate
from factory_creator.evolution.fitness import Fitness
from factory_creator.grid import Grid
from factory_creator.evolution.hill_climbing import HillClimbing
from factory_creator.util.factorio_const import FactorioConst


def create_hill_climbing():
    return HillClimbing(
        mutations=[MoveBuildingMutation(show_failure_reasons=True)],
        fitness=Fitness(),
        generation_print=False,
    )


def test_get_changed_cords_uses_grid_moves():
    assert list(MoveBuildingMutation._get_changed_cords((10, 20))) == [
        (10, 21),
        (9, 20),
        (10, 19),
        (11, 20),
    ]


def test_fitness_connection_checks_all_expected_paths():
    grid = Grid()
    grid.add_source((0, 0), "a")
    grid.add_source((0, 2), "b")
    grid.add_transportation((0, 1), FactorioConst.TRANSPORT_BELT, 0, (0, 0), (0, 2))
    belt_id = grid[(0, 1)].get_id_text()

    fitness = Fitness()
    assert fitness.evaluate(
        grid,
        connection_pair=[([(0, 0)], [(0, 2)], belt_id)],
    ) > -float("inf")
    assert fitness.evaluate(
        grid,
        connection_pair=[([(0, 2)], [(0, 0)], "missing")],
    ) == -float("inf")


def test_fitness_penalizes_missing_connections():
    grid = Grid()
    grid.add_source((0, 0), "a")
    grid.add_source((0, 2), "b")

    fitness = Fitness()
    assert fitness.evaluate(grid, test_connection=False) > -float("inf")
    assert fitness.evaluate(
        grid,
        connection_pair=[([(0, 0)], [(0, 2)], "missing")],
    ) == -float("inf")


def test_fitness_penalizes_long_handed_inserter_more_than_normal_inserter():
    def grid_with(inserter_name):
        grid = Grid()
        grid.add_source((0, 0), "source")
        grid.add_source((0, 2), "target")
        grid.add_transportation(
            (0, 1), inserter_name, 0, (0, 0), (0, 2)
        )
        return grid

    fitness = Fitness()
    normal_fitness = fitness.evaluate(
        grid_with(FactorioConst.INSERTER), test_connection=False
    )
    long_fitness = fitness.evaluate(
        grid_with(FactorioConst.LONG_HANDED_INSERTER), test_connection=False
    )

    assert long_fitness == normal_fitness - 2


def test_evolution_delegates_to_hill_climbing(monkeypatch):
    grid = Grid()
    returned = Grid()
    calls = {}

    def fake_evolve(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        return returned

    monkeypatch.setattr(HillClimbing, "evolve", fake_evolve)
    # monkeypatch temporarily swaps hill_climb for a fake function,
    # so we can verify that evol only forwards the call and returns the same value.

    assert Evolution.evolve(grid, iteration=3, stagnation_break=2, report_method=lambda _: None) is returned
    assert calls["args"][1] is grid
    assert calls["kwargs"]["iteration"] == 3
    assert calls["kwargs"]["stagnation_break"] == 2


def test_hill_climbing_passes_grid_to_each_mutation():
    grid = Grid()
    grid.add_source((0, 0), "a")
    received_grids = []

    class EmptyMutation:
        def generate(self, grid, report_method):
            received_grids.append(grid)
            return iter(())

    supervisor = HillClimbing(
        [EmptyMutation(), EmptyMutation()],
        Fitness(),
        generation_print=False,
    )

    supervisor.evolve(grid, iteration=1, report_method=lambda _: None)

    assert received_grids == [grid, grid]


def test_supervisor_selects_best_candidate():
    original = Grid()
    original.add_source((0, 0), "original")
    worse = copy.deepcopy(original)
    better = copy.deepcopy(original)

    class CandidateMutation:
        def generate(self, grid, report_method):
            yield MutationCandidate(worse)
            yield MutationCandidate(better)

    class StubFitness:
        def evaluate(self, grid, **kwargs):
            return {id(original): 0, id(worse): 1, id(better): 2}[id(grid)]

    supervisor = HillClimbing(
        [CandidateMutation()],
        StubFitness(),
        generation_print=False,
    )

    selected = supervisor.evolve(
        original,
        iteration=1,
        report_method=lambda _: None,
    )

    assert selected is better


def test_hill_climb_can_return_presentation():
    grid = Grid()
    grid.add_source((0, 0), "a")

    new_grid = create_hill_climbing().evolve(
        copy.deepcopy(grid),
        iteration=1,
        stagnation_break=1,
        create_presentation=False,
        report_method=lambda _: None,
    )

    assert isinstance(new_grid, Grid)
    assert new_grid == grid

def test_hill_climb_correct_climb():
    # 1              
    # XXXXXXXXXX2
    grid = Grid()
    grid.add_source((0, 1), "a")
    grid.add_source((10, 0), "b")
    for x in range(10):
        grid.add_transportation((x, 0), FactorioConst.TRANSPORT_BELT, 0, (0, 1), (10, 0))

    new_grid = create_hill_climbing().evolve(
        copy.deepcopy(grid),
        iteration=1,
        stagnation_break=1,
        create_presentation=False,
        report_method=print,
    )

    assert isinstance(new_grid, Grid)
    assert grid.get_area() != new_grid.get_area(), print(new_grid)
    assert grid.get_area() == 22, print(grid)
    assert new_grid.get_area() == 11, print(new_grid)
    assert grid.get_number_of_factories() == 2
    assert new_grid.get_number_of_factories() == 2

def test_hill_climb_correct_climb2():          
    # 1XXXXXXXXXX2
    grid = Grid()
    grid.add_source((0, 0), "a")
    grid.add_source((10, 0), "b")
    for x in range(1,10):
        grid.add_transportation((x, 0), FactorioConst.TRANSPORT_BELT, 0, (0, 0), (10, 0))

    new_grid = create_hill_climbing().evolve(
        copy.deepcopy(grid),
        iteration=1,
        stagnation_break=1,
        create_presentation=False,
        report_method=print,
    )

    assert isinstance(new_grid, Grid)
    assert grid.get_area() != new_grid.get_area(), print(new_grid)
    assert grid.get_area() == 11, print(grid)
    assert new_grid.get_area() == 10, print(new_grid)
    assert grid.get_number_of_factories() == 2
    assert new_grid.get_number_of_factories() == 2

def test_hill_climb_correct_climb_absolute_convergence():          
    # 1XXXXXXXXXX2 -> 1X2
    grid = Grid()
    grid.add_source((0, 0), "engine-unit_source")
    grid.add_source((10, 0), "engine-unit_source")
    for x in range(1,10):
        grid.add_transportation((x, 0), FactorioConst.TRANSPORT_BELT, 0, (0, 0), (10, 0))

    new_grid = create_hill_climbing().evolve(
        copy.deepcopy(grid),
        iteration=100,
        stagnation_break=10,
        create_presentation=False,
        report_method=print,
    )

    assert isinstance(new_grid, Grid)
    assert grid.get_area() != new_grid.get_area(), print(new_grid)
    assert grid.get_area() == 11, print(grid)
    assert new_grid.get_area() == 3, print(new_grid)
    assert grid.get_number_of_factories() == 2
    assert new_grid.get_number_of_factories() == 2

def test_hill_climb_correct_climb_absolute_convergence2():          
    # 1
    # XXXXXXXXXX2 -> 1X2 or rotation
    grid = Grid()
    grid.add_source((0, 1), "engine-unit_source")
    grid.add_source((10, 0), "engine-unit_source")
    for x in range(10):
        grid.add_transportation((x, 0), FactorioConst.TRANSPORT_BELT, 0, (0, 1), (10, 0))

    new_grid = create_hill_climbing().evolve(
        copy.deepcopy(grid),
        iteration=100,
        stagnation_break=10,
        create_presentation=False,
        report_method=print,
    )

    assert isinstance(new_grid, Grid)
    assert grid.get_area() != new_grid.get_area(), print(new_grid)
    assert grid.get_area() == 22, print(grid)
    assert new_grid.get_area() == 3, print(new_grid)
    assert grid.get_number_of_factories() == 2
    assert new_grid.get_number_of_factories() == 2
