import itertools
from collections.abc import Iterator
import prettytable
from collections import deque

from .grid_entry import *
from .util.factorio_const import FactorioConst


#TODO: maybe add mapping id to object
class Grid:
    """
    Represents the planar layout of the factory.
    """

    GRID_MOVES = [(0, 1), (-1, 0), (0, -1), (1, 0)]

    # In Factorio the orientation is
    #  Up: 0
    #  Right: 4
    #  Down: 8
    #  Left: 12

    # When we compute the path between assemblers we go against the orientation.
    # Therefore, the move array is in this strange order.

    # This is the number of tiles red fast underground belt can travel
    UNDERGROUND_MOVE_LENGTH = 6

    def __init__(self) -> None:
        """
        Creates an empty grid representation of the factory.
        """

        self.id_counter = 0

        self.data : dict[tuple, GridEntry] = {}
        self.occupied = set()

    def set_occupied(self, cord: tuple, building_cord: tuple) -> None:
        """
        Sets the provided coordinates as occupied in the grid.

        :param cord: Coordinates in the grid.
        :param building_cord: Coordinates of the building which occupies the provided coordinates.
        """

        self.occupied.add(cord)
        self.data[building_cord].add_surrounding(cord)

    def add_factory(self, cord: tuple, name: str, sur_cord: list[tuple]) -> None:
        """
        Adds a factory into the grid and marks its surrounding coordinates as occupied.

        :param cord: Coordinates where the factory will be placed.
        :param name: Name of the factory entry.
        :param sur_cord: Coordinates occupied by the factory around the main coordinate.
        """

        self.try_place(cord, name, GridEntryTypes.Factory)

        self.__setitem__(cord, GridEntry(self._get_movable_id(), name, entry_type=GridEntryTypes.Factory))

        for sur in sur_cord:
            self.try_place(sur, name, GridEntryTypes.Factory)

            self.set_occupied(sur, cord)

    def add_source(self, cord: tuple, name: str) -> None:
        """
        Adds a source into the grid at the provided coordinates.

        :param cord: Coordinates where the source will be placed.
        :param name: Name of the source entry.
        """

        self.try_place(cord, name, GridEntryTypes.Source)

        self.__setitem__(cord, GridEntry(self._get_movable_id(), name, entry_type=GridEntryTypes.Source))

    def add_transportation(
        self,
        cord: tuple,
        name: str,
        orientation: int,
        from_cord: tuple,
        to_cord: tuple,
        underground_belt_type: str | None = None
    ) -> None:
        """
        Adds a transportation element connecting two movable grid entries.

        :param cord: Coordinates where the transportation element will be placed.
        :param name: Name of the transportation element.
        :param orientation: Orientation of the transportation element.
        :param from_cord: Coordinates of the source grid entry.
        :param to_cord: Coordinates of the destination grid entry.
        """

        self.try_place(cord, name, GridEntryTypes.Transportation)

        self.__setitem__(
            cord,
            GridEntry(
                GridEntryTransportationId(self._find_movable_id(from_cord), self._find_movable_id(to_cord)),
                name,
                orientation,
                GridEntryTypes.Transportation,
                underground_belt_type
            )
        )

    def try_place(self, cord, name, grid_type):
        if cord in self:
            raise Exception(f"Building {name} ({grid_type.name}) at {cord} cannot be placed because if already occupies by {self.data[cord].name if cord in self.data else "factory part"}.")

    def try_transportation(self, cord: tuple, from_cord: tuple, to_cord: tuple):
        entry_id = GridEntryTransportationId.create_belt_id(
            self.data[from_cord].get_id_text(),
            self.data[to_cord].get_id_text()
        )

        if cord in self.occupied or (cord in self.data and (self.data[cord].entry_type != GridEntryTypes.Transportation or self.data[cord].get_id_text() != entry_id)):

            raise Exception(f"Inserter cannot be placed at {cord} instead of factory or source.")

    def transform_into_inserter(
        self,
        cord: tuple,
        from_cord: tuple,
        to_cord: tuple
    ) -> None:
        """
        Changes a transportation element at the provided coordinates into an inserter.

        :param cord: Coordinates of the transportation element.
        """

        self.try_transportation(cord, from_cord, to_cord)

        self.data[cord].name = FactorioConst.INSERTER
        self.data[cord].orientation = (self.data[cord].orientation + 8) % 16

    def _get_movable_id(self) -> GridEntryId:
        """
        Creates a new identifier for a movable grid entry.

        :return: New identifier for a movable grid entry.
        """

        self.id_counter += 1

        return GridEntryMovableId(self.id_counter)

    def _find_movable_id(self, cord: tuple) -> GridEntryId:
        """
        Returns the identifier of a movable grid entry at the provided coordinates.

        :param cord: Coordinates of the movable grid entry.
        :return: Identifier of the movable grid entry.
        """

        return self.data[cord].id

    def __setitem__(self, key: tuple, value: GridEntry) -> None:
        """
        Adds elements into grid at the provided coordinates.

        :param key: Coordinates where will be the elements placed.
        :param value: Elements which will be placed into grid.
        """

        self.data[key] = value

    def __getitem__(self, key: tuple) -> GridEntry:
        """
        Returns elements laying at the provided coordinates.

        :param key: Coordinates in the grid.
        :return: Elements laying at the provided coordinates.
        """

        return self.data[key]

    def __contains__(self, cord: tuple) -> bool:
        """
        Returns whether in the grid at the provided coordinates is some element
        of if the coordinate is occupied in general.

        :param cord: Coordinate in the grid.
        :return: Whether in the grid at the provided coordinates is some element
        or if the coordinate is occupied in general.
        """

        return cord in self.data or cord in self.occupied

    def __iter__(self) -> Iterator[tuple]:
        """
        Iterator over the coordinates with elements in the grid.

        :return: Iterator over the coordinates with elements in the grid.
        """

        for key in self.data.keys():
            yield key

    def __len__(self):
        return len(self.occupied) + len(self.data)

    def __str__(self) -> str:
        """
        Returns a table representation of the occupied part of the grid.

        :return: Table representation of the occupied part of the grid.
        """

        min_x = min(self.get_x_cord())
        min_y = min(self.get_y_cord())

        max_x = max(self.get_x_cord())
        max_y = max(self.get_y_cord())

        header = ["#"]
        for x in range(min_x, max_x + 1):
            header.append(str(x))

        table = prettytable.PrettyTable(header)

        for y in range(min_y, max_y + 1):
            row = [str(y)]
            for x in range(min_x, max_x + 1):
                if (x, y) in self.occupied:
                    row.append("B")
                elif (x,y) in self.data.keys():
                    #row.append("F")
                    row.append(str(self.data[(x, y)]))
                else:
                    row.append("_")

            table.add_row(row)

        return str(table)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Grid):
            return False

        return self.data == other.data and self.occupied == other.occupied

    def get_x_cord(self) -> Iterator[int]:
        """
        Returns iterator over all used x coordinates in the grid.

        :return: Iterator over all used x coordinates in the grid.
        """

        return map(lambda x: x[0], self.occupied.union(self.data.keys()))

    def get_y_cord(self) -> Iterator[int]:
        """
        Returns iterator over all used y coordinates in the grid.

        :return: Iterator over all used y coordinates in the grid.
        """

        return map(lambda x: x[1], self.occupied.union(self.data.keys()))

    def get_with(self):
        return abs(max(self.get_x_cord()) - min(self.get_x_cord())) + 1

    def get_height(self):
        return abs(max(self.get_y_cord()) - min(self.get_y_cord())) + 1

    def get_area(self) -> int:
        """
        Returns the area of the rectangle covering all used coordinates.

        :return: Area of the rectangle covering all used coordinates.
        """

        return self.get_with() * self.get_height()

    def get_used_block(self) -> int:
        """
        Returns number of coordinates used by elements and occupied surroundings.

        :return: Number of coordinates used by elements and occupied surroundings.
        """

        #return len(self.occupied) + len(self.data)

        n = len(self.occupied)

        for entry_key in self.data.keys():
            if self.data[entry_key].name == FactorioConst.FAST_UNDERGROUND_BELT:
                n += 6
            else:
                n += 1

        return n

    def _get_center_cord(self) -> tuple[float, float]:
        x, y = 0, 0

        for dx, dy in itertools.chain(self.occupied, self.data.keys()):
            x += dx
            y += dy

        n = len(self)

        return x / n, y / n

    def get_distances_from_center(self) -> int:
        cx, cy = self._get_center_cord()

        d = 0

        for dx, dy in itertools.chain(self.occupied, self.data.keys()):
            d += abs(cx - dx)
            d += abs(cy - dy)

        return d

    def get_factories(self) -> Iterator[tuple[tuple, GridEntry]]:
        """
        Iterates over movable grid entries and their coordinates.

        :return: Iterator over pairs of coordinates and movable grid entries.
        """

        for grid_entry_cord in self.data.keys():
            if self.data[grid_entry_cord].is_movable():
                yield grid_entry_cord, self.data[grid_entry_cord]

    def get_number_of_factories(self) -> int:
        n = 0

        for grid_entry_cord in self.data.keys():
            if self.data[grid_entry_cord].is_movable():
                n += 1

        return n

    def _erase_building(self, grid_entry: GridEntry) -> None:
        """
        Removes occupied surroundings of the provided building from the grid.

        :param grid_entry: Building whose surroundings will be removed.
        """

        for sur in grid_entry.surroundings:
            self.occupied.remove(sur)

    def _remove_belts(self, grid_entry: GridEntry) -> None:
        """
        Removes all transportation elements connected to the provided grid entry.

        :param grid_entry: Grid entry whose connected transportation elements will be removed.
        """

        belts_cors = set()

        for entry_key in self.data.keys():
            if self.data[entry_key].is_connected_to(grid_entry.get_id()):
                belts_cors.add(entry_key)

        for cord in belts_cors:
            self.data.pop(cord)

    def _get_neighbors(self, grid_entry: GridEntry) -> list[tuple]:
        """
        Returns movable neighbors connected to the provided grid entry.

        :param grid_entry: Grid entry whose neighbors will be found.
        :return: List of connected neighbor coordinates and connection directions.
        """

        neighbors = set()
        is_from_removed_to_neighbor = {}

        for entry_key in self.data.keys():
            if self.data[entry_key].is_connected_to(grid_entry.get_id()):
                belt_id = self.data[entry_key].get_id_text().split("-")

                if len(belt_id) != 2:
                    raise ValueError(f"Identifier of belts {self.data[entry_key].get_id_text()} is not valid.")

                if belt_id[0] == grid_entry.get_id_text():
                    neighbors.add(belt_id[1])
                    is_from_removed_to_neighbor[belt_id[1]] = True
                elif belt_id[1] == grid_entry.get_id_text():
                    neighbors.add(belt_id[0])
                    is_from_removed_to_neighbor[belt_id[0]] = False
                else:
                    raise ValueError(f"Identifier of belts {self.data[entry_key].get_id_text()} does not match grid entry {grid_entry.get_id_text()}")

        neighbors_cord = []
        for entry_key in self.data.keys():
            if self.data[entry_key].get_id_text() in neighbors:
                neighbors_cord.append(
                    (entry_key, is_from_removed_to_neighbor[self.data[entry_key].get_id_text()])
                )

        return neighbors_cord

    def erase_factory(self, cord: tuple) -> list[tuple]:
        """
        Removes a movable grid entry and its connected transportation elements.

        :param cord: Coordinates of the movable grid entry which will be removed.
        :return: List of connected neighbor coordinates and connection directions.
        """

        grid_entry = self.data[cord]

        neighbors = self._get_neighbors(grid_entry)

        self._remove_belts(grid_entry)
        self._erase_building(grid_entry)

        self.data.pop(cord)

        return neighbors

    def is_belt_with_id(self, cord: tuple, id: str) -> bool:
        """
        Returns whether a transportation element at the provided coordinates has the provided id.

        :param cord: Coordinates checked in the grid.
        :param id: Identifier of the transportation element.
        :return: Whether a transportation element at the provided coordinates has the provided id.
        """

        if not cord in self.data:
            return False

        return self.data[cord].get_id_text() == id

    @staticmethod
    def orientation_to_vector(orientation):
        return Grid.GRID_MOVES[orientation // 4]

    @staticmethod
    def is_opposite_orientation_enum(orientation_a: int, orientation_b: int) -> bool:
        return (orientation_a + 8) % 16 == orientation_b

    def _is_pointing_to_center(self, cord):
        x, y = cord

        fdx, fdy = Grid.orientation_to_vector(self.data[cord].orientation)
        rdx, rdy = self.orientation_to_vector((self.data[cord].orientation + 4) % 16)
        ldx, ldy = Grid.orientation_to_vector((self.data[cord].orientation - 4) % 16)

        borders = [(x + fdx, y + fdy), (x + rdx + fdx, y + rdy + fdy), (x + ldx + fdx, y + ldy + fdy)]

        return all(map(lambda b: self.__contains__(b), borders))

    def get_number_of_pointing_to_center(self) -> int:
        n = 0

        for entry_key in self.data.keys():
            if self.data[entry_key].is_transportation() and self._is_pointing_to_center(entry_key):
                n += 1

        return n

    def exists_path(
        self,
        a: list[tuple],
        b: list[tuple],
        id: str
    ) -> bool:
        """
        Returns whether a path with the provided transportation id exists between two coordinate sets.

        :param a: Starting coordinates of the path.
        :param b: Ending coordinates of the path.
        :param id: Identifier of the transportation elements forming the path.
        :return: Whether a path with the provided transportation id exists.
        """

        queue = deque((x, y, 0) for x, y in a)
        visited = set()

        while len(queue) > 0:
            if len(queue) >= 100_000:
                raise Exception("Cannot find connection")

            x,y,d = queue.popleft()

            found = False
            multiplier = 0
            while not found and multiplier < Grid.UNDERGROUND_MOVE_LENGTH:
                multiplier += 1

                for dx, dy in [(0,1), (-1, 0), (1,0), (0, -1)]:
                    nx, ny = x + multiplier * dx, y + multiplier * dy

                    if (nx, ny) in b and d > 0:
                        return True

                    if self.__contains__((nx, ny)) and self.is_belt_with_id((nx, ny), id) and (nx, ny) not in visited:
                        queue.append((nx, ny, d + 1))
                        visited.add((nx, ny))
                        found = True
        return False
