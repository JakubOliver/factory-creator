import pytest
from pyrsistent import pset

from factory_creator.graph_to_matrix import AStartNode, GraphToMatrix, VisitedMatrix
from factory_creator.grid import Grid
from factory_creator.grid_entry import GridEntryTypes
from factory_creator.util.factorio_const import FactorioConst


def _grid_diagnostics(grid, node=None):
    grid_text = str(grid) if len(grid) else "<empty grid>"
    path = node.reconstruct_path() if node is not None else None
    path_text = path if path is not None else "<no A* path available>"
    return f"\nGenerated grid:\n{grid_text}\nA* path:\n{path_text}"


def _build_and_validate_path(start, target, obstacles):
    """Build one connection and check the invariants expected from a valid grid."""
    grid = Grid()
    grid.add_source(start, "start")
    grid.add_source(target, "target")

    for index, cord in enumerate(obstacles):
        grid.add_source(cord, f"obstacle-{index}")

    try:
        node, _ = GraphToMatrix.a_star(
            [start], lambda cord: cord == target, [target], grid
        )
        grid._test_path = node.reconstruct_path()
        GraphToMatrix.find_path(
            start,
            [start],
            lambda cord: cord == start,
            target,
            [target],
            lambda cord: cord == target,
            grid,
        )
    except Exception as error:
        pytest.fail(f"Grid generation failed: {error}{_grid_diagnostics(grid)}")

    diagnostics = _grid_diagnostics(grid)

    connection_id = f"{grid[start].get_id_text()}-{grid[target].get_id_text()}"
    transportation = {
        cord: entry
        for cord, entry in grid.data.items()
        if entry.entry_type == GridEntryTypes.Transportation
        and entry.get_id_text() == connection_id
    }

    assert transportation, f"The generated grid contains no transportation path{diagnostics}"
    assert grid.exists_path([start], [target], connection_id), diagnostics
    assert all(cord not in obstacles for cord in transportation), diagnostics
    assert all(entry.orientation in (0, 4, 8, 12) for entry in transportation.values()), diagnostics
    assert sum(entry.name == FactorioConst.INSERTER for entry in transportation.values()) == 2, diagnostics

    underground_inputs = [
        entry for entry in transportation.values()
        if entry.underground_belt_type == FactorioConst.UNDERGROUND_BELT_INPUT
    ]
    underground_outputs = [
        entry for entry in transportation.values()
        if entry.underground_belt_type == FactorioConst.UNDERGROUND_BELT_OUTPUT
    ]

    assert len(underground_inputs) == len(underground_outputs), diagnostics

    return grid


def _square_perimeter(radius):
    return (
        {(x, y) for x in range(-radius, radius + 1) for y in (-radius, radius)}
        | {(x, y) for x in (-radius, radius) for y in range(-radius, radius + 1)}
    )


def _assert_underground_belt_is_used(grid, minimum_pairs=1):
    underground_belts = [
        entry
        for entry in grid.data.values()
        if entry.name == FactorioConst.FAST_UNDERGROUND_BELT
    ]

    diagnostics = _grid_diagnostics(grid)
    assert len(underground_belts) >= minimum_pairs * 2, diagnostics
    assert len(underground_belts) % 2 == 0, diagnostics


def _closed_one_tile_corridor(length, blocked_tiles):
    wall_thickness = Grid.UNDERGROUND_MOVE_LENGTH
    grid = Grid()

    obstacles = {
        (x, y)
        for x in range(-wall_thickness, wall_thickness + 1)
        for y in range(-wall_thickness, length + wall_thickness + 1)
        if x != 0 or y < 0 or y > length
    }
    obstacles |= {(0, y) for y in blocked_tiles}

    for index, cord in enumerate(obstacles):
        grid.add_source(cord, f"wall-{index}")

    return grid


def _assert_a_star_cannot_find_path(grid, start, target):
    try:
        node, _ = GraphToMatrix.a_star(
            [start], lambda cord: cord == target, [target], grid
        )
    except Exception as error:
        assert "Unable to find a path" in str(error), _grid_diagnostics(grid)
        return

    pytest.fail(
        "A* unexpectedly found a path"
        + _grid_diagnostics(grid, node)
    )


