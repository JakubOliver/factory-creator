from src.factory_creator.factory_loader import FactoryLoader
from src.factory_creator.factory_processor import FactoryProcessor
from src.factory_creator.gui.main_window import MainWindow


class CLI:
    @staticmethod
    def run(args) -> None:
        if not FactoryLoader.is_valid_recipe(args.input, args.building):
            raise ValueError(f"Invalid file {args.input} or recipe {args.building}")

        result = FactoryProcessor.process_factory(
            args.input,
            args.building,
            evolution_iteration=args.iteration,
            evolution_stagnation=args.stagnation,
            create_presentation=False
        )

        print(MainWindow.create_factory_url_link(result.factory_seed))
        print(MainWindow.create_factory_url_link(result.evolution_seed))

        if args.show_graph:
            try:
                from src.factory_creator.export.factory_graph_renderer import FactoryGraphRenderer
            except ImportError as exc:
                raise RuntimeError(
                    "Graphviz rendering is not available. Install the optional "
                    "graph rendering dependencies and the Graphviz system package."
                ) from exc

            FactoryGraphRenderer.show_graph(result.dependency_graph)
