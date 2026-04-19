import math
import random

import networkx
import collections

from src.factory_creator.dependency_graph import DependencyTreeNode

class Grid:
    def __init__(self):
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, item):
        return item in self.data

    def __iter__(self):
        for key in self.data.keys():
            yield key

# TODO: factorio building has the coordination set to their center
class GraphToMatrix:
    grid_moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    @staticmethod
    def convert_via_heuristics(graph: networkx.classes.DiGraph, root: DependencyTreeNode) -> Grid:
        max_width = root.get_approx_width_of_tree()
        max_depth = networkx.dag_longest_path_length(graph) + 1

        #TODO: better
        width_multiplicator = 10
        depth_multiplicator = 10

        padding = 0
        matrix_width = width_multiplicator * max_width
        matrix_depth = depth_multiplicator * max_depth + 10

        #TODO: instead of numpy matrix can be used networkx grid

        #TODO: enforce that all identifiers are shorter or equal 20 characters
        matrix = Grid()

        #TODO: maybe we want nondeterministic BFS, so we get different planar graphs, therefore
        # we should shuffle the children of the nodes

        #TODO: consider using custom BFS that would non-deterministically assign the depth to the node,
        # if there is space of change

        root_cord = (10, matrix_width // 2)
        #TODO: resolve warning (at method get_cords not only to factory but also item)
        for cord in root.factory.get_cords(root_cord):
            if cord != root_cord:
                matrix[cord] = "-"
            else:
                matrix[cord] = str(root)

        graph.nodes[DependencyTreeNode.get_root_identifier()]["cord"] = root_cord

        #TODO: fistly place building then find belts

        offset_in_layer = padding + math.floor(0.1 * matrix_width)
        active_layer = -1
        for to_node, from_node in networkx.bfs_edges(graph, source=DependencyTreeNode.get_root_identifier(), reverse=True):
            if "ref" in graph.nodes[from_node]:
                dependency_node = graph.nodes[from_node]["ref"]
                node_layer = dependency_node.get_layer()
                type = str(dependency_node)

                if active_layer != node_layer:
                    offset_in_layer = padding + math.floor(0.1 * matrix_width)
                    active_layer = node_layer

                cord = (node_layer * depth_multiplicator + 10, offset_in_layer + dependency_node.get_approx_width_of_tree() // 2)

                offset_in_layer += dependency_node.get_approx_width_of_tree() * width_multiplicator

                for building_cord in dependency_node.factory.get_cords(cord):
                    if building_cord != cord:
                        matrix[building_cord] = "-"

                matrix[cord] = str(dependency_node)

                is_in_cords = dependency_node.factory.get_cords_lambda(cord)

                from_cords = [c for c in dependency_node.factory.get_cords(cord)]
            else:
                active_layer = max(matrix_depth - 1, active_layer)

                offset_in_layer = math.floor((0.1 + random.random() / 2)  * matrix_width)
                active_layer += 1

                cord = (active_layer, offset_in_layer)
                type = from_node

                #offset_in_layer += math.floor(0.25 * matrix_width)

                matrix[cord] = from_node

                is_in_cords = lambda new_cord : new_cord == cord
                from_cords = [cord]

            graph.nodes[from_node]["cord"] = cord

            for successor in graph.successors(from_node):
                print(type, from_node, cord, successor, graph.nodes[successor]["cord"])

                if "ref" in graph.nodes[successor]:
                    is_in_successor = graph.nodes[successor]["ref"].factory.get_cords_lambda(graph.nodes[successor]["cord"])
                else:
                    is_in_successor = lambda new_cord : new_cord == graph.nodes[successor]["cord"]

                try:
                    GraphToMatrix.find_path(
                        from_cords,
                        is_in_cords,
                        is_in_successor,
                        matrix,
                        type
                    )
                except Exception as e:
                    print("failed")
                    break

        return matrix

    # TODO: heuristic for bfs
    @staticmethod
    def find_path(from_cords, is_in_cords, is_in_successor, matrix, belt_type):
        queue = collections.deque([(from_cord, 1) for from_cord in from_cords])

        visited_matrix = {}
        for from_cord in from_cords:
            visited_matrix[from_cord] = 1

        active_cord = None
        found = False
        while not found and len(queue) != 0:
            cord, depth = queue.popleft()
            #print(cord)

            for new_cord in GraphToMatrix.get_moves(cord, visited_matrix):
                if is_in_successor(new_cord):
                    visited_matrix[new_cord] = depth + 1
                    active_cord = new_cord

                    found = True
                    break

                if new_cord not in matrix:
                    queue.append((new_cord, depth + 1))
                    visited_matrix[new_cord] = depth + 1
                else:
                    visited_matrix[new_cord] = -1

        while not is_in_cords(active_cord):
            active_cord = GraphToMatrix.get_path_predecessor(active_cord, visited_matrix)

            if not is_in_cords(active_cord) and not is_in_successor(active_cord):
                matrix[active_cord] = f"{belt_type}-belt"

    @staticmethod
    def get_moves(from_cord, visited_matrix, was_visited = False):
        for move in GraphToMatrix.grid_moves:
            new_cord = (from_cord[0] + move[0], from_cord[1] + move[1])

            if (was_visited and new_cord in visited_matrix) or (not was_visited and new_cord not in visited_matrix):
                yield new_cord

    @staticmethod
    def get_path_predecessor(cord, visited_matrix):
        for new_cord in GraphToMatrix.get_moves(cord, visited_matrix, True):
            if (visited_matrix[cord] - visited_matrix[new_cord]) == 1:
                return new_cord

        #TODO: better exception
        raise ValueError()

# https://wiki.factorio.com/Blueprint_string_format
# https://github.com/redruin1/factorio-blueprint-schemas