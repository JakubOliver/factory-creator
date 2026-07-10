import math
import random

import networkx
import collections
import heapq

from networkx import DiGraph
from pyrsistent import pset

from .dependency_graph import DependencyTreeNode
from .grid import *
from .util.factorio_const import FactorioConst

class AStartNode:
    """
    Represents heap node witch wraps information necessary for A* computation.
    """

    def __init__(self, cord, depth, comp, orientation, streak, predecessor, path_set, is_start = False):
        self.cord = cord
        self.depth = depth
        self.comp = comp
        self.orientation = orientation
        self.streak = streak
        self.predecessor = predecessor
        self.path_set = path_set.add(cord)
        self.is_start = is_start

    def is_underground_belt_end(self):
        if self.predecessor is None:
            return False

        return abs(self.cord[0] - self.predecessor.cord[0]) + abs(self.cord[1] - self.predecessor.cord[1]) > 1

    def is_after_start(self):
        if self.predecessor is None:
            return False

        return self.predecessor.is_start

    def same_direction_is_needed(self):
        return self.is_after_start() or self.is_underground_belt_end()

    def __lt__(self, other):
        if self.comp != other.comp:
            return self.comp < other.comp

        if not self.is_underground_belt_end() and other.is_underground_belt_end():
            return True
        if self.is_underground_belt_end() and not other.is_underground_belt_end():
            return False

        return self.streak > other.streak

    def __str__(self):
        return f"Cord: {self.cord}, Depth: {self.depth}, Comp: {self.comp}, Orientation: {self.orientation}, Streak: {self.streak}"

class VisitedMatrix:
    def __init__(self):
        self.visited: dict[tuple[tuple, int | None, int, bool], int] = {}

    def __setitem__(self, key: tuple[tuple, int | None, int, bool], value: int):
        self.visited[key] = value

    def __len__(self):
        return len(self.visited)

    def __contains__(self, item):
        return item in self.visited

    def __str__(self):
        return str(self.visited)


