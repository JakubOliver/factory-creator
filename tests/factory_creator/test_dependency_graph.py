import pytest

from factory_creator.assembler import Assembler
from factory_creator.dependency_graph import DependencyTreeNode, Stats
from factory_creator.factory import Factory, Ingredient, Item


def test_stats_starts_with_only_layer_set():
    stats = Stats(layer=3)

    assert stats.layer == 3
    assert stats.approx_width is None
    assert stats.approx_depth is None


def test_dependency_node_computes_crafting_ratios_and_tree_size():
    plate = DependencyTreeNode(Item("iron-plate", is_terminal=True), [], layer=1)
    gear_factory = Factory(
        "engine-unit",
        energy_required=0.5,
        amount=1,
        ingredients=[Ingredient("iron-plate", "item", 2)],
        x_size=3,
        y_size=3,
    )
    gear = DependencyTreeNode(gear_factory, [plate], layer=0, assembler=Assembler(1.0))

    assert gear.crafting_time() == 0.5
    assert gear.relative_crafting_time(0) == 0.5
    assert gear.number_of_ingredient_factories(1) == [0]
    assert gear.get_approx_width_of_tree() == 1
    assert gear.get_approx_depth_of_tree() == 2


def test_normalize_amount_and_identifiers():
    assert DependencyTreeNode.get_graph_identifier(4) == "n4"
    assert DependencyTreeNode.get_root_identifier() == "n0"
    assert DependencyTreeNode.normalize_amount(0) == 0
    assert DependencyTreeNode.normalize_amount(2.5) == pytest.approx(2.5 / 3)


def test_dependency_graph_contains_recipe_and_terminal_source():
    terminal = DependencyTreeNode(Item("iron-plate", is_terminal=True), [], layer=1)
    root_factory = Factory(
        "engine-unit",
        energy_required=0.5,
        amount=1,
        ingredients=[Ingredient("iron-plate", "item", 2)],
        x_size=3,
        y_size=3,
    )
    root = DependencyTreeNode(root_factory, [terminal], layer=0)

    graph = root.get_dependency_graph(show_amounts=True, show_simplified=True)

    assert DependencyTreeNode.get_root_identifier() in graph.nodes
    assert any(data["label"] == "iron-plate_source" for _, data in graph.nodes(data=True))
    assert any("label" in data for _, _, data in graph.edges(data=True))
