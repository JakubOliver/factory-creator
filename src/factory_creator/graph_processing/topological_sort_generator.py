import random

from networkx import DiGraph

class TopologicalSortGenerator:
    @staticmethod
    def generate_random(graph: DiGraph) -> list:
        working_graph = graph.copy()

        for node in working_graph.nodes:
            #working_graph.nodes[node]["weight"] = 1 + working_graph.out_degree(node)
            working_graph.nodes[node]["weight"] = 1

        topological_ordering = []

        while len(working_graph.nodes) > 0:
            zero_out_degree_nodes = [
                node for node in working_graph.nodes if working_graph.out_degree(node) == 0
            ]

            weights = [working_graph.nodes[node]["weight"] for node in zero_out_degree_nodes]
            selected_node = random.choices(zero_out_degree_nodes, weights=weights)[0]

            topological_ordering.append(selected_node)

            working_graph.remove_node(selected_node)

        topological_ordering.reverse()
        return topological_ordering


# P. García-Segador, P. Miranda: Bottom-Up: A new algorithm to generate random linear extensions of a poset
# https://docta.ucm.es/entities/publication/381ae9b7-5863-417e-be07-8d316624df52
# https://blogs.mat.ucm.es/pmiranda/wp-content/uploads/sites/47/2020/12/27-BottomUp.pdf

# Classic topological sort algorithm, and we choose a random node from list of nodes with out degree 0 based on weights.
# possible heuristics for weights:
# - all 1
# - out degree of node + 1

# Russ Bubley, Martin Dyer: Faster random generation of linear extensions, Discrete Mathematics 201, 1999
# https://www.math.cmu.edu/~af1p/Teaching/MCC17/Papers/linext.pdf
