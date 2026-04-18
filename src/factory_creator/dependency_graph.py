#from graphviz import Digraph
from collections import defaultdict

from networkx import DiGraph

from .assembler import Assembler, AssemblingMachine3
from .factory import Item

import math

# TODO: electricity problem: in this state I only computes the layout of the factory but
#  do not compute with the fact, that all the factories have to be power by electricity.
#  Idea: this can be optional at this stage and required only before the evolution
#  algorithm stage. And at that point we would electrify the factory, if the electrification
#  is not possible, then the fitness would be zero.

class Stats:
    def __init__(self):
        self.approx_width = None

class DependencyTreeNode:
    def __init__(self, factory: Item, children: list[DependencyTreeNode], assembler: Assembler = AssemblingMachine3()):
        self.factory = factory
        self.children = children

        self.assembler = assembler
        self.stats = Stats()

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

        terminal_nodes = defaultdict(list)

        for node in graph.nodes:
            if graph.in_degree(node) == 0:
                terminal_nodes[graph.nodes[node]["label"]].append(node)

        # TODO: the splitter can only make from one belts two belts therefore makes
        #  sense that the nodes has at most degree 2 in the graph. On the other hand
        #  there is not need that the belt always terminates next to first inserter
        #  because one belts can service multiple ones. This difference can be good way
        #  how to differ individuals in the population generating

        for type in terminal_nodes.keys():
            source_node_id = f"{type}_source"

            graph.add_node(source_node_id, label=source_node_id, shape="ellipse")

            for terminal_node in terminal_nodes[type]:
                graph.add_edge(
                    source_node_id,
                    terminal_node,
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
            amount_needed_per_factory = amount_needed / math.ceil(amount_needed)

            for _ in range(max(1, math.ceil(amount_needed))):
                child_id, counter = child._dependency_graph(
                    dot,
                    counter,
                    amount_needed_per_factory,
                    show_amounts,
                    show_simplified
                )

                if show_amounts:
                    dot.add_edge(
                        child_id,
                        node_id,
                        label=f"{amount_needed if show_simplified else amount_needed_per_factory:0.4f}"
                    )
                else:
                    dot.add_edge(child_id, node_id)

                if show_simplified or child.factory.is_terminal:
                    break

        return node_id, counter

    def crafting_time(self) -> float:
        return self.factory.crafting_time(self.assembler)

    def relative_crafting_time(self, output_needed) -> float:
        return self.factory.crafting_time(self.assembler) / (output_needed if output_needed != 0 else 1)

    def number_of_ingredient_factories(self, output_needed) -> list[float]:
        # TODO: In this stage all stages has to create at least one item per second (or other time period),
        #  but I should be improved without this, because sometimes is this overkill and makes the whole
        #  factory bigger for no reason

        # TODO: make the computation more readable
        item_crafting_time = self.relative_crafting_time(output_needed)

        return [self._get_required_min_number_of_child_factory(child, item_crafting_time) for child in self.children]

    def _get_required_min_number_of_child_factory(
        self,
        child: DependencyTreeNode,
        item_crafting_time: float
    ) -> float:
        return self.factory.required_amount(child.factory.name) * child.crafting_time() / item_crafting_time if item_crafting_time != 0 else 0

    def _compute_approx_width(self, output_needed: float):
        number_of_ingredient_factories = self.number_of_ingredient_factories(output_needed)

        #print(self, *zip(self.children, number_of_ingredient_factories))
        #print(self, sum(math.ceil(amount_need) for amount_need in number_of_ingredient_factories))

        return max(
            math.ceil(output_needed),
            sum(1 if child.factory.is_terminal else math.ceil(amount_needed) * child.get_approx_width_of_tree(DependencyTreeNode.normalize_amount(amount_needed)) for child, amount_needed in zip(self.children, number_of_ingredient_factories))
        )

    def get_approx_width_of_tree(self, output_needed) -> int:
        if self.factory.is_terminal:
            self.stats.approx_width = 1

        if self.stats.approx_width is None:
            self.stats.approx_width = self._compute_approx_width(output_needed)

        return self.stats.approx_width

    # TODO: maybe move method bellow somewhere else
    @staticmethod
    def normalize_amount(amount: float) -> float:
        if math.ceil(amount) == 0:
            return 0

        return amount / math.ceil(amount)

    def __str__(self) -> str:
        return self.factory.name

    """
    def __iter__(self):
        yield self

        for child in self.children:
            for descendant in child:
                yield descendant
    """