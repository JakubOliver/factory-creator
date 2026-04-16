import json

from .factory import Factory, Ingredient, Item
from .dependency_graph import DependencyTreeNode

class FactoryLoader:
    @staticmethod
    def load(factory_definition_file_path: str) -> list[Factory]:
        factories = []

        with open(factory_definition_file_path, "r") as file:
            data = json.load(file)

            for entry in data:
                if entry["type"] == "recipe":
                    if not "energy_required" in entry:
                        energy_required = 0
                    else:
                        energy_required = entry["energy_required"]

                    ingredients = []
                    for ingredient in entry["ingredients"]:
                        ingredients.append(Ingredient(ingredient["name"], ingredient["type"], int(ingredient["amount"])))

                    # TODO: maybe change the input data so the results are not an array but only one JSON object
                    if not "results" in entry or not "amount" in entry["results"][0]:
                        amount = 1
                    else:
                        amount = int(entry["results"][0]["amount"])

                    factory = Factory(entry["name"], int(energy_required), amount, ingredients, 4, 4) #TODO: loading real sizes
                    factories.append(factory)

        return factories

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