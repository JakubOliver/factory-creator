from typing import override

from .assembler import Assembler

class Item:
    DEFAULT_VALUE_OF_COST_OF_TERMINAL_ITEMS = 0.0

    def __init__(
            self,
            name: str,
            amount: int = 1,
            ingredients=None,
            is_terminal: bool = True
    ) -> None:
        if ingredients is None:
            ingredients = list()

        self.name = name
        self.amount = amount
        self.ingredients = ingredients
        self.is_terminal = is_terminal

    def required_amount(self, ingredient_name: str) -> int:
        for ingredient in self.ingredients:
            if ingredient.name == ingredient_name:
                return ingredient.amount

        # TODO: throw ingredient now found
        return 1

    def crafting_time(self, assembler: Assembler) -> float:
        return Item.DEFAULT_VALUE_OF_COST_OF_TERMINAL_ITEMS

    def __str__(self):
        return f"name: {self.name}"

class Factory(Item):
    def __init__(
            self,
            name: str,
            energy_required: float,
            amount: int,
            ingredients: list[Ingredient],
            x_size: int,
            y_size: int,
            is_terminal: bool = False
    ) -> None:
        super().__init__(name, amount, ingredients, is_terminal)

        self.energy_required = energy_required
        self.x_size = x_size
        self.y_size = y_size

    @override
    def crafting_time(self, assembler: Assembler) -> float:
        return self.energy_required / assembler.multiplicator / self.amount

    def __str__(self) -> str:
        return (f"name: {self.name}, "
                f"energy_required: {self.energy_required}, "
                f"ingredients: {", ".join(str(ingredient) for ingredient in self.ingredients)}")

class Ingredient:
    def __init__(self, name: str, type: str, amount: int):
        self.name = name
        self.type = type
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.name}, {self.type}, {self.amount}"