import math
import random

import networkx
import collections
import heapq

from networkx import DiGraph

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

    # This is the number of tiles red fast underground belt can travel
    UNDERGROUND_MOVE_LENGTH = 6
    UNDERGROUND_MOVES_ENABLED = True

    USE_A_STAR = True # If false, then BFS would be used
    ENABLE_UNFINISH_BELTS = False # ONLY FOR DEBUGGING PURPOSES

    DEFAULT_WIDTH_MULTIPLIER = 10
    DEFAULT_DEPTH_MULTIPLIER = 10
    DEFAULT_PADDING = 1

    @staticmethod
    def convert_via_heuristics(graph: DiGraph, root: DependencyTreeNode) -> Grid:
        """
        Converts factory from graph to grid representation with the use of heuristics
        and general graph algorithms.

        :param graph: Graph of the factory that will be transformed.
        :param root: Root the recipe dependency tree.
        :return: Grid representation of the factory.
        """

        padding = GraphToMatrix.DEFAULT_PADDING

        max_width = root.get_approx_width_of_tree()
        max_depth = networkx.dag_longest_path_length(graph) + 1

        width_multiplier = GraphToMatrix.DEFAULT_WIDTH_MULTIPLIER
        depth_multiplier = GraphToMatrix.DEFAULT_DEPTH_MULTIPLIER

        grid = None

        successful = False
        while not successful:
            try:
                grid =  GraphToMatrix._compute_grid(
                    graph,
                    root,
                    padding = padding,
                    width_multiplier = width_multiplier,
                    max_width = max_width,
                    depth_multiplier = depth_multiplier,
                    max_depth = max_depth
                )

                successful = True
            except Exception as e:
                padding *= 2
                width_multiplier *= 2
                depth_multiplier *= 2

                print(padding, width_multiplier, depth_multiplier)

                print(e)

        return grid

    @staticmethod
    def _compute_grid(
        graph: networkx.classes.DiGraph,
        root: DependencyTreeNode,
        padding,
        width_multiplier,
        max_width,
        depth_multiplier,
        max_depth
    ) -> Grid:
        matrix_width = width_multiplier * max_width
        matrix_depth = depth_multiplier * max_depth + 10

        grid = Grid()

        # TODO: maybe we want nondeterministic BFS, so we get different planar graphs, therefore
        # we should shuffle the children of the nodes

        # TODO: consider using custom BFS that would non-deterministically assign the depth to the node,
        # if there is space of change

        root_cord = (10, matrix_width // 2)
        # TODO: resolve warning (at method get_cords not only to factory but also item)

        grid.add_factory(
            root_cord,
            str(root),
            [sur for sur in root.factory.get_cords(root_cord) if sur != root_cord]
        )

        graph.nodes[DependencyTreeNode.get_root_identifier()]["cord"] = root_cord

        # TODO: fistly place building then find belts
        # TODO: maybe makes more sense to compute the layers only based on the graph with the inbuild networkx function
        # best thing would be to use networkx.brf_layers but this methods (as far a know) does not provided the reverse option

        active_layer = {}

        # TODO: rewrite to more prettier way

        number_of_sources = GraphToMatrix.get_number_of_sources(graph) + 1
        number_of_sources_placed = 1

        for from_node in reversed(list(networkx.topological_sort(graph))):
            print(f"Building building: {from_node}")

            # Filter out the sink node, because we are define it above.
            if graph.out_degree(from_node) == 0:
                continue

            if "ref" in graph.nodes[from_node]:
                dependency_node = graph.nodes[from_node]["ref"]
                node_layer = dependency_node.get_layer()

                if node_layer not in active_layer:
                    active_layer[node_layer] = padding + math.floor(0.1 * matrix_width)

                cord = (node_layer * depth_multiplier + 10,
                        active_layer[node_layer] + dependency_node.get_approx_width_of_tree() // 2)

                active_layer[node_layer] += dependency_node.get_approx_width_of_tree() * width_multiplier

                grid.add_factory(
                    cord,
                    str(dependency_node),
                    [sur for sur in dependency_node.factory.get_cords(cord) if sur != cord]
                )
            else:
                source_layer = matrix_depth - 1
                offset_in_layer = math.floor(number_of_sources_placed / number_of_sources * matrix_width)

                number_of_sources_placed += 1

                cord = (source_layer, offset_in_layer)

                grid.add_source(cord, from_node)

            graph.nodes[from_node]["cord"] = cord

        for from_node in reversed(list(networkx.topological_sort(graph))):
            cord = graph.nodes[from_node]["cord"]

            # TODO: extract into one function
            if "ref" in graph.nodes[from_node]:
                dependency_node = graph.nodes[from_node]["ref"]
                from_cords = [c for c in dependency_node.factory.get_cords(cord)]
                is_in_cords = dependency_node.factory.get_cords_lambda(cord)

                element_type = str(dependency_node)
            else:
                from_cords = [cord]
                is_in_cords = lambda new_cord: new_cord == cord

                element_type = from_node

            for successor in graph.successors(from_node):
                print(f"Building path: {element_type}, {from_node}, {cord}, {successor}, {graph.nodes[successor]["cord"]}")

                if "ref" in graph.nodes[successor]:
                    is_in_successor = graph.nodes[successor]["ref"].factory.get_cords_lambda(
                        graph.nodes[successor]["cord"])

                    to_cords = [c for c in
                                graph.nodes[successor]["ref"].factory.get_cords(graph.nodes[successor]["cord"])]
                else:
                    is_in_successor = lambda new_cord: new_cord == graph.nodes[successor]["cord"]

                    to_cords = [graph.nodes[successor]["cord"]]

                GraphToMatrix.find_path(
                    cord,
                    from_cords,
                    is_in_cords,
                    graph.nodes[successor]["cord"],
                    to_cords,
                    is_in_successor,
                    grid,
                )

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

        if GraphToMatrix.USE_A_STAR:
            active_cord, visited_matrix = GraphToMatrix.a_star(
                from_cords,
                is_in_successor,
                to_cords,
                grid
            )
        else:
            active_cord, visited_matrix = GraphToMatrix.bfs(
                from_cords,
                is_in_successor,
                grid
            )

        start_cord = None
        last_cord = None
        active_orientation = None
        underground_next = False
        while not is_in_cords(active_cord):
            next_cord, next_orientation = GraphToMatrix.get_path_predecessor(active_cord, visited_matrix, to_cords)

            if start_cord is None:
                start_cord = next_cord

            if not is_in_cords(active_cord) and not is_in_successor(active_cord):
                distance = GraphToMatrix.distance_between_basis_vectors(active_cord, next_cord)

                if underground_next:
                    opposite_orientation = GraphToMatrix.get_orientation_in_opposite_direction(active_orientation)

                    grid.add_transportation(
                        cord=active_cord,
                        name="fast-underground-belt",
                        orientation=opposite_orientation,
                        from_cord=from_cord,
                        to_cord=to_cord
                    )

                    underground_next = False
                elif distance == 1:
                    grid.add_transportation(
                        cord=active_cord,
                        name="transport-belt",
                        orientation=active_orientation,
                        from_cord=from_cord,
                        to_cord=to_cord
                    )
                else:
                    grid.add_transportation(
                        cord=active_cord,
                        name="fast-underground-belt",
                        orientation=active_orientation,
                        from_cord=from_cord,
                        to_cord=to_cord
                    )

                    underground_next = True

            """
            if not is_in_cords(active_cord) and not is_in_successor(active_cord):
                distance = GraphToMatrix.distance_between_basis_vectors(active_cord, next_cord)

                if distance == 1:
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

                    grid.add_transportation(
                        cord = start_of_underground_belt,
                        name = "fast-underground-belt",
                        orientation = opposite_orientation,
                        from_cord= from_cord,
                        to_cord= to_cord
                    )

                    grid.add_transportation(
                        cord = active_cord,
                        name = "fact-underground-belt",
                        orientation = active_orientation,
                        from_cord= from_cord,
                        to_cord= to_cord
                    )
                """

            last_cord = active_cord
            active_cord = next_cord
            active_orientation = next_orientation

        grid.transform_into_inserter(last_cord)

        if start_cord != last_cord:
            grid.transform_into_inserter(start_cord) # TODO: it is needed to ensure that path is find that way that last 2 and first 2 transportation elements has same orientation (same orientation is not necessary but it has to be one of possible approaches such as L connection etc.)

        """
        (Belt) -> (Inserter) -> (Factory)
        (Belt)
          |
          v
        (inserter)
          |
          V
        (Factory)
        """

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

        heap = [AStartNode(from_cord, 0, GraphToMatrix.get_manhattan_metric(from_cord, to_cords) + GraphToMatrix.evaluate_borders(from_cord, from_cords)) for from_cord in from_cords]
        heapq.heapify(heap)

        visited_matrix = {}
        for entry in heap:
            visited_matrix[entry.cord] = 0

        active_cord = 0
        found = False

        last_len = 0
        while not found and len(heap) != 0 and len(visited_matrix) <= 1_000_000: #TODO: remove limit
            if len(visited_matrix) - last_len >= 100_000:
                last_len = len(visited_matrix)
                print(f"tu {len(visited_matrix)}")

            a_star_node = heapq.heappop(heap)
            #print(a_star_node)

            # TODO: There is a problem with underground belts, I want them to be used if and only if are needed
            #  but every configuration I think of needs to know about the obstacles
            #  Maybe the solutions is to always "enable" underground belts but give them cost as if it was
            #  multiple above ground (the cost would be the distance), so if there is both ways (same length)
            #  under and above ground, then with the implementation as it is, we would choose the above ground

            if is_in_successor(a_star_node.cord):
                active_cord = a_star_node.cord

                break

            # TODO: at this points we are looking for arbitrary shortest path, but if we want to enforce "esthetics" maybe
            #  makes sense for example to get values to the surrounding of factory and if we preferre it to be at the center
            #  we give the points more or less points
            found_way = False

            for multiplier in range(1, GraphToMatrix.UNDERGROUND_MOVE_LENGTH):
                for new_cord in GraphToMatrix.get_moves(a_star_node.cord, visited_matrix, multiplier=multiplier):
                    if new_cord in grid and not is_in_successor(new_cord):
                        visited_matrix[new_cord] = -1
                    else:
                        heapq.heappush(
                            heap,
                            AStartNode(
                                new_cord,
                                a_star_node.depth + multiplier, # TODO: maybe makes sense to instead all times have 1 to use multiplier so using underground belts hold some wight
                                a_star_node.depth + multiplier + GraphToMatrix.get_manhattan_metric(new_cord, to_cords) + GraphToMatrix.evaluate_borders(new_cord, to_cords)
                            )
                        )
                        visited_matrix[new_cord] = a_star_node.depth + multiplier
                        found_way = True

                    #TODO: remove
                    active_cord = new_cord

                #if found_way or found or not GraphToMatrix.UNDERGROUND_MOVES_ENABLED:
                #    break

        if len(visited_matrix) > 1_000_000 and not GraphToMatrix.ENABLE_UNFINISH_BELTS:
            raise Exception("Unable to find a path")

        return active_cord, visited_matrix

    @staticmethod
    def evaluate_borders(cord, points):
        return 0

        NOT_CENTER_PENALTY = 100

        #TODO: for correct A* with penalties is necessary to add reopening

        if cord not in points:
            return NOT_CENTER_PENALTY

        cx, cy = (sum(x[0] for x in points) / len(points), sum(x[1] for x in points) / len(points))
        x, y = cord

        #print(f"x {cord}, {points}")
        #if abs(cx - x) + abs(cy - y) == 1:
            #print(cord, points)

        return 0 if abs(cx - x) + abs(cy - y) == 1 else NOT_CENTER_PENALTY

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

        for i, move in enumerate(Grid.GRID_MOVES):
            new_cord = (from_cord[0] + multiplier * move[0], from_cord[1] + multiplier * move[1])

            if (was_visited and new_cord in visited_matrix) or (not was_visited and new_cord not in visited_matrix):
                yield new_cord if not return_enumeration else (i, new_cord)


    @staticmethod
    def _get_standard_move(from_cord, visited_matrix, multiplier, was_visited = False, return_enumeration = False):
        normal_move_was_used = False

        for i, move in enumerate(Grid.GRID_MOVES):
            new_cord = (from_cord[0] + multiplier * move[0], from_cord[1] + multiplier * move[1])

            if (was_visited and new_cord in visited_matrix) or (not was_visited and new_cord not in visited_matrix):
                normal_move_was_used = True

                yield new_cord if not return_enumeration else (i, new_cord)

        return normal_move_was_used

    @staticmethod
    def get_path_predecessor(cord, visited_matrix, to_cords):
        """
        Returns coordinate from which we could have gone to the current one.

        :param cord: Coordinates of the current position.
        :param visited_matrix: Matrix denoting if we achieved position and in how many steps.
        :return: Coordinate from which we could have gone to the current one.
        """

        for multiplier in range(1, GraphToMatrix.UNDERGROUND_MOVE_LENGTH):
            for enumeration, new_cord in GraphToMatrix.get_moves(cord, visited_matrix, multiplier=multiplier, was_visited=True, return_enumeration=True):
                if (visited_matrix[cord] - visited_matrix[new_cord]) == multiplier and new_cord not in to_cords:
                    return new_cord, GraphToMatrix.get_enumeration_to_orientation(enumeration)

        raise ValueError(f"While backtracking path to the starting points at {cord} no predecessor was found.")

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

    @staticmethod
    def get_number_of_sources(graph: DiGraph) -> int:
        n = 0

        for node in graph.nodes:
            if "source" in graph.nodes[node]["label"]:
                n += 1

        return n

# https://wiki.factorio.com/Blueprint_string_format
# https://github.com/redruin1/factorio-blueprint-schemas