class GraphToMatrix:
    """
    Wrapper for the methods which transform factory from graph representation
    into the grid representation.
    """

    UNDERGROUND_MOVES_ENABLED = True

    USE_A_STAR = True # If false, then BFS would be used
    ENABLE_UNFINISH_BELTS = False # ONLY FOR DEBUGGING PURPOSES

    A_STAR_STREAK_THRESHOLD = 1 # Can use underground belts if and only if the streak of orientation is bigger or equal to the threshold

    DEFAULT_WIDTH_MULTIPLIER = 10
    DEFAULT_DEPTH_MULTIPLIER = 10
    DEFAULT_PADDING = 1

    @staticmethod
    def convert_via_heuristics(
        graph: DiGraph, 
        root: DependencyTreeNode,
        report_method: callable = print
    ) -> Grid:
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
                    max_depth = max_depth,
                    report_method=report_method
                )

                successful = True
            except Exception as e:
                padding *= 2
                width_multiplier *= 2
                depth_multiplier *= 2

                report_method(f"padding, width_multiplier, depth_multiplier")

                report_method(e)
                #raise e

        return grid

    @staticmethod
    def _compute_grid(
        graph: networkx.classes.DiGraph,
        root: DependencyTreeNode,
        padding,
        width_multiplier,
        max_width,
        depth_multiplier,
        max_depth,
        report_method: callable = print
    ) -> Grid:
        matrix_width = width_multiplier * max_width
        matrix_depth = depth_multiplier * max_depth + 10

        grid = Grid()

        # TODO: maybe we want nondeterministic BFS, so we get different planar graphs, therefore
        # we should shuffle the children of the nodes

        # TODO: consider using custom BFS that would non-deterministically assign the depth to the node,
        # if there is space of change

        root_cord = (10, matrix_width // 2)

        grid.add_factory(
            root_cord,
            str(root),
            [sur for sur in root.factory.get_cords(root_cord) if sur != root_cord]
        )

        graph.nodes[DependencyTreeNode.get_root_identifier()]["cord"] = root_cord

        # TODO: maybe makes more sense to compute the layers only based on the graph with the inbuild networkx function
        # best thing would be to use networkx.brf_layers but this methods (as far a know) does not provided the reverse option

        active_layer = {}

        # TODO: rewrite to more prettier way

        number_of_sources = GraphToMatrix.get_number_of_sources(graph) + 1
        number_of_sources_placed = 1

        for from_node in reversed(list(networkx.topological_sort(graph))):


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

                report_building_name = str(dependency_node)
            else:
                source_layer = matrix_depth - 1
                offset_in_layer = math.floor(number_of_sources_placed / number_of_sources * matrix_width)

                number_of_sources_placed += 1

                cord = (source_layer, offset_in_layer)

                grid.add_source(cord, from_node)

                report_building_name = from_node

            report_method(f"Building source: {report_building_name}")

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
                report_method(f"Building path: {element_type}, {from_node}, {cord}, {successor}, {graph.nodes[successor]["cord"]}")

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
            a_star_node, visited_matrix = GraphToMatrix.a_star(
                from_cords,
                is_in_successor,
                to_cords,
                grid
            )
        else:
            # At this points BFS is not set for new version with nodes, therefore does not work
            raise Exception("At this points BFS is not set for new version with nodes, therefore does not work")
            active_cord, visited_matrix = GraphToMatrix.bfs(
                from_cords,
                is_in_successor,
                grid
            )

        start_cord = None
        last_node = None
        underground_next = False

        while not is_in_cords(a_star_node.cord):
            next_node = a_star_node.predecessor

            if not is_in_cords(a_star_node.cord) and not is_in_successor(a_star_node.cord):
                if start_cord is None:
                    start_cord = a_star_node.cord

                distance = GraphToMatrix.distance_between_basis_vectors(a_star_node.cord, next_node.cord)

                if underground_next:
                    opposite_orientation = GraphToMatrix.get_orientation_in_opposite_direction(GraphToMatrix.get_enumeration_to_orientation(a_star_node.orientation)) # TODO: resolve that opposite is not really opposite in input also in output

                    grid.add_transportation(
                        cord=a_star_node.cord,
                        name=FactorioConst.FAST_UNDERGROUND_BELT,
                        orientation=opposite_orientation,
                        from_cord=from_cord,
                        to_cord=to_cord,
                        underground_belt_type=FactorioConst.UNDERGROUND_BELT_INPUT
                    )

                    underground_next = False
                elif distance == 1:
                    grid.add_transportation(
                        cord=a_star_node.cord,
                        name=FactorioConst.TRANSPORT_BELT,
                        orientation=GraphToMatrix.get_orientation_in_opposite_direction(
                            GraphToMatrix.get_enumeration_to_orientation(last_node.orientation)
                        ),
                        from_cord=from_cord,
                        to_cord=to_cord
                    )
                else:
                    grid.add_transportation(
                        cord=a_star_node.cord,
                        name=FactorioConst.FAST_UNDERGROUND_BELT,
                        orientation=GraphToMatrix.get_orientation_in_opposite_direction(
                            GraphToMatrix.get_enumeration_to_orientation(last_node.orientation)
                        ),
                        from_cord=from_cord,
                        to_cord=to_cord,
                        underground_belt_type=FactorioConst.UNDERGROUND_BELT_OUTPUT
                    )

                    underground_next = True

            last_node = a_star_node
            a_star_node = next_node

        grid.transform_into_inserter(last_node.cord, from_cord, to_cord)

        if start_cord != last_node:
            grid.transform_into_inserter(start_cord, from_cord, to_cord) 

        #TODO: when we have path length 2 we can not use anything else than big inserter

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
    def get_a_star_visited_key(cord, orientation, streak, is_underground):
        max_tracked_streak = GraphToMatrix.A_STAR_STREAK_THRESHOLD + 5
        return (cord, orientation, min(streak, max_tracked_streak), is_underground)

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
        path_set = pset([])

        heap = [AStartNode(
            from_cord,
            0,
            GraphToMatrix.get_manhattan_metric(from_cord, to_cords)
                + GraphToMatrix.evaluate_borders(from_cord, from_cords),
            None,
            0,
            None,
            path_set = path_set,
            is_start = True) for from_cord in from_cords]

        heapq.heapify(heap)

        visited_matrix = VisitedMatrix()
        for entry in heap:
            #visited_matrix[(entry.cord, entry.orientation, entry.streak)] = 0
            visited_matrix[GraphToMatrix.get_a_star_visited_key(
                entry.cord,
                entry.orientation,
                entry.streak,
                entry.is_underground_belt_end()
            )] = 0

        active_node = None
        found = False

        while not found and len(heap) != 0 and len(visited_matrix) <= 1_000_000:
            a_star_node = heapq.heappop(heap)

            if is_in_successor(a_star_node.cord) and a_star_node.streak > GraphToMatrix.A_STAR_STREAK_THRESHOLD:
                active_node = a_star_node

                break

            # TODO: at this points we are looking for arbitrary shortest path, but if we want to enforce "esthetics" maybe
            #  makes sense for example to get values to the surrounding of factory and if we preferre it to be at the center
            #  we give the points more or less points
            for multiplier in range(1, Grid.UNDERGROUND_MOVE_LENGTH):
                if a_star_node.streak < GraphToMatrix.A_STAR_STREAK_THRESHOLD and multiplier > 1:
                    break

                for orientation, streak, new_cord in GraphToMatrix.get_moves(a_star_node, visited_matrix, multiplier=multiplier, return_enumeration=True):
                    if new_cord in a_star_node.path_set:
                        continue

                    if new_cord in grid and not is_in_successor(new_cord):
                        visited_matrix[new_cord] = -1
                    else:
                        node = AStartNode(
                            new_cord,
                            a_star_node.depth + multiplier,
                            a_star_node.depth + multiplier + GraphToMatrix.get_manhattan_metric(new_cord, to_cords) + GraphToMatrix.evaluate_borders(new_cord, to_cords),
                            orientation = orientation,
                            streak = streak,
                            predecessor = a_star_node,
                            path_set = a_star_node.path_set
                        )

                        heapq.heappush(
                            heap,
                            node
                        )

                        visited_matrix[GraphToMatrix.get_a_star_visited_key(
                            node.cord,
                            node.orientation,
                            node.streak,
                            node.is_underground_belt_end()
                        )] = a_star_node.depth + multiplier
                        #visited_matrix[(new_cord, orientation, streak)] = a_star_node.depth + multiplier

                        if GraphToMatrix.ENABLE_UNFINISH_BELTS:
                            active_node = node

        if len(visited_matrix) > 1_000_000 and not GraphToMatrix.ENABLE_UNFINISH_BELTS or active_node is None:
            raise Exception("Unable to find a path")

        return active_node, visited_matrix

    @staticmethod
    def evaluate_borders(cord, points):
        return 0

        NOT_CENTER_PENALTY = 100

        #TODO: for correct A* with penalties is necessary to add reopening

        if cord not in points:
            return NOT_CENTER_PENALTY

        cx, cy = (sum(x[0] for x in points) / len(points), sum(x[1] for x in points) / len(points))
        x, y = cord

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
    def get_moves(a_star_node: AStartNode, visited_matrix, multiplier = 1, was_visited = False, return_enumeration = False):
        """
        Iterator over the coordinates which can be achieved from the provided coordinate.

        :param a_star_node: Starting coordinate.
        :param visited_matrix: Matrix denoting if we achieved position and in how many steps.
        :param multiplier: How may points in the grid can se move across in one points.
        :param was_visited: Denotes whether we return position which were previously visited.
        :param return_enumeration: Denotes whether we return the number of the enum_orientation.
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

        for enum_orientation, move in enumerate(Grid.GRID_MOVES):
            new_cord = (a_star_node.cord[0] + multiplier * move[0], a_star_node.cord[1] + multiplier * move[1])

            streak = 0 if a_star_node.orientation != enum_orientation else a_star_node.streak + 1

            if (multiplier > 1 or a_star_node.same_direction_is_needed()) and enum_orientation != a_star_node.orientation:
                continue

            visited_key = GraphToMatrix.get_a_star_visited_key(
                new_cord,
                enum_orientation,
                streak,
                multiplier > 1
            )
            if ((was_visited and visited_key in visited_matrix)
                    or (not was_visited and visited_key not in visited_matrix)):
            #if ((was_visited and (new_cord, enum_orientation, streak) in visited_matrix)
            #        or (not was_visited and (new_cord, enum_orientation, streak) not in visited_matrix)):
                yield new_cord if not return_enumeration else (enum_orientation, streak, new_cord)


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

        for multiplier in range(1, Grid.UNDERGROUND_MOVE_LENGTH):
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

        if x[0] - y[0] != 0 and x[1] - y[1] != 0:
            raise ValueError(f"Vectors {x} and {y} are not achievable from each other with the use of basis vectors.")

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
