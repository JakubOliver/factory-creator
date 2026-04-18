#from graphviz import Digraph
from networkx import DiGraph
from numpy.ma.core import shape

from .assembler import Assembler, AssemblingMachine3
from .factory import Item

import math

class DependencyTreeNode:
    def __init__(self, factory: Item, children: list[DependencyTreeNode], assembler: Assembler = AssemblingMachine3()):
        self.factory = factory
        self.children = children

        self.assembler = assembler

    def dfs(self):
        print(self.factory)

        for child in self.children:
            child.dfs()

    def get_dependency_graph(
        self,
        show_amounts: bool,
        show_simplified: bool,
    ) -> DiGraph:
        graph = DiGraph()

        self._dependency_graph(
            graph,
            0,
            1,
            show_amounts=show_amounts,
            show_simplified=show_simplified
        )

        return graph

    def _dependency_graph(
        self,
        dot,
        counter,
        output_needed,
        show_amounts = False,
        show_simplified = True
    ):
        node_id = f"n{counter}"
        dot.add_node(node_id, label=str(self), shape="ellipse")
        counter += 1

        if self.factory.is_terminal:
            return node_id, counter

        for child, amount_needed in zip(self.children, self.number_of_ingredient_factories(output_needed)):
            for _ in range(max(1, math.ceil(amount_needed))):
                child_id, counter = child._dependency_graph(
                    dot,
                    counter,
                    amount_needed,
                    show_amounts,
                    show_simplified
                )

                if show_amounts:
                    dot.add_edge(
                        child_id,
                        node_id,
                        label=f"{amount_needed:0.4f}"
                    )
                else:
                    dot.add_edge(child_id, node_id)

                if show_simplified or child.factory.is_terminal:
                    break

        return node_id, counter

    def crafting_time(self) -> float:
        return self.factory.crafting_time(self.assembler)

    def number_of_ingredient_factories(self, output_needed) -> list[float]:
        # TODO: In this stage all stages has to create at least one item per second (or other time period), but I should be improved without this, because sometimes is this overkill and makes the whole factor bigger for no reason

        # TODO: make the computation more readable
        item_crafting_time =  self.factory.crafting_time(self.assembler) / (output_needed if output_needed != 0 else 1)

        return [self.factory.required_amount(child.factory.name) * child.crafting_time() / item_crafting_time if item_crafting_time != 0 else 0 for child in self.children]

    def __str__(self) -> str:
        return self.factory.name

    """
    def __iter__(self):
        yield self

        for child in self.children:
            for descendant in child:
                yield descendant
    """