from __future__ import annotations
import itertools
from typing import override
from collections.abc import Iterator, Callable

from .assembler import Assembler

class Item:
    """
    Represents an item which occurs in the recipe instructions
    in the factories.
    """

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
        """
        Returns the amount of the ingredient with the provided name.

        :param ingredient_name: Name of the ingredient.
        :return: The amount of the ingredient with the provided name.
        """

        for ingredient in self.ingredients:
            if ingredient.name == ingredient_name:
                return ingredient.amount

        raise ValueError(f"{ingredient_name} not found in ingredients")

    def get_cords(self, cord):
        """
        Returns interator across all 2D coordination that the item occupies
        in the grid representation based on the provided top left coordinate.

        :param cord: Coordination of the top left point of the item.
        :return: Iterator across all 2D coordination that the item occupies.
        """

        # This is only dummy function (it is needed to check if this makes sense)
        yield  cord

    @staticmethod
    def get_dummy_cords(cord):
        """
        Dummy iterator which provides only coordination provided in the argument.

        :param cord: Coordination for the iterator.
        :return: Dummy iterator which provided only coordination provided in the argument.
        """

        yield cord

    def get_cords_lambda(self, cord):
        """
        Provides lambda expression which when called provides information whether the provided
        points in the grid is inside the item.

        :param cord: Coordination of the top left point of the item.
        :return: Lambda expression which provides information whether the provided points
            is inside the item.
        """

        return lambda new_cord : any(new_cord == building_cord for building_cord in self.get_cords(cord))

    def get_cord_of_center(self, cord):
        """
        Returns coordination of the center of the item.

        :param cord: Coordination of the top left point of the item.
        :return: Coordination of the center of the item.
        """

        # This is only dummy function (it is needed to check if this makes sense)
        x, y = cord

        return x + 0.5, y + 0.5

    def crafting_time(self, assembler: Assembler) -> float:
        """
        Returns the crafting time of the item.

        :param assembler: Assembler in which the item will be crafted.
        :return: The crafting time of the item.
        """

        return Item.DEFAULT_VALUE_OF_COST_OF_TERMINAL_ITEMS

    def __str__(self):
        return f"name: {self.name}"

class Factory(Item):
    """
    Represents not trivial item which can be crafted in the factory/assembler.
    """

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

    @override
    def get_cords(self, cord):
        x, y = cord

        for dx, dy in itertools.product(range(0, self.x_size), range(0, self.y_size)):
            yield x + dx, y + dy

    @override
    def get_cord_of_center(self, cord):
        x, y = cord

        return x + self.x_size / 2, y + self.y_size / 2

    def __str__(self) -> str:
        return (f"name: {self.name}, "
                f"energy_required: {self.energy_required}, "
                f"ingredients: {", ".join(str(ingredient) for ingredient in self.ingredients)}")

class Ingredient:
    """
    Represents an ingredient of the recipe.
    """

    def __init__(self, name: str, type: str, amount: int):
        self.name = name
        self.type = type
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.name}, {self.type}, {self.amount}"
    
class FactoryUtil:
    @staticmethod
    def get_cords(cords: tuple) -> Iterator[tuple]:
        """
        Iterates over coordinates occupied by a temporary 3x3 factory footprint.

        :param cords: Top left coordinates of the temporary factory footprint.
        :return: Iterator over coordinates occupied by the temporary factory footprint.
        """

        x, y = cords

        for dx, dy in itertools.product(range(0, 3), range(0, 3)):
            yield x + dx, y + dy

    @staticmethod
    def get_cords_lambda(cord: tuple) -> Callable[[tuple], bool]:
        """
        Creates function checking whether coordinates are inside a temporary factory footprint.

        :param cord: Top left coordinates of the temporary factory footprint.
        :return: Function checking whether coordinates are inside the temporary factory footprint.
        """

        return lambda new_cord : any(new_cord == building_cord for building_cord in FactoryUtil.get_cords(cord))
