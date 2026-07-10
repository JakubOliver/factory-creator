import pytest

from factory_creator.assembler import Assembler, AssemblingMachine3
from factory_creator.factory import Factory, FactoryUtil, Ingredient, Item


def test_item_required_amount_returns_matching_ingredient():
    item = Item("gear", ingredients=[Ingredient("iron-plate", "item", 2)])

    assert item.required_amount("iron-plate") == 2


def test_item_required_amount_raises_for_missing_ingredient():
    item = Item("gear")

    with pytest.raises(ValueError, match="copper not found"):
        item.required_amount("copper")


def test_item_default_geometry_and_crafting_time():
    item = Item("iron-ore")

    assert list(item.get_cords((3, 4))) == [(3, 4)]
    assert item.get_cords_lambda((3, 4))((3, 4))
    assert not item.get_cords_lambda((3, 4))((4, 4))
    assert item.get_cord_of_center((3, 4)) == (3.5, 4.5)
    assert item.crafting_time(Assembler(2.0)) == 0.0
    assert str(item) == "name: iron-ore"


def test_factory_uses_size_for_geometry_and_assembler_for_crafting_time():
    factory = Factory(
        "engine-unit",
        energy_required=0.5,
        amount=2,
        ingredients=[Ingredient("iron-plate", "item", 2)],
        x_size=2,
        y_size=3,
    )

    assert set(factory.get_cords((10, 20))) == {
        (10, 20),
        (10, 21),
        (10, 22),
        (11, 20),
        (11, 21),
        (11, 22),
    }
    assert factory.get_cord_of_center((10, 20)) == (11.0, 21.5)
    assert factory.crafting_time(Assembler(0.5)) == 0.5
    assert factory.crafting_time(AssemblingMachine3()) == pytest.approx(0.2)


def test_factory_util_temporary_three_by_three_footprint():
    cords = set(FactoryUtil.get_cords((5, 7)))

    assert len(cords) == 9
    assert (5, 7) in cords
    assert (7, 9) in cords
    assert FactoryUtil.get_cords_lambda((5, 7))((6, 8))
    assert not FactoryUtil.get_cords_lambda((5, 7))((8, 8))
