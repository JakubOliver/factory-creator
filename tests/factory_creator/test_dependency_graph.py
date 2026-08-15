import pytest

from factory_creator.factory import Assembler, DependencyTreeNode, Factory, Ingredient, Item, Stats


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


def test_output_efficiency_controls_full_dependency_graph_size():
    terminal = DependencyTreeNode(Item("ore", is_terminal=True), [], layer=2)
    intermediate_factory = Factory(
        "intermediate",
        energy_required=10,
        amount=1,
        ingredients=[Ingredient("ore", "item", 1)],
        x_size=3,
        y_size=3,
    )
    intermediate = DependencyTreeNode(
        intermediate_factory,
        [terminal],
        layer=1,
    )
    root_factory = Factory(
        "target",
        energy_required=0.5,
        amount=1,
        ingredients=[Ingredient("intermediate", "item", 10)],
        x_size=3,
        y_size=3,
    )
    root = DependencyTreeNode(root_factory, [intermediate], layer=0)

    minimal_graph = root.get_dependency_graph(
        show_amounts=False,
        show_simplified=False,
        output_efficiency=0,
    )
    half_output_graph = root.get_dependency_graph(
        show_amounts=False,
        show_simplified=False,
        output_efficiency=0.5,
    )
    full_output_graph = root.get_dependency_graph(
        show_amounts=False,
        show_simplified=False,
        output_efficiency=1,
    )

    assert len(minimal_graph) == 4
    assert len(half_output_graph) == 300
    assert len(full_output_graph) == 600


@pytest.mark.parametrize("output_efficiency", [-0.01, 1.01])
def test_output_efficiency_must_be_between_zero_and_one(output_efficiency):
    root = DependencyTreeNode(Item("ore", is_terminal=True), [], layer=0)

    with pytest.raises(ValueError, match="between 0 and 1"):
        root.get_dependency_graph(
            show_amounts=False,
            show_simplified=False,
            output_efficiency=output_efficiency,
        )
