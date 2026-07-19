import copy

from factory_creator.evolution import Evolution
from factory_creator.evolution.mutations.move_building_mutation import MoveBuildingMutation
from factory_creator.evolution.mutations.move_subgraph_mutation import MoveSubgraphMutation
from factory_creator.evolution.mutations.mutation import Mutation, MutationCandidate
from factory_creator.evolution.fitness import Fitness
from factory_creator.evolution.fitness_aspects import (
    AreaAspect,
    ConnectionValidityAspect,
    DistanceFromCenterAspect,
    FitnessContext,
    InserterCostAspect,
    PointingToCenterAspect,
    UsedBlockAspect,
)
from factory_creator.grid import Grid
from factory_creator.evolution.hill_climbing import HillClimbing
from factory_creator.util.factorio_const import FactorioConst


def create_fitness():
    return Fitness([
        AreaAspect(),
        UsedBlockAspect(),
        PointingToCenterAspect(),
        DistanceFromCenterAspect(),
        InserterCostAspect(),
        ConnectionValidityAspect(),
    ])


def evolution_plugins():
    return (
        [MoveBuildingMutation(), MoveSubgraphMutation()],
        create_fitness().aspects,
    )


def create_hill_climbing():
    return HillClimbing(
        mutations=[MoveBuildingMutation(show_failure_reasons=True)],
        fitness=create_fitness(),
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

    fitness = create_fitness()
    assert fitness.evaluate(
        FitnessContext(grid, connection_pairs=[([(0, 0)], [(0, 2)], belt_id)])
    ) > -float("inf")
    assert fitness.evaluate(
        FitnessContext(grid, connection_pairs=[([(0, 2)], [(0, 0)], "missing")])
    ) == -float("inf")


def test_fitness_penalizes_missing_connections():
    grid = Grid()
    grid.add_source((0, 0), "a")
    grid.add_source((0, 2), "b")

    fitness = create_fitness()
    assert fitness.evaluate(FitnessContext(grid, test_connection=False)) > -float("inf")
    assert fitness.evaluate(
        FitnessContext(
            grid,
            connection_pairs=[([(0, 0)], [(0, 2)], "missing")],
        )
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

    fitness = create_fitness()
    normal_fitness = fitness.evaluate(
        FitnessContext(grid_with(FactorioConst.INSERTER), test_connection=False)
    )
    long_fitness = fitness.evaluate(
        FitnessContext(
            grid_with(FactorioConst.LONG_HANDED_INSERTER),
            test_connection=False,
        )
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

    mutations, aspects = evolution_plugins()
    assert Evolution.evolve(
        grid,
        mutations,
        aspects,
        iteration=3,
        stagnation_break=2,
        report_method=lambda _: None,
    ) is returned
    assert calls["args"][1] is grid
    assert calls["kwargs"]["iteration"] == 3
    assert calls["kwargs"]["stagnation_break"] == 2


def test_hill_climbing_passes_grid_to_each_mutation():
    grid = Grid()
    grid.add_source((0, 0), "a")
    received_grids = []

    class EmptyMutation(Mutation):
        def _generate(self, grid, report_method, error_report_method=None):
            received_grids.append(grid)
            yield from ()

        def get_cache_key(self, value):
            return 0

    supervisor = HillClimbing(
        [EmptyMutation(), EmptyMutation()],
        create_fitness(),
        generation_print=False,
    )

    supervisor.evolve(grid, iteration=1, report_method=lambda _: None)

    assert received_grids == [grid, grid]


def test_fitness_cache_reuses_result_for_same_key():
    grid = Grid()
    evaluated_grids = []
    fitness = 41

    class CountingFitness:
        def evaluate(self, context):
            nonlocal fitness
            evaluated_grids.append(context.grid)
            fitness += 1
            return fitness

    supervisor = HillClimbing([], CountingFitness(), generation_print=False)

    first_result = supervisor._evaluate_fitness(grid, cache_key="same-layout")
    second_result = supervisor._evaluate_fitness(grid, cache_key="same-layout")

    assert first_result == second_result == 42
    assert evaluated_grids == [grid]


def test_fitness_cache_can_be_disabled():
    grid = Grid()
    evaluation_count = 0

    class CountingFitness:
        def evaluate(self, context):
            nonlocal evaluation_count
            evaluation_count += 1
            return evaluation_count

    supervisor = HillClimbing(
        [],
        CountingFitness(),
        generation_print=False,
        caching_enabled=False,
    )

    assert supervisor._evaluate_fitness(grid, cache_key="same-layout") == 1
    assert supervisor._evaluate_fitness(grid, cache_key="same-layout") == 2
    assert evaluation_count == 2


def test_fitness_without_cache_key_is_not_cached():
    grid = Grid()
    evaluation_count = 0

    class CountingFitness:
        def evaluate(self, context):
            nonlocal evaluation_count
            evaluation_count += 1
            return evaluation_count

    supervisor = HillClimbing([], CountingFitness(), generation_print=False)

    assert supervisor._evaluate_fitness(grid) == 1
    assert supervisor._evaluate_fitness(grid) == 2
    assert evaluation_count == 2


def test_fitness_cache_is_reset_between_evolve_runs():
    grid = Grid()
    evaluation_count = 0

    class CountingFitness:
        def evaluate(self, context):
            nonlocal evaluation_count
            evaluation_count += 1
            return evaluation_count

    supervisor = HillClimbing([], CountingFitness(), generation_print=False)

    supervisor.evolve(grid, iteration=2, stagnation_break=2)
    assert evaluation_count == 1

    supervisor.evolve(grid, iteration=1, stagnation_break=1)
    assert evaluation_count == 2


def test_supervisor_selects_best_candidate():
    original = Grid()
    original.add_source((0, 0), "original")
    worse = copy.deepcopy(original)
    better = copy.deepcopy(original)

    class CandidateMutation(Mutation):
        def _generate(self, grid, report_method, error_report_method=None):
            yield MutationCandidate(worse)
            yield MutationCandidate(better)

        def get_cache_key(self, value):
            return 0

    class StubFitness:
        def evaluate(self, context):
            return {
                id(original): 0,
                id(worse): 1,
                id(better): 2,
            }[id(context.grid)]

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


def test_move_subgraph_mutation_rebuilds_grid_and_connections():
    grid = Grid()
    grid.add_source((0, 0), "source")
    grid.add_source((3, 0), "target")
    grid.add_transportation(
        (1, 0),
        FactorioConst.TRANSPORT_BELT,
        4,
        (0, 0),
        (3, 0),
    )
    grid.add_transportation(
        (2, 0),
        FactorioConst.TRANSPORT_BELT,
        4,
        (0, 0),
        (3, 0),
    )

    candidates = list(
        MoveSubgraphMutation(show_failure_reasons=False).generate(
            grid,
            report_method=lambda _: None,
        )
    )

    assert len(candidates) == MoveSubgraphMutation.HOW_MANY_GENERATE_IN_ONE_GENERATION
    assert all(isinstance(candidate, MutationCandidate) for candidate in candidates)
    assert all(
        create_fitness().evaluate(
            FitnessContext(
                candidate.grid,
                connection_pairs=candidate.connection_pairs,
            )
        ) > -float("inf")
        for candidate in candidates
    )


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
