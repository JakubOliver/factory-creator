from factory_creator.export.json_matrix_representation import BluePrintRepresentation, MatrixJsonConvertor
from factory_creator.grid import Grid
from factory_creator.util.factorio_const import FactorioConst


def test_blueprint_encoding_round_trips_json():
    payload = {"blueprint": {"entities": [{"name": "transport-belt"}]}}

    encoded = BluePrintRepresentation.encode(payload)

    assert encoded.startswith("0")
    assert BluePrintRepresentation.decode(encoded) == payload


def test_entity_helpers_create_expected_structures():
    entity = MatrixJsonConvertor._get_entity("transport-belt", (1.5, 2.5), 4, 7)
    chest = MatrixJsonConvertor._get_chest_entity("wooden-chest", (0.5, 0.5), 0, 1, "iron-plate")
    assembler = MatrixJsonConvertor._get_assembling_machine("assembling-machine-2", (3.5, 4.5), 8, 2, "engine-unit")

    assert entity["position"] == {"x": 1.5, "y": 2.5}
    assert entity["direction"] == 4
    assert entity["entity_number"] == 7
    assert chest["items"][0]["id"]["name"] == "iron-plate"
    assert assembler["recipe"] == "engine-unit"


def test_load_entities_exports_belts_sources_and_factories():
    grid = Grid()
    grid.add_source((0, 0), "iron-plate_source")
    grid.add_source((0, 2), "engine-unit")
    grid.add_transportation(
        (0, 1),
        FactorioConst.FAST_UNDERGROUND_BELT,
        4,
        (0, 0),
        (0, 2),
        underground_belt_type=FactorioConst.UNDERGROUND_BELT_INPUT,
    )

    entities = MatrixJsonConvertor._load_entities(grid, offset=(10, 20), entity_number=5)["entities"]

    assert [entity["entity_number"] for entity in entities] == [5, 6, 7]
    assert entities[0]["name"] == FactorioConst.WOODEN_CHEST
    assert entities[0]["items"][0]["id"]["name"] == "iron-plate"
    assert entities[1]["name"] == FactorioConst.ASSEMBLING_MACHINE_2
    assert entities[1]["recipe"] == "engine-unit"
    assert entities[2]["name"] == FactorioConst.FAST_UNDERGROUND_BELT
    assert entities[2]["type"] == FactorioConst.UNDERGROUND_BELT_INPUT