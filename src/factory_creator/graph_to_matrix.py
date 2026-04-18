import math

import networkx
import numpy
import numpy as np
import collections

from matplotlib import pyplot as plt
from networkx.algorithms.isomorphism.vf2pp import vf2pp_is_isomorphic
from six import moves

from src.factory_creator.dependency_graph import DependencyTreeNode


class GraphToMatrix:
    grid_moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    @staticmethod
    def convert_via_heuristics(graph: networkx.classes.DiGraph, root: DependencyTreeNode) -> np.ndarray:
        print(root.get_approx_width_of_tree())
        print(root.get_approx_depth_of_tree())
        print(networkx.dag_longest_path_length(graph))

        max_width = root.get_approx_width_of_tree()
        max_depth = networkx.dag_longest_path_length(graph) + 1

        #TODO: better
        width_multiplicator = 5
        depth_multiplicator = 5

        matrix_width = width_multiplicator * max_width
        matrix_depth = depth_multiplicator * max_depth + 10

        #TODO: instead of numpy matrix can be used networkx grid

        #TODO: enforce that all identifiers are shorter or equal 20 characters
        matrix = np.zeros((matrix_depth, matrix_width), dtype="U20")
        print(matrix.dtype)

        #TODO: maybe we want nondeterministic BFS, so we get different planar graphs, therefore
        # we should shuffle the children of the nodes

        #TODO: consider using custom BFS that would non-deterministically assign the depth to the node,
        # if there is space of change


        matrix[(10, matrix_width // 2)] = str(graph.nodes[DependencyTreeNode.get_root_identifier()]["ref"])
        graph.nodes[DependencyTreeNode.get_root_identifier()]["cord"] = (10, matrix_width // 2)

        #TODO: fistly place building then find belts

        offset_in_layer = math.floor(0.1 * matrix_width)
        active_layer = -1
        for to_node, from_node in networkx.bfs_edges(graph, source=DependencyTreeNode.get_root_identifier(), reverse=True):
            if "ref" in graph.nodes[from_node]:
                dependency_node = graph.nodes[from_node]["ref"]
                node_layer = dependency_node.get_layer()
                type = str(dependency_node)

                if active_layer != node_layer:
                    offset_in_layer = math.floor(0.1 * matrix_width)
                    active_layer = node_layer

                cord = (node_layer * depth_multiplicator + 10, offset_in_layer + dependency_node.get_approx_width_of_tree() // 2)

                offset_in_layer += dependency_node.get_approx_width_of_tree() * width_multiplicator

                matrix[cord] = str(dependency_node)
            else:
                if active_layer != matrix_depth - 1:
                    offset_in_layer = math.floor(0.1 * matrix_width)

                cord = (matrix_depth - 1, offset_in_layer)
                type = from_node

                offset_in_layer += 1

                matrix[cord] = from_node

            graph.nodes[from_node]["cord"] = cord

            print(type, from_node, to_node)

            numpy.savetxt("matrix.csv", matrix, fmt="%s", delimiter=",")

            # TODO: here is needed to have for loop over the all successors of from_node because the from_node will be
            #  processed inside bfs only ones, therefore in the matrix will not be all edges

            GraphToMatrix.find_path(
                cord,
                graph.nodes[to_node]["cord"],
                matrix,
                type
            )

        """
        for depth, layer in enumerate(networkx.bfs_layers(graph, sources=DependencyTreeNode.get_root_identifier())):
            print(depth, layer)
        """

        #print(matrix)
        return matrix

    @staticmethod
    def find_path(from_cord, to_cord, matrix, belt_type):
        queue = collections.deque([(from_cord, 1)])

        visited_matrix = np.zeros(matrix.shape, dtype=int)
        visited_matrix[from_cord] = 1

        while len(queue) != 0:
            cord, depth = queue.popleft()

            for new_cord in GraphToMatrix.get_moves(cord, visited_matrix):
                if new_cord == to_cord:
                    visited_matrix[new_cord] = depth + 1
                    break

                if matrix[new_cord] == '':
                    queue.append((new_cord, depth + 1))
                    visited_matrix[new_cord] = depth + 1
                else:
                    visited_matrix[new_cord] = -1

        active_cord = to_cord
        length = visited_matrix[to_cord]
        print("length", length)
        print("from", from_cord)
        print("to", to_cord)

        while not np.array_equal(active_cord, from_cord):
            active_cord = GraphToMatrix.get_path_predecessor(active_cord, visited_matrix)

            matrix[active_cord] = belt_type

        numpy.savetxt("visited_matrix.csv", visited_matrix, fmt="%s", delimiter=",")

    @staticmethod
    def get_moves(from_cord, visited_matrix, unvisited = True):
        for move in GraphToMatrix.grid_moves:
            new_cord = (from_cord[0] + move[0], from_cord[1] + move[1])

            if 0 <= new_cord[0] < visited_matrix.shape[0] and 0 <= new_cord[1] < visited_matrix.shape[1] and (not unvisited or visited_matrix[new_cord] == 0):
                yield new_cord

    @staticmethod
    def get_path_predecessor(cord, visited_matrix):
        for new_cord in GraphToMatrix.get_moves(cord, visited_matrix, False):
            if (visited_matrix[cord] - visited_matrix[new_cord]) == 1:
                return new_cord

        print(cord)
        print(visited_matrix[cord])
        print(visited_matrix)

        #TODO: better exception
        raise ValueError()

# https://wiki.factorio.com/Blueprint_string_format
# https://github.com/redruin1/factorio-blueprint-schemas