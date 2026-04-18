import numpy as np
from networkx.classes import DiGraph

from src.factory_creator.dependency_graph import DependencyTreeNode


class GraphToMatrix:
    @staticmethod
    def convert_via_heuristics(graph: DiGraph, root: DependencyTreeNode) -> np.ndarray:
        print(root.get_approx_width_of_tree(1))

# https://wiki.factorio.com/Blueprint_string_format
# https://github.com/redruin1/factorio-blueprint-schemas