def test_a_star_node_helpers_detect_start_and_underground_step():
    start = AStartNode((0, 0), 0, 0, 0, 0, None, path_set=pset(), is_start=True)
    adjacent = AStartNode((0, 1), 1, 1, 0, 1, start, path_set=start.path_set)
    underground = AStartNode((0, 5), 5, 5, 0, 2, adjacent, path_set=adjacent.path_set)

    assert adjacent.is_after_start()
    assert adjacent.same_direction_is_needed()
    assert underground.is_underground_belt_end()
    assert underground.same_direction_is_needed()
    assert (0, 5) in underground.path_set


def test_visited_matrix_tracks_a_star_keys():
    matrix = VisitedMatrix()
    key = GraphToMatrix.get_a_star_visited_key((1, 2), 4, 100)

    matrix[key] = 7

    assert key == ((1, 2), 4, GraphToMatrix.A_STAR_STREAK_THRESHOLD + 1)
    assert key in matrix
    assert len(matrix) == 1


def test_distance_and_orientation_helpers():
    assert GraphToMatrix.get_enumeration_to_orientation(3) == 12
    assert GraphToMatrix.get_orientation_in_opposite_direction(12) == 4
    assert GraphToMatrix.distance_between_basis_vectors((0, 0), (0, 5)) == 5
    assert GraphToMatrix.cord_after_previous_in_direction((0, 5), (0, 2)) == (0.0, 4.0)

    with pytest.raises(ValueError):
        GraphToMatrix.distance_between_basis_vectors((0, 0), (1, 1))


def test_get_moves_respects_visited_keys_and_forced_direction():
    start = AStartNode((0, 0), 0, 0, 0, 0, None, path_set=pset(), is_start=True)
    visited = VisitedMatrix()
    visited[GraphToMatrix.get_a_star_visited_key((0, 1), 0, 1)] = 1

    moves = list(GraphToMatrix.get_moves(start, visited, return_enumeration=True))

    assert moves == [(1, 0, (-1, 0)), (2, 0, (0, -1)), (3, 0, (1, 0))]

    after_start = AStartNode((0, 1), 1, 1, 0, 1, start, path_set=start.path_set)
    assert list(GraphToMatrix.get_moves(after_start, VisitedMatrix(), return_enumeration=True)) == [
        (0, 2, (0, 2))
    ]


@pytest.mark.xfail(reason="bfs still calls get_moves with the pre-AStartNode tuple API")
def test_bfs_finds_successor_around_obstacle():
    grid = Grid()
    grid.add_source((0, 1), "block")

    found, visited = GraphToMatrix.bfs([(0, 0)], lambda cord: cord == (0, 2), grid)

    diagnostics = _grid_diagnostics(grid)
    assert found == (0, 2), diagnostics
    assert visited[(0, 1)] == -1, diagnostics
    assert visited[(0, 2)] > 1, diagnostics


def test_a_star_finds_simple_path_and_reports_unreachable_target():
    grid = Grid()

    node, visited = GraphToMatrix.a_star([(0, 0)], lambda cord: cord == (0, 3), [(0, 3)], grid)

    diagnostics = _grid_diagnostics(grid, node)
    assert node.cord == (0, 3), diagnostics
    assert len(visited) > 0, diagnostics

    blocked = Grid()
    blocked.add_source((0, 1), "block")
    blocked.add_source((-1, 0), "block")
    blocked.add_source((0, -1), "block")
    blocked.add_source((1, 0), "block")

    _assert_a_star_cannot_find_path(blocked, (0, 0), (0, 2))


