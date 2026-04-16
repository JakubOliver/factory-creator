class Item:
    def __init__(self, name: str, amount: int = 1, ingredients: list[Ingredient] = list()):
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