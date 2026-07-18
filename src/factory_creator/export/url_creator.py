from ..grid import Grid
from .json_matrix_representation import BluePrintRepresentation, MatrixJsonConvertor


class URLCreator:
    """Creates links for opening encoded factory blueprints."""

    BASE_URL = "https://fbe.teoxoy.com/"
    SOURCE_EXTENSION = "?source="

    @staticmethod
    def create_factory_url_link(
        seed: str,
        base_url: str = BASE_URL,
    ) -> str:
        """Build a web editor URL for an encoded factory blueprint seed."""
        return f"{base_url.strip()}{URLCreator.SOURCE_EXTENSION}{seed}"

    @staticmethod
    def create_factory_url_from_grid(
        grid: Grid,
        base_url: str = BASE_URL,
    ) -> str:
        """Convert a factory grid into a blueprint and build its editor URL."""
        blueprint_json = MatrixJsonConvertor.encode(grid)
        seed = BluePrintRepresentation.encode(blueprint_json)
        return URLCreator.create_factory_url_link(seed, base_url)
