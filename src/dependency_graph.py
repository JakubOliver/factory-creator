from .factory import Item

class DependencyTreeNode:
    def __init__(self, factory: Item, children: list[DependencyTreeNode]):
        self.factory = factory
        self.children = children

    def dfs(self):
        print(self.factory)

        for child in self.children:
            child.dfs()

    def dependency_graph(self, dot, counter, show_amounts = False, show_simplified = True):
        node_id = f"n{counter}"
        dot.node(node_id, label=str(self))
        counter += 1

        for child in self.children:
            # TODO: change logic from unsimplified to simplified
            amount_needed = self.factory.required_amount(child.factory.name)
            amount_processes = 0

            while amount_processes < amount_needed:
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
                else:
                    amount_processes += child.factory.amount

        return node_id, counter

    def node_parent(self, parent_idx = None, counter = None):
        node_idx = parent_idx + 1 if parent_idx is not None else 0
        counter = counter + 1 if counter is not None else node_idx

        yield node_idx, str(self), parent_idx, counter

        for child in self.children:
            for child_idx, child_id, ancestor_idx, new_counter in child.node_parent(node_idx, counter):
                counter = new_counter

                yield child_idx, child_id, ancestor_idx, counter

    def __str__(self) -> str:
        return self.factory.name

    """
    def __iter__(self):
        yield self

        for child in self.children:
            for descendant in child:
                yield descendant
    """