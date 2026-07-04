import json

from .factory import Factory, Ingredient, Item
from .dependency_graph import DependencyTreeNode

class FactoryLoader:
    """
    Wrapper for the methods that loads factory and recipe definitions
    from the json input files.
    """

    ENABLE_PLATE_TERMINATION = True
    DEFAULT_ENERGY_REQUIREMENT = 0.5
    DEFAULT_AMOUNT_FOR_ITEM = 1

    @staticmethod
    def load(factory_definition_file_path: str) -> list[Factory]:
        """
        Returns list of factories loaded from the json input file.

        :param factory_definition_file_path: Path to factory definition json file.
        :return: List of factories.
        """

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

                    factory = Factory(name, energy_required, amount, ingredients, 3, 3, is_terminal) #TODO: loading real sizes
                    factories.append(factory)

        return factories

    @staticmethod
    def is_valid_recipe(factory_definition_file_path: str, recipe: str) -> bool:
        return recipe in FactoryLoader.load_recipe_names(factory_definition_file_path)

    @staticmethod
    def load_recipe_names(factory_definition_file_path: str) -> list[str]:
        """
        Returns list of recipe names loaded from the json input file.

        :param factory_definition_file_path: Path to the input json file.
        :return: List of recipe names loaded from the json file.
        """

        recipe_names = []

        with open(factory_definition_file_path, "r") as file:
            data = json.load(file)

            for entry in data:
                recipe_names.append(entry["name"])

        recipe_names.sort()

        return recipe_names

    @staticmethod
    def get_factory(factories: list[Factory], factory_name: str) -> Item:
        """
        Returns factory with given factory name.

        :param factories: List of available factories.
        :param factory_name: Name of the required factory.
        :return: Factory with the required name.
        """

        for factory in factories:
            if factory.name == factory_name:
                return factory

        return Item(factory_name)

    @staticmethod
    def get_dependency_tree(factories: list[Factory], recipe_name: str, layer: int = 0) -> DependencyTreeNode | None:
        """
        Returns dependency tree for given factories and recipe name.

        :param factories: List of available factories.
        :param recipe_name: Name of the required recipe.
        :param layer: Layer of the root node in the recipe subtree.
        :return: Dependency tree for given factories and recipe name.
        """

        factory = FactoryLoader.get_factory(factories, recipe_name)

        if factory is None:
            return None
            #raise RuntimeError(f"Not valid recipe name {recipe_name}") #TODO: custom InputError

        children = []

        for ingredient in factory.ingredients:
            children.append(FactoryLoader.get_dependency_tree(factories, ingredient.name, layer + 1))

        return DependencyTreeNode(factory, children, layer)