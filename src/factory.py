import json

class Item:
    def __init__(self, name: str, ingredients: list[Ingredient] = []):
        self.name = name
        self.ingredients = ingredients

    def __str__(self):
        return f"name: {self.name}"

class Factory(Item):
    def __init__(self, name: str, energy_required: int, ingredients: list[Ingredient], x_size: int, y_size: int) -> None:
        super().__init__(name, ingredients)
        self.energy_required = energy_required
        self.x_size = x_size
        self.y_size = y_size

    def __str__(self) -> str:
        return f"name: {self.name}, energy_required: {self.energy_required}, ingredients: {", ".join(str(ingredient) for ingredient in self.ingredients)}"

class Ingredient:
    def __init__(self, name: str, type: str, amount: int):
        self.name = name
        self.type = type
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.name}, {self.type}, {self.amount}"

class DependencyTreeNode:
    def __init__(self, factory: Item, children: list[DependencyTreeNode]):
        self.factory = factory
        self.children = children

    def dfs(self):
        print(self.factory)

        for child in self.children:
            child.dfs()

    def add_to_graph(self, dot, counter):
        node_id = f"n{counter}"
        dot.node(node_id, label=str(self))
        counter += 1

        for child in self.children:
            child_id, counter = child.add_to_graph(dot, counter)
            dot.edge(child_id, node_id)

        return node_id, counter

    def __str__(self) -> str:
        return self.factory.name

    """
    def __iter__(self):
        yield self

        for child in self.children:
            for descendant in child:
                yield descendant
    """

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

                    factory = Factory(entry["name"], int(energy_required), ingredients, 4, 4) #TODO: loading real sizes
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
