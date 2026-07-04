import math
import random

import networkx
import collections
import heapq

from .dependency_graph import DependencyTreeNode
from .grid import *

class AStartNode:
    """
    Represents heap node witch wraps information necessary for A* computation.
    """

    def __init__(self, cord, depth, comp):
        self.cord = cord
        self.depth = depth
        self.comp = comp

    def __lt__(self, other):
        if self.comp != other.comp:
            return self.comp < other.comp

        return self.cord < other.cord

    def __str__(self):
        return f"{self.cord}, {self.depth}, {self.comp}"


# TODO: factorio building has the coordination set to their center
class GraphToMatrix:
    """
    Wrapper for the methods which transform factory from graph representation
    into the grid representation.
    """

    grid_moves = [(0, 1), (-1, 0), (0, -1), (1, 0)]
    # In Factorio the orientation is
    #  Up: 0
    #  Right: 4
    #  Down: 8
    #  Left: 12

    # When we compute the path between assemblers we go against the orientation.
    # Therefore, the move array is in this strange order.

    # This is the number of tiles red fast underground belt can travel
    UNDERGROUND_MOVE_LENGTH = 6
    UNDERGROUND_MOVES_ENABLED = True

    @staticmethod
    def convert_via_heuristics(graph: networkx.classes.DiGraph, root: DependencyTreeNode) -> Grid:
        """
        Converts factory from graph to grid representation with the use of heuristics
        and general graph algorithms.

        :param graph: Graph of the factory that will be transformed.
        :param root: Root the recipe dependency tree.
        :return: Grid representation of the factory.
        """

        max_width = root.get_approx_width_of_tree()
        max_depth = networkx.dag_longest_path_length(graph) + 1

        #TODO: better
        width_multiplicator = 10
        depth_multiplicator = 10

        padding = 0
        matrix_width = width_multiplicator * max_width
        matrix_depth = depth_multiplicator * max_depth + 10

        grid = Grid()

        #TODO: maybe we want nondeterministic BFS, so we get different planar graphs, therefore
        # we should shuffle the children of the nodes

        #TODO: consider using custom BFS that would non-deterministically assign the depth to the node,
        # if there is space of change

        root_cord = (10, matrix_width // 2)
        #TODO: resolve warning (at method get_cords not only to factory but also item)

        grid.add_factory(
            root_cord,
            str(root),
            [sur for sur in root.factory.get_cords(root_cord) if sur != root_cord]
        )
        """
        grid[root_cord] = GridEntry(str(root), is_factory=True)
        for cord in root.factory.get_cords(root_cord):
            if cord != root_cord:
                grid.set_occupied(cord, root_cord)
        """


        graph.nodes[DependencyTreeNode.get_root_identifier()]["cord"] = root_cord

        #TODO: fistly place building then find belts
        #TODO: maybe makes more sense to compute the layers only based on the graph with the inbuild networkx function
        # best thing would be to use networkx.brf_layers but this methods (as far a know) does not provided the reverse option

        active_layer = {}

        # TODO: rewrite to more prettier way

        # TODO: remove and repair the code
        EXPERIMENTAL = False
        max_layer_used = 0

        #for to_node, from_node in networkx.bfs_edges(graph, source=DependencyTreeNode.get_root_identifier(), reverse=True):
        for from_node in reversed(list(networkx.topological_sort(graph))):
            print(from_node)

            # Filter out the sink node, because we are define it above.
            if graph.out_degree(from_node) == 0:
                continue

            if "ref" in graph.nodes[from_node]:
                dependency_node = graph.nodes[from_node]["ref"]
                node_layer = dependency_node.get_layer()

                if EXPERIMENTAL:
                    max_layer_used = max(max_layer_used, node_layer)

                element_type = str(dependency_node)

                if node_layer not in active_layer:
                    active_layer[node_layer] = padding + math.floor(0.1 * matrix_width)

                cord = (node_layer * depth_multiplicator + 10, active_layer[node_layer] + dependency_node.get_approx_width_of_tree() // 2)

                active_layer[node_layer] += dependency_node.get_approx_width_of_tree() * width_multiplicator

                # TODO: add functino for this, because this work if and only if building is created before surroundings
                grid.add_factory(
                    cord,
                    str(dependency_node),
                    [sur for sur in dependency_node.factory.get_cords(cord) if sur != cord]
                )

                """
                grid[cord] = GridEntry(str(dependency_node), is_factory=True)
                for building_cord in dependency_node.factory.get_cords(cord):
                    if building_cord != cord:
                        grid.set_occupied(building_cord, cord)
                """

                is_in_cords = dependency_node.factory.get_cords_lambda(cord)

                from_cords = [c for c in dependency_node.factory.get_cords(cord)]
            else:
                if EXPERIMENTAL:
                    source_layer = max(max_layer_used, max(x for x in active_layer.keys()) + 3)
                else:
                    source_layer = max(matrix_depth - 1, max(x for x in active_layer.keys()) + 3)

                if source_layer not in active_layer:
                    active_layer[source_layer] = padding + padding + math.floor(0.1 * matrix_width)

                offset_in_layer = math.floor((0.1 + random.random() / 2)  * matrix_width)

                cord = (source_layer, offset_in_layer)
                element_type = from_node

                #grid[cord] = GridEntry(from_node, entry_type=GridEntryTypes.Source)
                grid.add_source(cord, from_node)

                is_in_cords = lambda new_cord : new_cord == cord
                from_cords = [cord]

            graph.nodes[from_node]["cord"] = cord

            for successor in graph.successors(from_node):
                print(element_type, from_node, cord, successor, graph.nodes[successor]["cord"])

                if "ref" in graph.nodes[successor]:
                    is_in_successor = graph.nodes[successor]["ref"].factory.get_cords_lambda(graph.nodes[successor]["cord"])

                    to_cords = [c for c in graph.nodes[successor]["ref"].factory.get_cords(graph.nodes[successor]["cord"])]
                else:
                    is_in_successor = lambda new_cord : new_cord == graph.nodes[successor]["cord"]

                    to_cords = [graph.nodes[successor]["cord"]]

                try:
                    GraphToMatrix.find_path(
                        cord,
                        from_cords,
                        is_in_cords,
                        graph.nodes[successor]["cord"],
                        to_cords,
                        is_in_successor,
                        grid,
                    )
                except Exception as e:
                    print(f"failed: {e}")
                    continue

        return grid

    @staticmethod
    def find_path(
        from_cord,
        from_cords,
        is_in_cords,
        to_cord,
        to_cords,
        is_in_successor,
        grid,
    ) -> None:
        """
        Finds path between provided coordinates/elements in the grid
        and updates the grid.

        :param from_cords: Coordinate of the starting elements.
        :param is_in_cords: Function denoting whether coordinate is
            inside the starting elements.
        :param to_cords: Coordinate of the ending elements.
        :param is_in_successor: Function denoting whether coordinate is
            inside the ending elements.
        :param grid: Grid representation of the factory.
        """

        """
        active_cord, visited_matrix = GraphToMatrix.bfs(
            from_cords,
            is_in_successor,
            matrix
        )
        """
        active_cord, visited_matrix = GraphToMatrix.a_star(
            from_cords,
            is_in_successor,
            to_cords,
            grid
        )

        active_orientation = None
        while not is_in_cords(active_cord):
            next_cord, next_orientation = GraphToMatrix.get_path_predecessor(active_cord, visited_matrix)

            if not is_in_cords(active_cord) and not is_in_successor(active_cord):
                distance = GraphToMatrix.distance_between_basis_vectors(active_cord, next_cord)
                if distance == 1:
                    #active_orientation = 0 if active_orientation is None else active_orientation #TODO: remove
                    #grid[active_cord] = GridEntry("transport-belt", orientation=active_orientation)
                    grid.add_transportation(
                        cord = active_cord,
                        name = "transport-belt",
                        orientation = active_orientation,
                        from_cord= from_cord,
                        to_cord= to_cord
                    )
                else:
                    #TODO: better approach will be to remember, that we used underground belts and
                    # create it in next step, because in this form, it only "works" with skipping one belt
                    start_of_underground_belt = GraphToMatrix.cord_after_previous_in_direction(next_cord, active_cord)
                    opposite_orientation = GraphToMatrix.get_orientation_in_opposite_direction(active_orientation)

                    #grid[start_of_underground_belt] = GridEntry("fast-underground-belt", orientation=opposite_orientation)
                    grid.add_transportation(
                        cord = start_of_underground_belt,
                        name = "fast-underground-belt",
                        orientation = opposite_orientation,
                        from_cord= from_cord,
                        to_cord= to_cord
                    )

                    #grid[active_cord] = GridEntry("fast-underground-belt", active_orientation)
                    grid.add_transportation(
                        cord = active_cord,
                        name = "fact-underground-belt",
                        orientation = active_orientation,
                        from_cord= from_cord,
                        to_cord= to_cord
                    )

            active_cord = next_cord
            active_orientation = next_orientation

    @staticmethod
    def bfs(from_cords, is_in_successor, grid):
        """
        Finds path between elements in the grid with the usage
        of Breath First Search (BFS).

        :param from_cords: Coordinate of the starting elements.
        :param is_in_successor: Function provided information whether the coordinate
            is inside the ending element.
        :param grid: Grid representation of the factory.
        :return: Returns the pair of the points in the grid, which lays inside the ending elements
            and has the shortest distance to the starting element. And the matrix of the coordinates
            with the information in how many steps can be coordinate achieved.
        """

        queue = collections.deque([(from_cord, 1) for from_cord in from_cords])

        visited_matrix = {}
        for from_cord in from_cords:
            visited_matrix[from_cord] = 1

        active_cord = None
        found = False
        while not found and len(queue) != 0:
            cord, depth = queue.popleft()

            for new_cord in GraphToMatrix.get_moves(cord, visited_matrix):
                if is_in_successor(new_cord):
                    visited_matrix[new_cord] = depth + 1
                    active_cord = new_cord

                    found = True
                    break

                if new_cord not in grid:
                    queue.append((new_cord, depth + 1))
                    visited_matrix[new_cord] = depth + 1
                else:
                    visited_matrix[new_cord] = -1

        return active_cord, visited_matrix

    @staticmethod
    def a_star(from_cords, is_in_successor, to_cords, grid):
        """
        Finds path between elements in the grid with the usage
        of the A* algorithm and manhattan distance.

        :param from_cords: Coordinate of the starting elements.
        :param is_in_successor: Function provided information whether the coordinate
            is inside the ending element.
        :param to_cords: Coordinate of the ending elements.
        :param grid: Grid representation of the factory.
        :return: Returns the pair of the points in the grid, which lays inside the ending elements
            and has the shortest distance to the starting element. And the matrix of the coordinates
            with the information in how many steps can be coordinate achieved.
        """

        heap = [AStartNode(from_cord, 0, GraphToMatrix.get_manhattan_metric(from_cord, to_cords)) for from_cord in from_cords]
        heapq.heapify(heap)

        visited_matrix = {}
        for entry in heap:
            visited_matrix[entry.cord] = 0

        active_cord = 0
        found = False
        while not found and len(heap) != 0 and len(heap) <= 1_000_000: #TODO: remove limit
            a_star_node = heapq.heappop(heap)
            #print(a_star_node)

            # TODO: There is a problem with underground belts, I want them to be used if and only if are needed
            #  but every configuration I think of needs to know about the obstacles
            #  Maybe the solutions is to always "enable" underground belts but give them cost as if it was
            #  multiple above ground (the cost would be the distance), so if there is both ways (same length)
            #  under and above ground, then with the implementation as it is, we would choose the above ground
            """
            for new_cord in GraphToMatrix.get_moves(a_star_node.cord, visited_matrix):
                if new_cord in matrix:
                    visited_matrix[new_cord] = -1
            """
            found_way = False

            for multiplier in range(1, GraphToMatrix.UNDERGROUND_MOVE_LENGTH):
                for new_cord in GraphToMatrix.get_moves(a_star_node.cord, visited_matrix, multiplier=multiplier):
                    if is_in_successor(new_cord):
                        visited_matrix[new_cord] = a_star_node.depth + 1
                        active_cord = new_cord

                        found = True
                        break

                    if new_cord in grid:
                        visited_matrix[new_cord] = -1
                    else:
                        heapq.heappush(
                            heap,
                            AStartNode(
                                new_cord,
                                a_star_node.depth + 1, # TODO: maybe makes sense to instead all times have 1 to use multiplier so using underground belts hold some wight
                                a_star_node.depth + 1 + GraphToMatrix.get_manhattan_metric(new_cord, to_cords)
                            )
                        )
                        visited_matrix[new_cord] = a_star_node.depth + 1
                        found_way = True

                        #print(GraphToMatrix.get_manhattan_metric(new_cord, to_cords))

                    #TODO: remove
                    active_cord = new_cord

                if found_way or found:
                    break

                #print("way not found")

        return active_cord, visited_matrix

    @staticmethod
    def get_manhattan_metric(from_cord, to_cords):
        """
        Returns the minimal manhattan distance between coordinate and the
        coordinates of the final elements.

        :param from_cord: Staring coordinates.
        :param to_cords:
        :return: The minimal manhattan distance between coordinate and
            the coordinates of the final elements.
        """

        return min((sum(abs(x - y) for x, y in zip(from_cord, to_cord)) for to_cord in to_cords))

    @staticmethod
    def get_moves(from_cord, visited_matrix, multiplier = 1, was_visited = False, return_enumeration = False):
        """
        Iterator over the coordinates which can be achieved from the provided coordinate.

        :param from_cord: Starting coordinate.
        :param visited_matrix: Matrix denoting if we achieved position and in how many steps.
        :param multiplier: How may points in the grid can se move across in one points.
        :param was_visited: Denotes whether we return position which were previously visited.
        :param return_enumeration: Denotes whether we return the number of the orientation.
        :return: Coordination of the points achievable from the provided coordinate.
        """

        """
        for multiplier in range(1, GraphToMatrix.UNDERGROUND_MOVE_LENGTH):
            #print(multiplier)
            smaller_move_found = yield from GraphToMatrix._get_standard_move(from_cord, visited_matrix, multiplier, was_visited, return_enumeration)

            if smaller_move_found or not GraphToMatrix.UNDERGROUND_MOVES_ENABLED:
                return

            #print("vetsi pouzit", multiplier + 1)
        """

        for i, move in enumerate(GraphToMatrix.grid_moves):
            new_cord = (from_cord[0] + multiplier * move[0], from_cord[1] + multiplier * move[1])

            if (was_visited and new_cord in visited_matrix) or (not was_visited and new_cord not in visited_matrix):
                yield new_cord if not return_enumeration else (i, new_cord)


    @staticmethod
    def _get_standard_move(from_cord, visited_matrix, multiplier, was_visited = False, return_enumeration = False):
        normal_move_was_used = False

        for i, move in enumerate(GraphToMatrix.grid_moves):
            new_cord = (from_cord[0] + multiplier * move[0], from_cord[1] + multiplier * move[1])

            if (was_visited and new_cord in visited_matrix) or (not was_visited and new_cord not in visited_matrix):
                normal_move_was_used = True

                yield new_cord if not return_enumeration else (i, new_cord)

        return normal_move_was_used

    @staticmethod
    def get_path_predecessor(cord, visited_matrix):
        """
        Returns coordinate from which we could have gone to the current one.

        :param cord: Coordinates of the current position.
        :param visited_matrix: Matrix denoting if we achieved position and in how many steps.
        :return: Coordinate from which we could have gone to the current one.
        """

        for multiplier in range(1, GraphToMatrix.UNDERGROUND_MOVE_LENGTH):
            for enumeration, new_cord in GraphToMatrix.get_moves(cord, visited_matrix, multiplier=multiplier, was_visited=True, return_enumeration=True):
                if (visited_matrix[cord] - visited_matrix[new_cord]) == 1:
                    return new_cord, GraphToMatrix.get_enumeration_to_orientation(enumeration)

        #TODO: better exception
        print(cord)
        print(visited_matrix)
        raise ValueError("No predecessors")

    @staticmethod
    def get_enumeration_to_orientation(enumeration: int) -> int:
        """
        Returns orientation representation in Factorio format from the number of basis vector.

        :param enumeration: Number of the basis vector.
        :return: Returns orientation representation in Factorio format.
        """

        return enumeration * 4

    @staticmethod
    def get_orientation_in_opposite_direction(orientation: int) -> int:
        """
        Returns opposite orientation in the Factorio format.

        :param orientation: Original orientation.
        :return: Opposite orientation in the Factorio format.
        """

        return (orientation + 8) % 16

    @staticmethod
    def distance_between_basis_vectors(x: tuple, y:tuple) -> int:
        """
        Returns size of multiple of basis vector which applied to the one
        vector the other one can be achieved.

        :param x: First 2D vector.
        :param y: Second 2D vector.
        :return: Returns size of multiple basis vector.
        """

        #TODO: check whether are same basis vector

        return max(abs(x[0] - y[0]), abs(x[1] - y[1]))

    @staticmethod
    def cord_after_previous_in_direction(active: tuple, prev: tuple):
        """
        Returns coordinates of the grid position which comes right
        before the active coordinates.

        :param active: Coordinates of the active position in the grid.
        :param prev: Coordinates of the previous position in the grid.
        :return: Coordinates of the grid position which comes right before
            the active coordinates.
        """

        distance = GraphToMatrix.distance_between_basis_vectors(active, prev)
        orientation_vector = ((active[0] - prev[0]) / distance, (active[1] - prev[1]) / distance)

        return prev[0] + 2 * orientation_vector[0], prev[1] + 2 * orientation_vector[1]

# https://wiki.factorio.com/Blueprint_string_format
# https://github.com/redruin1/factorio-blueprint-schemas