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

    def dependency_graph(
            self,
            dot,
            counter,
            show_amounts = False,
            show_simplified = True
    ):
        node_id = f"n{counter}"
        dot.node(node_id, label=str(self))
        counter += 1

        for child, amount_needed in zip(self.children, self.number_of_ingredient_factories()):
            print(child, amount_needed)
            #amount_needed = self.factory.required_amount(child.factory.name)
            for _ in range(amount_needed):
                child_id, counter = child.dependency_graph(dot, counter, show_amounts, show_simplified)

                if show_amounts:
                    dot.edge(
                        child_id,
                        node_id,
                        label=str(amount_needed if show_simplified else child.factory.amount)
                    )
                else:
                    dot.edge(child_id, node_id)

                if show_simplified:
                    break

        return node_id, counter

    def crafting_time(self) -> float:
        print(self.factory.crafting_time(self.assembler))

        return self.factory.crafting_time(self.assembler)

    def number_of_ingredient_factories(self) -> list[int]:
        # TODO: In this stage all stages has to create at least one item per second (or other time period), but I should be improved without this, because sometimes is this overkill and makes the whole factor bigger for no reason

        item_crafting_time = self.factory.crafting_time(self.assembler)

        x =  [max(1, math.ceil(self.factory.required_amount(child.factory.name) * child.crafting_time() / item_crafting_time if item_crafting_time != 0 else 1)) for child in self.children]

        print(x)

        return x

    def __str__(self) -> str:
        return self.factory.name

    """
    def __iter__(self):
        yield self

        for child in self.children:
            for descendant in child:
                yield descendant
    """