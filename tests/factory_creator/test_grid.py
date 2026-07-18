import pytest

from factory_creator.grid import Grid
from factory_creator.grid.grid_entry import GridEntryTypes
from factory_creator.util.factorio_const import FactorioConst


def test_add_factory_marks_main_tile_and_surroundings():
    grid = Grid()

    grid.add_factory((0, 0), "engine-unit", [(0, 1), (1, 0)])

    assert (0, 0) in grid.data
    assert grid[(0, 0)].entry_type == GridEntryTypes.Factory
    assert (0, 1) in grid.occupied
    assert (1, 0) in grid.occupied
    assert len(grid) == 3
    assert grid.get_number_of_factories() == 1
    assert list(grid.get_factories()) == [((0, 0), grid[(0, 0)])]


def test_add_source_and_collision_detection():
    grid = Grid()

    grid.add_source((2, 3), "iron_source")

    assert grid[(2, 3)].is_source()
    with pytest.raises(Exception, match="cannot be placed"):
        grid.add_source((2, 3), "other")


def test_add_transportation_uses_movable_ids_and_transform_to_inserter():
    grid = Grid()
    grid.add_source((0, 0), "source")
    grid.add_source((0, 2), "target")

    grid.add_transportation((0, 1), FactorioConst.TRANSPORT_BELT, 0, (0, 0), (0, 2))
    belt_id = grid[(0, 1)].get_id_text()

    assert belt_id == "1-2"
    assert grid.exists_path([(0, 0)], [(0, 2)], belt_id)

    grid.transform_into_inserter((0, 1), (0, 0), (0, 2))
    assert grid[(0, 1)].name == FactorioConst.INSERTER
    assert grid[(0, 1)].orientation == 8


def test_underground_belt_endpoint_cannot_be_transformed_to_inserter():
    grid = Grid()
    grid.add_source((0, 0), "source")
    grid.add_source((0, 2), "target")
    grid.add_transportation(
        (0, 1),
        FactorioConst.FAST_UNDERGROUND_BELT,
        0,
        (0, 0),
        (0, 2),
        underground_belt_type=FactorioConst.UNDERGROUND_BELT_OUTPUT,
    )

    with pytest.raises(ValueError, match="cannot be transformed into an inserter"):
        grid.transform_into_inserter((0, 1), (0, 0), (0, 2))

    assert grid[(0, 1)].name == FactorioConst.FAST_UNDERGROUND_BELT
    assert grid[(0, 1)].underground_belt_type == FactorioConst.UNDERGROUND_BELT_OUTPUT


@pytest.mark.parametrize(
    "inserter_cords,target",
    [
        ([(0, 1), (0, 2)], (0, 3)),
        ([(0, 1), (1, 1)], (2, 1)),
        ([(0, 1), (1, 1)], (1, 0))
    ],
    ids=["straight-chain", "corner-chain", "tower-chain"],
)
def test_exists_path_rejects_adjacent_inserters(inserter_cords, target):
    grid = Grid()
    source = (0, 0)
    grid.add_source(source, "source")
    grid.add_source(target, "target")

    for cord in inserter_cords:
        grid.add_transportation(
            cord, FactorioConst.TRANSPORT_BELT, 0, source, target
        )
        grid.transform_into_inserter(cord, source, target)

    belt_id = grid[inserter_cords[0]].get_id_text()

    assert not grid.exists_path([source], [target], belt_id)


def test_exists_path_rejects_adjacent_mixed_inserter_types():
    grid = Grid()
    source = (0, 0)
    target = (0, 3)
    grid.add_source(source, "source")
    grid.add_source(target, "target")
    grid.add_transportation(
        (0, 1), FactorioConst.INSERTER, 0, source, target
    )
    grid.add_transportation(
        (0, 2), FactorioConst.LONG_HANDED_INSERTER, 0, source, target
    )

    belt_id = grid[(0, 1)].get_id_text()

    assert not grid.exists_path([source], [target], belt_id)


def test_erase_factory_removes_surroundings_and_connected_belts():
    grid = Grid()
    grid.add_factory((0, 0), "engine-unit", [(1, 0)])
    grid.add_source((0, 3), "iron_source")
    grid.add_transportation((0, 1), FactorioConst.TRANSPORT_BELT, 0, (0, 3), (0, 0))

    neighbors = grid.erase_factory((0, 0))

    assert neighbors == [((0, 3), False)]
    assert (0, 0) not in grid.data
    assert (1, 0) not in grid.occupied
    assert (0, 1) not in grid.data
    assert (0, 0) not in grid
    assert (1, 0) not in grid
    assert (0, 1) not in grid


def test_grid_measurements_and_orientation_helpers():
    grid = Grid()
    grid.add_source((0, 0), "a")
    grid.add_source((2, 3), "b")

    assert grid.get_with() == 3
    assert grid.get_height() == 4
    assert grid.get_area() == 12
    assert grid.get_used_block() == 2
    assert grid._get_center_cord() == (1, 1.5)
    assert grid.get_distances_from_center() == 5
    assert Grid.orientation_to_vector(4) == (-1, 0)
    assert Grid.is_opposite_orientation_enum(0, 8)
    assert not Grid.is_opposite_orientation_enum(0, 4)


def test_underground_belt_counts_as_multiple_used_blocks():
    grid = Grid()
    grid.add_source((0, 0), "a")
    grid.add_source((0, 7), "b")
    grid.add_transportation(
        (0, 1),
        FactorioConst.FAST_UNDERGROUND_BELT,
        0,
        (0, 0),
        (0, 7),
    )

    assert grid.get_used_block() == 8
