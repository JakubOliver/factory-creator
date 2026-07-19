import math

import networkx
import pytest

from factory_creator.factory import DependencyTreeNode, Factory
from factory_creator.evolution import Evolution
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
from factory_creator.evolution.mutations import MoveBuildingMutation, MoveSubgraphMutation
from factory_creator.graph_processing import GraphToMatrix
from factory_creator.grid import Grid
from factory_creator.grid.grid_entry import GridEntryTransportationId


def create_fitness_aspects():
    return [
        AreaAspect(),
        UsedBlockAspect(),
        PointingToCenterAspect(),
        DistanceFromCenterAspect(),
        InserterCostAspect(),
        ConnectionValidityAspect(),
    ]


def _factory_node(name, layer):
    factory = Factory(
        name,
        energy_required=0.5,
        amount=1,
        ingredients=[],
        x_size=3,
        y_size=3,
    )
    return DependencyTreeNode(factory, [], layer)


def _make_graph(edges, factory_nodes):
    graph = networkx.DiGraph()

    for node_id, dependency_node in factory_nodes.items():
        graph.add_node(node_id, label=str(dependency_node), ref=dependency_node)

    for from_node, to_node in edges:
        if from_node not in graph:
            graph.add_node(from_node, label=from_node)
        graph.add_edge(from_node, to_node)

    return graph


def _node_cords(graph, node):
    cord = graph.nodes[node]["cord"]
    if "ref" not in graph.nodes[node]:
        return [cord]
    return list(graph.nodes[node]["ref"].factory.get_cords(cord))


def _assert_graph_connections_exist(graph, grid):
    for from_node, to_node in graph.edges:
        from_cords = _node_cords(graph, from_node)
        to_cords = _node_cords(graph, to_node)
        belt_id = GridEntryTransportationId.create_belt_id(
            grid[graph.nodes[from_node]["cord"]].get_id_text(),
            grid[graph.nodes[to_node]["cord"]].get_id_text(),
        )

        assert grid.exists_path(from_cords, to_cords, belt_id), (
            f"Missing grid connection for graph edge {from_node} -> {to_node}"
        )


@pytest.mark.parametrize(
    ("edges", "factory_names"),
    [
        pytest.param(
            [("iron-source", "n0")],
            {"n0": "iron-gear-wheel"},
            id="single-source",
        ),
        pytest.param(
            [
                ("iron-source", "n1"),
                ("copper-source", "n1"),
                ("n1", "n0"),
            ],
            {"n0": "science-pack", "n1": "electronic-circuit"},
            id="branching-recipe",
        ),
        pytest.param(
            [
                ("direct-source", "n0"),
                ("deep-source", "n1"),
                ("n1", "n0"),
            ],
            {"n0": "engine-unit", "n1": "iron-gear-wheel"},
            id="uneven-depth",
        ),
    ],
)
def test_networkx_graph_is_converted_to_connected_grid(edges, factory_names):
    factory_nodes = {
        node_id: _factory_node(name, layer=0)
        for node_id, name in factory_names.items()
    }
    graph = _make_graph(edges, factory_nodes)

    grid = GraphToMatrix.convert_via_heuristics(
        graph,
        report_method=lambda _: None,
    )

    assert isinstance(grid, Grid)
    assert grid.get_number_of_factories() == len(graph.nodes)
    assert all("cord" in graph.nodes[node] for node in graph.nodes)
    _assert_graph_connections_exist(graph, grid)


@pytest.mark.parametrize(
    ("edges", "factory_names"),
    [
        pytest.param(
            [("iron-source", "n0")],
            {"n0": "iron-gear-wheel"},
            id="single-source",
        ),
        pytest.param(
            [("iron-source", "n1"), ("n1", "n0")],
            {"n0": "engine-unit", "n1": "iron-gear-wheel"},
            id="production-chain",
        ),
    ],
)
def test_grid_created_from_graph_can_run_one_evolution_step(edges, factory_names):
    factory_nodes = {
        node_id: _factory_node(name, layer=0)
        for node_id, name in factory_names.items()
    }
    graph = _make_graph(edges, factory_nodes)
    grid = GraphToMatrix.convert_via_heuristics(
        graph,
        report_method=lambda _: None,
    )

    evolved_grid = Evolution.evolve(
        grid,
        [MoveBuildingMutation(), MoveSubgraphMutation()],
        create_fitness_aspects(),
        iteration=1,
        stagnation_break=1,
        report_method=lambda _: None,
    )

    assert isinstance(evolved_grid, Grid)
    assert evolved_grid.get_number_of_factories() == len(graph.nodes)
    assert math.isfinite(
        Fitness(create_fitness_aspects()).evaluate(
            FitnessContext(evolved_grid, test_connection=False)
        )
    )
