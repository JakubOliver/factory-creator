import json

from factory_creator.factory import Factory, Ingredient, Item
from factory_creator.loading import FactoryLoader


def write_recipes(tmp_path, recipes):
    recipe_file = tmp_path / "recipes.json"
    recipe_file.write_text(json.dumps(recipes), encoding="utf-8")
    return recipe_file


def test_load_reads_recipes_and_applies_defaults(tmp_path):
    recipe_file = write_recipes(
        tmp_path,
        [
            {
                "type": "recipe",
                "name": "iron-plate",
                "ingredients": [{"name": "iron-ore", "type": "item", "amount": 1}],
            }
        ],
    )

    factories = FactoryLoader.load(str(recipe_file))

    assert len(factories) == 1
    assert factories[0].name == "iron-plate"
    assert factories[0].energy_required == FactoryLoader.DEFAULT_ENERGY_REQUIREMENT
    assert factories[0].amount == FactoryLoader.DEFAULT_AMOUNT_FOR_ITEM
    assert factories[0].is_terminal
    assert factories[0].ingredients[0].name == "iron-ore"


def test_load_recipe_names_sorts_all_names(tmp_path):
    recipe_file = write_recipes(
        tmp_path,
        [
            {
            "type":"recipe",
            "ingredients":[{
                "amount":5,
                "type":"item",
                "name":"advanced-circuit"
                },{
                "amount":5,
                "type":"item",
                "name":"electronic-circuit"
                }],
            "results":[{
                "amount":1,
                "type":"item",
                "name":"speed-module"
                }],
            "name":"speed-module",
            "enabled":False,
            "energy_required":15
            },{
            "type":"recipe",
            "ingredients":[{
                "amount":4,
                "type":"item",
                "name":"speed-module"
                },{
                "amount":5,
                "type":"item",
                "name":"advanced-circuit"
                },{
                "amount":5,
                "type":"item",
                "name":"processing-unit"
                }],
            "results":[{
                "amount":1,
                "type":"item",
                "name":"speed-module-2"
                }],
            "name":"speed-module-2",
            "enabled":False,
            "energy_required":30
            },{
            "type":"recipe",
            "ingredients":[{
                "amount":4,
                "type":"item",
                "name":"speed-module-2"
                },{
                "amount":5,
                "type":"item",
                "name":"advanced-circuit"
                },{
                "amount":5,
                "type":"item",
                "name":"processing-unit"
                }],
            "results":[{
                "amount":1,
                "type":"item",
                "name":"speed-module-3"
                }],
            "name":"speed-module-3",
            "enabled":False,
            "energy_required":60
            },
        ],
    )

    assert FactoryLoader.load_recipe_names(str(recipe_file)) == ["speed-module", "speed-module-2", "speed-module-3"]
    assert FactoryLoader.is_valid_recipe(str(recipe_file), "speed-module")
    assert not FactoryLoader.is_valid_recipe(str(recipe_file), "missing")


def test_get_factory_returns_existing_factory_or_terminal_item():
    factory = Factory("engine-unit", 0.5, 1, [], 3, 3)

    assert FactoryLoader.get_factory([factory], "engine-unit") is factory

    fallback = FactoryLoader.get_factory([factory], "iron-ore")
    assert isinstance(fallback, Item)
    assert fallback.name == "iron-ore"
    assert fallback.is_terminal


def test_get_dependency_tree_builds_children_recursively():
    factories = [
        Factory("engine-unit", 0.5, 1, [Ingredient("iron-plate", "item", 2)], 3, 3),
        Factory("iron-plate", 3.2, 1, [Ingredient("iron-ore", "item", 1)], 3, 3, True),
    ]

    tree = FactoryLoader.get_dependency_tree(factories, "engine-unit")  
    assert tree.factory.name == "engine-unit"
    assert tree.get_layer() == 0
    assert tree.children[0].factory.name == "iron-plate"
    assert tree.children[0].get_layer() == 1