@pytest.mark.parametrize(
    ("start", "target", "obstacles"),
    [
        pytest.param((0, 0), (0, 8), set(), id="straight-horizontal"),
        pytest.param((0, 0), (8, 0), set(), id="straight-vertical"),
        pytest.param((0, 0), (0, -8), set(), id="negative-direction"),
        pytest.param((0, 0), (0, 8), {(0, 4)}, id="single-blocker"),
        pytest.param(
            (0, 0),
            (0, 10),
            {(x, 5) for x in range(-3, 4)} - {(2, 5)},
            id="wall-with-offset-gap",
        ),
        pytest.param(
            (0, 0),
            (0, 10),
            {(-1, y) for y in range(2, 8)} | {(1, y) for y in range(2, 8)},
            id="narrow-corridor",
        ),
        pytest.param(
            (0, 0),
            (0, 10),
            {(-2, y) for y in range(2, 9)}
            | {(2, y) for y in range(2, 9)}
            | {(x, 8) for x in range(-2, 3)},
            id="u-shaped-dead-end",
        ),
        pytest.param(
            (0, 0),
            (0, 12),
            {(x, y) for x in range(-2, 3) for y in (4, 8)},
            id="two-solid-walls",
        ),
        pytest.param(
            (-8, -8),
            (2, 3),
            {(-4, y) for y in range(-8, 2)} - {(-4, -2)},
            id="mixed-sign-coordinates",
        ),
        pytest.param(
            (0, 0),
            (8, 8),
            {(x, 3) for x in range(-1, 8)} | {(5, y) for y in range(3, 9)},
            id="l-shaped-barrier",
        ),
        pytest.param(
            (0, 0),
            (0, 12),
            {(0, y) for y in range(3, 10)},
            id="long-blocked-direct-route",
        ),
        pytest.param(
            (0, 0),
            (10, 0),
            {(x, y) for x in range(3, 8) for y in range(-1, 2)},
            id="thick-obstacle",
        ),
    ],
)
def test_generated_grid_is_valid_for_difficult_a_star_scenarios(start, target, obstacles):
    _build_and_validate_path(start, target, obstacles)


def test_path_uses_underground_belts_to_escape_closed_square():
    grid = _build_and_validate_path(
        start=(0, 0),
        target=(0, 10),
        obstacles=_square_perimeter(radius=4),
    )

    _assert_underground_belt_is_used(grid)


def test_path_uses_underground_belts_to_escape_nested_closed_squares():
    grid = _build_and_validate_path(
        start=(0, 0),
        target=(0, 12),
        obstacles=_square_perimeter(radius=3) | _square_perimeter(radius=7),
    )

    _assert_underground_belt_is_used(grid, minimum_pairs=2)


def test_a_star_cannot_escape_corridor_blocked_beyond_underground_range():
    start = (0, 0)
    target = (0, 20)
    grid = _closed_one_tile_corridor(
        length=target[1],
        blocked_tiles=range(5, 12),
    )

    _assert_a_star_cannot_find_path(grid, start, target)


def test_a_star_rejects_overlapping_underground_endpoints():
    start = (0, 0)
    target = (0, 20)
    grid = _closed_one_tile_corridor(
        length=target[1],
        # Both four-tile obstacles fit within underground range on their own,
        # but the only free tile between them cannot hold an output and another input.
        blocked_tiles=(*range(4, 8), *range(9, 13)),
    )

    _assert_a_star_cannot_find_path(grid, start, target)


def test_adjacent_underground_output_and_input_are_allowed():
    start = (0, 0)
    target = (0, 20)
    grid = _closed_one_tile_corridor(
        length=target[1],
        # Tiles 8 and 9 hold the first output and the second input.
        blocked_tiles=(*range(4, 8), *range(10, 14)),
    )
    grid.add_source(start, "start")
    grid.add_source(target, "target")

    try:
        node, _ = GraphToMatrix.a_star(
            [start], lambda cord: cord == target, [target], grid
        )
        grid._test_path = node.reconstruct_path()
        GraphToMatrix.find_path(
            start,
            [start],
            lambda cord: cord == start,
            target,
            [target],
            lambda cord: cord == target,
            grid,
        )
    except Exception as error:
        pytest.fail(f"Grid generation failed: {error}{_grid_diagnostics(grid)}")

    _assert_underground_belt_is_used(grid, minimum_pairs=2)


def test_get_number_of_sources_reads_graph_labels():
    import networkx

    graph = networkx.DiGraph()
    graph.add_node("a", label="iron_source")
    graph.add_node("b", label="gear")

    assert GraphToMatrix.get_number_of_sources(graph) == 1
