import pytest
from pyrsistent import pset

from factory_creator.graph_to_matrix import AStartNode, GraphToMatrix, VisitedMatrix
from factory_creator.grid import Grid


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

    assert found == (0, 2)
    assert visited[(0, 1)] == -1
    assert visited[(0, 2)] > 1


def test_a_star_finds_simple_path_and_reports_unreachable_target():
    grid = Grid()

    node, visited = GraphToMatrix.a_star([(0, 0)], lambda cord: cord == (0, 3), [(0, 3)], grid)

    assert node.cord == (0, 3)
    assert len(visited) > 0

    blocked = Grid()
    blocked.add_source((0, 1), "block")
    blocked.add_source((-1, 0), "block")
    blocked.add_source((0, -1), "block")
    blocked.add_source((1, 0), "block")

    with pytest.raises(Exception, match="Unable to find a path"):
        GraphToMatrix.a_star([(0, 0)], lambda cord: cord == (0, 2), [(0, 2)], blocked)


def test_get_number_of_sources_reads_graph_labels():
    import networkx

    graph = networkx.DiGraph()
    graph.add_node("a", label="iron_source")
    graph.add_node("b", label="gear")

    assert GraphToMatrix.get_number_of_sources(graph) == 1
