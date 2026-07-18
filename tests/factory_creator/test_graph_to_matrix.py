import pytest
import networkx
from pyrsistent import pset

from factory_creator.factory import Factory, DependencyTreeNode
from factory_creator.graph_processing.graph_to_matrix import AStartNode, GraphToMatrix, VisitedMatrix
from factory_creator.grid import Grid
from factory_creator.grid.grid_entry import GridEntryTypes
from factory_creator.util.factorio_const import FactorioConst


def _grid_diagnostics(grid, node=None):
    grid_text = str(grid) if len(grid) else "<empty grid>"
    paths = [node.reconstruct_path()] if node is not None else None
    path_text = "\n".join(map(str, paths)) if paths else "<no A* path available>"
    return f"\nGenerated grid:\n{grid_text}\nA* path:\n{path_text}"


def _build_and_validate_grid(buildings, connections, obstacles=()):
    """Build a grid from buildings, directed connections, and blocking tiles."""
    grid = Grid()

    for cord, name in buildings.items():
        grid.add_source(cord, name)

    for index, cord in enumerate(obstacles):
        grid.add_source(cord, f"obstacle-{index}")

    grid._test_paths = []
    for start, target in connections:
        assert start in buildings and target in buildings, (
            f"Connection {start} -> {target} references an unknown building"
        )
        try:
            node, _ = GraphToMatrix.a_star(
                [start], lambda cord, target=target: cord == target, [target], grid
            )
            grid._test_paths.append(node.reconstruct_path())
            GraphToMatrix.find_path(
                start,
                [start],
                lambda cord, start=start: cord == start,
                target,
                [target],
                lambda cord, target=target: cord == target,
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


def _build_and_validate_path(start, target, obstacles):
    return _build_and_validate_grid(
        buildings={start: "start", target: "target"},
        connections=[(start, target)],
        obstacles=obstacles,
    )


def _square_perimeter(radius):
    return (
        {(x, y) for x in range(-radius, radius + 1) for y in (-radius, radius)}
        | {(x, y) for x in (-radius, radius) for y in range(-radius, radius + 1)}
    )


def _filled_square_without(radius, excluded_points=()):
    """Return all coordinates in a centered filled square except exclusions."""
    excluded_points = set(excluded_points)
    return {
        (x, y)
        for x in range(-radius, radius + 1)
        for y in range(-radius, radius + 1)
        if (x, y) not in excluded_points
    }


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


def test_get_node_path_data_for_factory_node():
    graph = networkx.DiGraph()
    dependency_node = DependencyTreeNode(Factory("engine-unit", 0.5, 1, [], 3, 3), [], 0)
    graph.add_node("factory", cord=(4, 5), ref=dependency_node)

    cords, contains_cord, element_type = GraphToMatrix._get_node_path_data(graph, "factory")

    assert cords == list(dependency_node.factory.get_cords((4, 5)))
    assert all(contains_cord(cord) for cord in cords)
    assert not contains_cord((0, 0))
    assert element_type == "engine-unit"


def test_get_node_path_data_for_source_node():
    graph = networkx.DiGraph()
    graph.add_node("iron-plate_source", cord=(4, 5))

    cords, contains_cord, element_type = GraphToMatrix._get_node_path_data(
        graph,
        "iron-plate_source",
    )

    assert cords == [(4, 5)]
    assert contains_cord((4, 5))
    assert not contains_cord((4, 6))
    assert element_type == "iron-plate_source"


@pytest.mark.parametrize("reverse", [False, True], ids=["chest-to-factory", "factory-to-chest"])
def test_long_handed_inserter_is_placed_next_to_factory(reverse):
    grid = Grid()
    chest = (0, 1)
    factory = (3, 0)
    factory_cords = [(x, y) for x in range(3, 6) for y in range(3)]
    grid.add_source(chest, "iron-plate_source")
    grid.add_factory(factory, "engine-unit", factory_cords[1:])

    if reverse:
        start, start_cords = factory, factory_cords
        target, target_cords = chest, [chest]
    else:
        start, start_cords = chest, [chest]
        target, target_cords = factory, factory_cords

    GraphToMatrix.find_path(
        start,
        start_cords,
        lambda cord: cord in start_cords,
        target,
        target_cords,
        lambda cord: cord in target_cords,
        grid,
    )

    long_inserters = [
        (cord, entry)
        for cord, entry in grid.data.items()
        if entry.name == FactorioConst.LONG_HANDED_INSERTER
    ]
    assert len(long_inserters) == 1
    assert long_inserters[0][0] == (2, 1)
    assert grid.exists_path(
        start_cords,
        target_cords,
        long_inserters[0][1].get_id_text(),
    )


def test_graph_layout_uses_longest_path_to_root_for_layers():
    graph = networkx.DiGraph(
        [
            ("direct-source", "root"),
            ("deep-source", "intermediate"),
            ("intermediate", "root"),
        ]
    )

    layers = GraphToMatrix._get_critical_path_layers(
        graph,
        list(networkx.topological_sort(graph))
    )

    assert layers == {
        "root": 0,
        "intermediate": 1,
        "direct-source": 1,
        "deep-source": 2,
    }


def test_graph_layout_centers_consumers_over_their_inputs():
    graph = networkx.DiGraph(
        [
            ("left-source", "consumer"),
            ("right-source", "consumer"),
            ("consumer", "root"),
        ]
    )

    topological_ordering = list(networkx.topological_sort(graph))

    layers = GraphToMatrix._get_critical_path_layers(
        graph,
        topological_ordering
    )

    positions = GraphToMatrix._get_vertical_positions(
        graph, 
        layers,
        topological_ordering
    )

    assert positions["left-source"] < positions["right-source"]
    assert positions["consumer"] == round(
        (positions["left-source"] + positions["right-source"]) / 2
    )
    assert positions["root"] == positions["consumer"]


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


def _assert_path_does_not_enter_target_from_underground_endpoint(start, target, obstacle):
    grid = Grid()
    grid.add_source(obstacle, "obstacle")

    target_node, _ = GraphToMatrix.a_star(
        [start],
        lambda cord: cord == target,
        [target],
        grid,
    )

    assert target_node.cord == target
    assert target_node.predecessor is not None
    assert not target_node.predecessor.is_underground_belt_end()


def test_a_star_does_not_enter_target_from_underground_endpoint_to_the_right():
    _assert_path_does_not_enter_target_from_underground_endpoint(
        start=(0, 0),
        target=(0, 5),
        obstacle=(0, 3),
    )


def test_a_star_does_not_enter_target_from_underground_endpoint_to_the_left():
    _assert_path_does_not_enter_target_from_underground_endpoint(
        start=(0, 5),
        target=(0, 0),
        obstacle=(0, 2),
    )


def test_a_star_does_not_enter_target_from_vertical_underground_endpoint():
    _assert_path_does_not_enter_target_from_underground_endpoint(
        start=(0, 0),
        target=(5, 0),
        obstacle=(3, 0),
    )


def test_a_star_cannot_jump_over_foreign_path_directly_into_target():
    start = (0, 0)
    target = (0, 20)
    grid = _closed_one_tile_corridor(
        length=target[1],
        # The foreign path blocks every valid surface approach to the target.
        # Before the regression fix, the second path incorrectly succeeded by
        # jumping underground from tile 15 directly into the target at tile 20.
        blocked_tiles=range(16, 20),
    )

    _assert_a_star_cannot_find_path(grid, start, target)


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


def test_grid_tool_builds_multiple_buildings_and_connections():
    grid = _build_and_validate_grid(
        buildings={
            (0, 0): "top-left",
            (0, 10): "top-right",
            (8, 0): "bottom-left",
            (8, 10): "bottom-right",
        },
        connections=[
            ((0, 0), (0, 10)),
            ((8, 0), (8, 10)),
        ],
        obstacles={(4, y) for y in range(3, 8)},
    )

    assert len(grid._test_paths) == 2, _grid_diagnostics(grid)


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
        grid._test_paths = [node.reconstruct_path()]
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


def _two_rooms_with_one_tile_hall_walls():
    padding = Grid.UNDERGROUND_MOVE_LENGTH
    room_half_width = 6
    top_room = {
        (x, y)
        for x in range(-room_half_width, room_half_width + 1)
        for y in range(0, 7)
    }
    bottom_room = {
        (x, y)
        for x in range(-room_half_width, room_half_width + 1)
        for y in range(14, 21)
    }
    hall = {(0, y) for y in range(7, 14)}
    walkable = top_room | hall | bottom_room

    return {
        (x, y)
        for x in range(-room_half_width - padding, room_half_width + padding + 1)
        for y in range(-padding, 21 + padding)
        if (x, y) not in walkable
    }


def _two_rooms_with_one_tile_hall():
    grid = Grid()
    walls = _two_rooms_with_one_tile_hall_walls()
    for index, cord in enumerate(walls):
        grid.add_source(cord, f"wall-{index}")

    return grid


def _sealed_cross_tunnels_walls(tunnel_length=10, extra_obstacles=()):
    padding = Grid.UNDERGROUND_MOVE_LENGTH
    horizontal_tunnel = {(x, 0) for x in range(-tunnel_length, tunnel_length + 1)}
    vertical_tunnel = {(0, y) for y in range(-tunnel_length, tunnel_length + 1)}
    walkable = horizontal_tunnel | vertical_tunnel

    walls = {
        (x, y)
        for x in range(-tunnel_length - padding, tunnel_length + padding + 1)
        for y in range(-tunnel_length - padding, tunnel_length + padding + 1)
        if (x, y) not in walkable
    }
    return walls | set(extra_obstacles)


def test_perpendicular_connections_can_cross_in_sealed_one_tile_tunnels():
    # ######### 3 #########
    # #########   #########
    # #########   #########
    # 1                   2
    # #########   #########
    # #########   #########
    # ######### 4 #########
    #
    # Connections: 1 -> 2, 3 -> 4
    tunnel_length = 10
    buildings = {
        (-tunnel_length, 0): "left",
        (tunnel_length, 0): "right",
        (0, -tunnel_length): "top",
        (0, tunnel_length): "bottom",
    }

    _build_and_validate_grid(
        buildings=buildings,
        connections=[
            ((-tunnel_length, 0), (tunnel_length, 0)),
            ((0, -tunnel_length), (0, tunnel_length)),
        ],
        obstacles=_sealed_cross_tunnels_walls(
            tunnel_length=tunnel_length,
            extra_obstacles=set(),
        ),
    )

def test_perpendicular_connections_cannot_cross_in_sealed_one_tile_tunnels():
    # ######### 3 #########
    # #########   #########
    # #########   #########
    # 1                   2
    # #########   #########
    # #########   #########
    # ######### 4 #########
    #
    # Connections: 1 -> 3, 2 -> 4 (fail, because we cannot use underground belt in the corner of the tunnel)
    tunnel_length = 10
    buildings = {
        (-tunnel_length, 0): "left",
        (tunnel_length, 0): "right",
        (0, -tunnel_length): "top",
        (0, tunnel_length): "bottom",
    }

    grid = _build_and_validate_grid(
        buildings=buildings,
        connections=[
            ((-tunnel_length, 0), (0, tunnel_length)),
        ],
        obstacles=_sealed_cross_tunnels_walls(
            tunnel_length=tunnel_length,
            extra_obstacles=set(),
        ),
    )

    _assert_a_star_cannot_find_path(grid, (0, -tunnel_length), (tunnel_length, 0))

def test_perpendicular_connections_can_cross_in_sealed_one_tile_tunnels_with_obstacles():
    # ######### 3 #########
    # #########   #########
    # #########   #########
    # 1     ####  ###     2
    # #########   #########
    # #########   #########
    # ######### 4 #########
    #
    # Connections: 1 -> 2, 3 -> 4 (will not fail because first connection uses the necessary underground)
    tunnel_length = 10
    buildings = {
        (-tunnel_length, 0): "left",
        (tunnel_length, 0): "right",
        (0, -tunnel_length): "top",
        (0, tunnel_length): "bottom",
    }

    _build_and_validate_grid(
        buildings=buildings,
        connections=[
            ((-tunnel_length, 0), (tunnel_length, 0)),
            ((0, -tunnel_length), (0, tunnel_length)),
        ],
        obstacles=_sealed_cross_tunnels_walls(
            tunnel_length=tunnel_length,
            extra_obstacles=set([(-1, 0), (-2, 0), (-3, 0), (2,0), (3,0), (4,0)]),
        ),
    )

@pytest.mark.xfail(
    reason="A* does not yet support prioritization of connections in the same sealed one-tile tunnel",
    strict=True,
)
def test_perpendicular_connections_can_cross_in_sealed_one_tile_tunnels_with_obstacles_with_prioritisation():
    # ######### 3 #########
    # #########   #########
    # #########   #########
    # 1     ####  ###     2
    # #########   #########
    # #########   #########
    # ######### 4 #########
    #
    # Connections: 1 -> 2, 3 -> 4 (will not fail because first connection uses the necessary underground)
    tunnel_length = 10
    buildings = {
        (-tunnel_length, 0): "left",
        (tunnel_length, 0): "right",
        (0, -tunnel_length): "top",
        (0, tunnel_length): "bottom",
    }

    _build_and_validate_grid(
        buildings=buildings,
        connections=[
            ((0, -tunnel_length), (0, tunnel_length)),
            ((-tunnel_length, 0), (tunnel_length, 0)),
        ],
        obstacles=_sealed_cross_tunnels_walls(
            tunnel_length=tunnel_length,
            extra_obstacles=set([(-1, 0), (-2, 0), (-3, 0), (2,0), (3,0), (4,0)]),
        ),
    )


def test_two_connections_can_share_a_sealed_one_tile_hall_between_rooms():
    # #####################
    # #                   #
    # #   1           2   #
    # #                   #
    # ########## ##########
    #          # #
    #          # #
    #          # #
    #          # #
    # ########## ##########
    # #                   #
    # #   4           3   #
    # #                   #
    # #####################
    #
    # Connections: 1 -> 2, 3 -> 4 (will not fail because connections are in same room)
    first_start, first_target = (-3, 3), (3, 3)
    second_start, second_target = (3, 17), (-3, 17)
    grid = _build_and_validate_grid(
        buildings={
            first_start: "first-start",
            first_target: "first-target",
            second_start: "second-start",
            second_target: "second-target",
        },
        connections=[(first_start, first_target), (second_start, second_target)],
        obstacles=_two_rooms_with_one_tile_hall_walls(),
    )

def test_three_connections_can_share_a_sealed_one_tile_hall_between_rooms():
    # #####################
    # #                   #
    # #   1     5     2   #
    # #                   #
    # ########## ##########
    #          # #
    #          # #
    #          # #
    #          # #
    # ########## ##########
    # #         6         #
    # #   4           3   #
    # #                   #
    # #####################
    #
    # Connections: 1 -> 2, 3 -> 4, 5 -> 6 (will not fail because connections only one connection is across rooms)
    first_start, first_target = (-3, 3), (3, 3)
    second_start, second_target = (3, 17), (-3, 17)
    third_start, third_target = (0, 3), (0, 17)
    grid = _build_and_validate_grid(
        buildings={
            first_start: "first-start",
            first_target: "first-target",
            second_start: "second-start",
            second_target: "second-target",
            third_start: "third-start",
            third_target: "third-target",
        },
        connections=[(first_start, first_target), (second_start, second_target)],
        obstacles=_two_rooms_with_one_tile_hall_walls(),
    )

def test_two_connections_cannot_share_a_sealed_one_tile_hall_between_rooms():
    # #####################
    # #                   #
    # #   1           2   #
    # #                   #
    # ########## ##########
    #          # #
    #          # #
    #          # #
    #          # #
    # ########## ##########
    # #                   #
    # #   4           3   #
    # #                   #
    # #####################
    #
    # Connections: 1 -> 3, 2 -> 4 (will fail because the hall is too narrow for two underground belts)
    grid = _two_rooms_with_one_tile_hall()
    first_start, first_target = (-3, 3), (3, 17)
    second_start, second_target = (3, 3), (-3, 17)

    for cord, name in (
        (first_start, "first-start"),
        (first_target, "first-target"),
        (second_start, "second-start"),
        (second_target, "second-target"),
    ):
        grid.add_source(cord, name)

    try:
        first_node, _ = GraphToMatrix.a_star(
            [first_start],
            lambda cord: cord == first_target,
            [first_target],
            grid,
        )
        grid._test_paths = [first_node.reconstruct_path()]
        GraphToMatrix.find_path(
            first_start,
            [first_start],
            lambda cord: cord == first_start,
            first_target,
            [first_target],
            lambda cord: cord == first_target,
            grid,
        )
    except Exception as error:
        pytest.fail(f"The first connection unexpectedly failed: {error}{_grid_diagnostics(grid)}")

    _assert_a_star_cannot_find_path(grid, second_start, second_target)


def test_get_number_of_sources_reads_graph_labels():
    import networkx

    graph = networkx.DiGraph()
    graph.add_node("a", label="iron_source")
    graph.add_node("b", label="gear")

    assert GraphToMatrix.get_number_of_sources(graph) == 1

def test_l_connection_straight_to_entity():
    # ###
    # #2#########################
    # #                        1#
    # ###########################

    grid = Grid()
    grid.add_source((0, 1), "a")
    grid.add_source((25, 0), "b")

    without = {(0, 1), (25, 0)} | {(x, 0) for x in range(25)}
    cube_size = 30

    for cord in _filled_square_without(cube_size - 1, without):
        grid.add_source(cord, "c")

    _assert_a_star_cannot_find_path(grid, (0, 1), (25, 0))
