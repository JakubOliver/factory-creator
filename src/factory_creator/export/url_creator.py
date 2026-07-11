from ..grid import Grid
from .json_matrix_representation import BluePrintRepresentation, MatrixJsonConvertor


class URLCreator:
    """Creates links for opening encoded factory blueprints."""

    BASE_URL = "https://fbe.teoxoy.com/?source="

    @staticmethod
    def create_factory_url_link(seed: str) -> str:
        """Build a web editor URL for an encoded factory blueprint seed."""
        return f"{URLCreator.BASE_URL}{seed}"

    @staticmethod
    def create_factory_url_from_grid(grid: Grid) -> str:
        """Convert a factory grid into a blueprint and build its editor URL."""
        blueprint_json = MatrixJsonConvertor.encode(grid)
        seed = BluePrintRepresentation.encode(blueprint_json)
        return URLCreator.create_factory_url_link(seed)
