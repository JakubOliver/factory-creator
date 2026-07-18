import copy

from factory_creator.evolution import Evolution
from factory_creator.grid import Grid
from factory_creator.util.factorio_const import FactorioConst


def test_get_changed_cords_uses_grid_moves():
    assert list(Evolution.get_changed_cords((10, 20))) == [
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

    assert Evolution.fitness_connection(grid, [([(0, 0)], [(0, 2)], belt_id)])
    assert not Evolution.fitness_connection(grid, [([(0, 2)], [(0, 0)], "missing")])


def test_fitness_penalizes_missing_connections():
    grid = Grid()
    grid.add_source((0, 0), "a")
    grid.add_source((0, 2), "b")

    assert Evolution.fitness(grid, test_connection=False) > -float("inf")
    assert Evolution.fitness(grid, connection_pair=[([(0, 0)], [(0, 2)], "missing")]) == -float("inf")


def test_fitness_penalizes_long_handed_inserter_more_than_normal_inserter():
    def grid_with(inserter_name):
        grid = Grid()
        grid.add_source((0, 0), "source")
        grid.add_source((0, 2), "target")
        grid.add_transportation(
            (0, 1), inserter_name, 0, (0, 0), (0, 2)
        )
        return grid

    normal_fitness = Evolution.fitness(
        grid_with(FactorioConst.INSERTER), test_connection=False
    )
    long_fitness = Evolution.fitness(
        grid_with(FactorioConst.LONG_HANDED_INSERTER), test_connection=False
    )

    assert long_fitness == normal_fitness - 2


def test_evol_delegates_to_hill_climb(monkeypatch):
    grid = Grid()
    returned = Grid()
    calls = {}

    def fake_hill_climb(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        return returned

    monkeypatch.setattr(Evolution, "hill_climb", fake_hill_climb)
    # monkeypatch temporarily swaps hill_climb for a fake function,
    # so we can verify that evol only forwards the call and returns the same value.

    assert Evolution.evol(grid, iteration=3, stagnation_break=2, report_method=lambda _: None) is returned
    assert calls["args"][0] is grid
    assert calls["kwargs"]["iteration"] == 3
    assert calls["kwargs"]["stagnation_break"] == 2


def test_hill_climb_can_return_presentation(monkeypatch):
    grid = Grid()
    grid.add_source((0, 0), "a")

    # monkeypatch replaces internal logic with stubs, so this test focuses only
    # on the presentation output that hill_climb returns when requested.
    monkeypatch.setattr(Evolution, "fitness", lambda *args, **kwargs: 0)
    monkeypatch.setattr(Evolution, "_hill_climbing_move_around_process_building", lambda *args, **kwargs: None)
    monkeypatch.setattr(Evolution, "GENERATION_PRINT", False)

    new_grid = Evolution.hill_climb(
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

    new_grid = Evolution.hill_climb(
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

    new_grid = Evolution.hill_climb(
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

    new_grid = Evolution.hill_climb(
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

    new_grid = Evolution.hill_climb(
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
