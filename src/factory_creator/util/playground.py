"""Manually editable playground for debugging grid evolution."""


if __name__ == "__main__":
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(project_root))

    from src.factory_creator.evolution import Evolution
    from src.factory_creator.export.json_matrix_representation import (
        BluePrintRepresentation,
        MatrixJsonConvertor,
    )
    from src.factory_creator.grid import Grid
    from src.factory_creator.gui.main_window import MainWindow
    from src.factory_creator.util.factorio_const import FactorioConst

    def create_grid() -> Grid:
        """Create the grid used by this debugging run.

        Edit this function freely when experimenting with layouts.
        """
        grid = Grid()

        grid.add_source((0, 0), "engine-unit_source")
        grid.add_source((4, 0), "engine-unit_source")

        for x in range(1, 4):
            grid.add_transportation(
                (x, 0),
                FactorioConst.TRANSPORT_BELT,
                0,
                (0, 0),
                (4, 0),
            )

        return grid

    grid = create_grid()
    evolved_grid = Evolution.evol(grid)

    Path("output").mkdir(parents=True, exist_ok=True)
    blueprint_json = MatrixJsonConvertor.encode(evolved_grid)
    blueprint = BluePrintRepresentation.encode(blueprint_json)
    url = MainWindow.create_factory_url_link(blueprint)

    print(evolved_grid)
    print(url)
