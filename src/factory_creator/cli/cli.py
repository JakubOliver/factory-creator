from ..loading import FactoryLoader
from ..factory_processor import FactoryProcessor
from ..export.url_creator import URLCreator
from ..evolution.plugin_configuration import PluginConfiguration


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
            create_presentation=False,
            mutations=PluginConfiguration.create_mutations(
                PluginConfiguration.discover_mutations()
            ),
            fitness_aspects=PluginConfiguration.create_fitness_aspects(
                PluginConfiguration.discover_fitness_aspects()
            ),
        )

        print(URLCreator.create_factory_url_link(result.factory_seed))
        print(URLCreator.create_factory_url_link(result.evolution_seed))

        if args.show_graph:
            try:
                from ..export.factory_graph_renderer import FactoryGraphRenderer
            except ImportError as exc:
                raise RuntimeError(
                    "Graphviz rendering is not available. Install the optional "
                    "graph rendering dependencies and the Graphviz system package."
                ) from exc

            FactoryGraphRenderer.show_graph(result.dependency_graph)
