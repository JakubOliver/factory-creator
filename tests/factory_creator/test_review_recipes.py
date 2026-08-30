import json
from pathlib import Path

import pytest

from factory_creator.graph_processing import GraphToMatrix
from factory_creator.loading import FactoryLoader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RECIPE_PATH = PROJECT_ROOT / "data" / "recipe.json"
REVIEW_RECIPE_PATH = PROJECT_ROOT / "data" / "recipe_for_review.json"
REVIEW_RECIPE_NAMES = FactoryLoader.load_recipe_names(str(REVIEW_RECIPE_PATH))


@pytest.fixture(scope="module")
def reviewed_factories():
    return FactoryLoader.load(str(REVIEW_RECIPE_PATH))


def test_reviewed_recipes_are_unchanged_item_recipe_definitions():
    source_recipes = {
        recipe["name"]: recipe
        for recipe in json.loads(RECIPE_PATH.read_text(encoding="utf-8"))
    }
    reviewed_recipes = json.loads(REVIEW_RECIPE_PATH.read_text(encoding="utf-8"))

    for recipe in reviewed_recipes:
        assert recipe == source_recipes[recipe["name"]]
        assert all(ingredient["type"] == "item" for ingredient in recipe["ingredients"])
        assert all(result["type"] == "item" for result in recipe["results"])


@pytest.mark.parametrize("recipe_name", REVIEW_RECIPE_NAMES)
def test_reviewed_recipe_can_be_converted_to_grid(
    reviewed_factories,
    recipe_name,
):
    root = FactoryLoader.get_dependency_tree(reviewed_factories, recipe_name)
    graph = root.get_dependency_graph(
        show_amounts=False,
        show_simplified=False,
        output_efficiency=1.0,
    )

    grid = GraphToMatrix.convert_via_heuristics(
        graph,
        report_method=lambda _: None,
        error_report_method=lambda _: None,
    )

    assert any(entry.name == recipe_name for _, entry in grid.get_factories())
