from factory_creator.grid.grid_entry import (
    GridEntry,
    GridEntryMovableId,
    GridEntryTransportationId,
    GridEntryTypes,
)
from factory_creator.util.factorio_const import FactorioConst


def test_movable_id_is_textual_and_not_connected():
    movable_id = GridEntryMovableId(42)

    assert movable_id.get_id() == "42"
    assert not movable_id.is_connected_to(GridEntryMovableId(7))


def test_transportation_id_connects_two_movable_entries():
    source_id = GridEntryMovableId(1)
    destination_id = GridEntryMovableId(2)
    belt_id = GridEntryTransportationId(source_id, destination_id)

    assert belt_id.get_id() == "1-2"
    assert belt_id.is_connected_to(source_id)
    assert belt_id.is_connected_to(destination_id)
    assert not belt_id.is_connected_to(GridEntryMovableId(3))


def test_grid_entry_type_helpers_and_detailed_names():
    factory = GridEntry(GridEntryMovableId(1), "engine-unit", entry_type=GridEntryTypes.Factory)
    source = GridEntry(GridEntryMovableId(2), "iron_source", entry_type=GridEntryTypes.Source)
    belt = GridEntry(
        GridEntryTransportationId(factory.get_id(), source.get_id()),
        "transport-belt",
    )

    assert factory.is_factory()
    assert factory.is_movable()
    assert factory.get_detailed_name() == "engine-unit-factory"
    assert source.is_source()
    assert source.is_movable()
    assert source.get_detailed_name() == "iron_source-source"
    assert belt.is_transportation()
    assert not belt.is_movable()
    assert belt.get_detailed_name() == "transport-belt"


def test_is_inserter_recognizes_normal_and_long_handed_types():
    entry_id = GridEntryTransportationId(
        GridEntryMovableId(1), GridEntryMovableId(2)
    )

    normal = GridEntry(entry_id, FactorioConst.INSERTER)
    long_handed = GridEntry(entry_id, FactorioConst.LONG_HANDED_INSERTER)
    belt = GridEntry(entry_id, FactorioConst.TRANSPORT_BELT)

    assert normal.is_inserter()
    assert long_handed.is_inserter()
    assert not belt.is_inserter()


def test_grid_entry_tracks_surroundings_and_source_item_names():
    entry = GridEntry(GridEntryMovableId(1), "assembler", entry_type=GridEntryTypes.Factory)

    entry.add_surrounding((1, 2))
    entry.add_surrounding((1, 2))

    assert entry.surroundings == {(1, 2)}
    assert GridEntry.extract_item_name_from_source("iron-plate_source_0") == "iron-plate"
