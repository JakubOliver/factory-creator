import json

class Item:
    def __init__(self, name: str, amount: int = 1, ingredients: list[Ingredient] = []):
        self.name = name
        self.amount = amount
        self.ingredients = ingredients

    def required_amount(self, ingredient_name: str) -> int:
        for ingredient in self.ingredients:
            if ingredient.name == ingredient_name:
                return ingredient.amount

        # TODO: throw ingredient now found
        return 1

    def __str__(self):
        return f"name: {self.name}"

class Factory(Item):
    def __init__(self, name: str, energy_required: int, amount: int, ingredients: list[Ingredient], x_size: int, y_size: int) -> None:
        super().__init__(name, amount, ingredients)

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

    def dependency_graph(self, dot, counter, show_amounts = False, show_simplified = True):
        node_id = f"n{counter}"
        dot.node(node_id, label=str(self))
        counter += 1

        for child in self.children:
            # TODO: change logic from unsimplified to simplified
            amount_needed = self.factory.required_amount(child.factory.name)
            amount_processes = 0

            while amount_processes < amount_needed:
                child_id, counter = child.dependency_graph(dot, counter, show_amounts, show_simplified)

                if show_amounts:
                    dot.edge(
                        child_id,
                        node_id,
                        label=str(amount_needed if show_simplified else child.factory.amount)
                    )
                else:
                    dot.edge(child_id, node_id)

                if show_simplified:
                    break
                else:
                    amount_processes += child.factory.amount

        return node_id, counter

    def node_parent(self, parent_idx = None, counter = None):
        node_idx = parent_idx + 1 if parent_idx is not None else 0
        counter = counter + 1 if counter is not None else node_idx

        yield node_idx, str(self), parent_idx, counter

        for child in self.children:
            for child_idx, child_id, ancestor_idx, new_counter in child.node_parent(node_idx, counter):
                counter = new_counter

                yield child_idx, child_id, ancestor_idx, counter

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
