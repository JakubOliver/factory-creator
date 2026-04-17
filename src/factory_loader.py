import json

from .factory import Factory, Ingredient, Item
from .dependency_graph import DependencyTreeNode

class FactoryLoader:
    ENABLE_PLATE_TERMINATION = True
    DEFAULT_ENERGY_REQUIREMENT = 0.5
    DEFAULT_AMOUNT_FOR_ITEM = 1

    @staticmethod
    def load(factory_definition_file_path: str) -> list[Factory]:
        factories = []

        with open(factory_definition_file_path, "r") as file:
            data = json.load(file)

            for entry in data:
                if entry["type"] == "recipe":
                    name = entry["name"]

                    if not "energy_required" in entry:
                        energy_required = FactoryLoader.DEFAULT_ENERGY_REQUIREMENT
                    else:
                        energy_required = float(entry["energy_required"])

                    # TODO: better implementation. We want that the plates are terminal node (or we can add this as parameter)
                    is_terminal = False
                    if FactoryLoader.ENABLE_PLATE_TERMINATION and "plate" in name:
                        is_terminal = True

                    ingredients = []
                    for ingredient in entry["ingredients"]:
                        ingredients.append(Ingredient(ingredient["name"], ingredient["type"], int(ingredient["amount"])))

                    # TODO: maybe change the input data so the results are not an array but only one JSON object
                    if not "results" in entry or not "amount" in entry["results"][0]:
                        amount = FactoryLoader.DEFAULT_AMOUNT_FOR_ITEM
                    else:
                        amount = int(entry["results"][0]["amount"])

                    factory = Factory(name, energy_required, amount, ingredients, 4, 4, is_terminal) #TODO: loading real sizes
                    factories.append(factory)

        return factories

    @staticmethod
    def load_recipe_names(factory_definition_file_path: str) -> list[str]:
        recipe_names = []

        with open(factory_definition_file_path, "r") as file:
            data = json.load(file)

            for entry in data:
                recipe_names.append(entry["name"])

        recipe_names.sort()

        return recipe_names

    @staticmethod
    def get_factory(factories: list[Factory], factory_name: str) -> Item:
        for factory in factories:
            if factory.name == factory_name:
                return factory

        return Item(factory_name)

    @staticmethod
    def get_dependency_tree(factories: list[Factory], recipe_name: str) -> DependencyTreeNode | None:
        factory = FactoryLoader.get_factory(factories, recipe_name)

        if factory is None:
            return None
            #raise RuntimeError(f"Not valid recipe name {recipe_name}") #TODO: custom InputError

        children = []

        for ingredient in factory.ingredients:
            children.append(FactoryLoader.get_dependency_tree(factories, ingredient.name))

        return DependencyTreeNode(factory, children)