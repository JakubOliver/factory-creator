from dataclasses import dataclass

from .evol import Evolution
from .factory_loader import FactoryLoader
from .graph_to_matrix import GraphToMatrix
from .json_matrix_representation import MatrixJsonConvertor, BluePrintRepresentation


@dataclass
class FactoryProcessingResult:
    factory_seed: str
    evolution_seed: str
    dependency_graph: object


class FactoryProcessor:
    @staticmethod
    def process_factory(
        path,
        recipe_type,
        show_amounts=True,
        simplified_structure=False,
        evolution_iteration=float("inf"),
        evolution_stagnation=10,
        create_presentation=False,
        report_method = print
    ) -> FactoryProcessingResult | None:
        factories = FactoryLoader.load(path)

        root = FactoryLoader.get_dependency_tree(factories, recipe_type)

        if root is not None:
            graph = root.get_dependency_graph(
                show_amounts=show_amounts,
                show_simplified=simplified_structure
            )

            matrix = GraphToMatrix.convert_via_heuristics(
                graph,
                root,
                report_method=report_method
            )
            json_obj = MatrixJsonConvertor.encode(matrix)
            factory_seed = BluePrintRepresentation.encode(json_obj)

            after_evolution = Evolution.evol(
                matrix,
                iteration=evolution_iteration,
                stagnation_break=evolution_stagnation,
                create_presentation=create_presentation,
                report_method=report_method
            )

            if create_presentation:
                return FactoryProcessingResult(
                    factory_seed,
                    BluePrintRepresentation.encode(MatrixJsonConvertor.process_presentation(after_evolution)),
                    graph
                )

            return FactoryProcessingResult(
                factory_seed,
                BluePrintRepresentation.encode(MatrixJsonConvertor.encode(after_evolution)),
                graph
            )
        else:
            return None
