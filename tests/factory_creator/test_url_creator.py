from factory_creator.export.json_matrix_representation import (
    BluePrintRepresentation,
    MatrixJsonConvertor,
)
from factory_creator.export.url_creator import URLCreator
from factory_creator.grid import Grid


def test_create_factory_url_link() -> None:
    assert URLCreator.create_factory_url_link("encoded-seed") == (
        "https://fbe.teoxoy.com/?source=encoded-seed"
    )


def test_create_factory_url_from_grid(monkeypatch) -> None:
    grid = Grid()
    blueprint_json = {"blueprint": {}}

    monkeypatch.setattr(MatrixJsonConvertor, "encode", lambda value: blueprint_json)
    monkeypatch.setattr(BluePrintRepresentation, "encode", lambda value: "encoded-seed")

    assert URLCreator.create_factory_url_from_grid(grid) == (
        "https://fbe.teoxoy.com/?source=encoded-seed"
    )
