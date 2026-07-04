from abc import ABC, abstractmethod
from enum import IntEnum
import prettytable

#TODO: maybe makes sense that the entries in the dictionary are not only string which denotes the type
# but also the size and roration (or at least rotation, if we can compute the size implicitly, but explicit
# size maybe makes more sense)

#TODO: maybe add mapping id to object
class Grid:
    """
    Represents the planar layout of the factory.
    """

    def __init__(self):
        self.id_counter = 0

        self.data : dict[tuple, GridEntry] = {} # TODO: maybe occupied whould be also for not only belts
        self.occupied = set()

    def set_occupied(self, cord: tuple, building_cord: tuple) -> None:
        """
        Sets the provided coordinates as occupied in the grid.

        :param cord: Coordinates in the grid.
        """

        self.occupied.add(cord)
        self.data[building_cord].add_surrounding(cord)

    def add_factory(self, cord: tuple, name: str, sur_cord) -> None:
        self.__setitem__(cord, GridEntry(self._get_movable_id(), name, entry_type=GridEntryTypes.Factory))

        for sur in sur_cord:
            self.set_occupied(sur, cord)

    def add_source(self, cord: tuple, name: str) -> None:
        self.__setitem__(cord, GridEntry(self._get_movable_id(), name, entry_type=GridEntryTypes.Source))

    def add_transportation(self, cord: tuple, name: str, orientation: int, from_cord: tuple, to_cord: tuple) -> None:
        self.__setitem__(
            cord,
            GridEntry(
                GridEntryTransportationId(self._find_movable_id(from_cord), self._find_movable_id(to_cord)),
                name,
                orientation,
                GridEntryTypes.Transportation
            )
        )

    def _get_movable_id(self) -> GridEntryId:
        self.id_counter += 1

        return GridEntryMovableId(self.id_counter)

    def _find_movable_id(self, cord: tuple) -> GridEntryId:
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

    def __iter__(self):
        """
        Iterator over the coordinates with elements in the grid.

        :return: Iterator over the coordinates with elements in the grid.
        """

        for key in self.data.keys():
            yield key

    def __str__(self):
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

    def get_x_cord(self):
        return map(lambda x: x[0], self.occupied.union(self.data.keys()))

    def get_y_cord(self):
        return map(lambda x: x[1], self.occupied.union(self.data.keys()))

    def get_area(self):
        dx = abs(max(self.get_x_cord()) - min(self.get_x_cord()))

        dy = abs(max(self.get_y_cord()) - min(self.get_y_cord()))

        return dx * dy

    def get_used_block(self):
        return len(self.occupied) + len(self.data)

    def get_factories(self):
        for grid_entry_cord in self.data.keys():
            if self.data[grid_entry_cord].is_movable():
                yield grid_entry_cord, self.data[grid_entry_cord]

    def _erase_building(self, grid_entry):
        for sur in grid_entry.surroundings:
            self.occupied.remove(sur)

    def _remove_belts(self, grid_entry) -> None:
        belts_cors = set()

        for entry_key in self.data.keys():
            if self.data[entry_key].is_connected_to(grid_entry.get_id()):
                belts_cors.add(entry_key)

        for cord in belts_cors:
            self.data.pop(cord)

    def _get_neighbors(self, grid_entry: GridEntry) -> list[tuple]:
        neighbors = set()
        is_to = {} # TODO: TEMPORARY USE OF INT USE ENUM OR SOMETHING ELSE

        for entry_key in self.data.keys():
            if self.data[entry_key].is_connected_to(grid_entry.get_id()):
                belt_id = self.data[entry_key].get_id_text().split("-") # TODO: maybe better

                if belt_id[0] == grid_entry.get_id_text():
                    neighbors.add(belt_id[1])
                    is_to[belt_id[1]] = True
                else:
                    neighbors.add(belt_id[0])
                    is_to[belt_id[0]] = False

                """
                for neighbor in belt_id:
                    if neighbor != grid_entry.get_id_text():
                        neighbors.add(neighbor)
                """

        neighbors_cord = []
        for entry_key in self.data.keys():
            if self.data[entry_key].get_id_text() in neighbors:
                neighbors_cord.append((entry_key, is_to[self.data[entry_key].get_id_text()]))

        return neighbors_cord

    def erase_factory(self, cord: tuple) -> list[tuple]:
        grid_entry = self.data[cord]

        neighbors = self._get_neighbors(grid_entry)

        self._remove_belts(grid_entry)
        self._erase_building(grid_entry)

        self.data.pop(cord)

        return neighbors


# TODO: We need some way how do distinguish belts, because at small factories, the do not overlap very much and
# we can distinguish them by the "topology" but when we have some intersection when we cannot 100% say which
# one is correct -> add ID to the factories and all belts etc. would have ID from-to according to factories

# Also we have 3 magor types -> factories, belts (other ways how to transport) and sources -> at this time
# we only distinguish factories and others so maybe it is good idea to add some enum for all three

class GridEntryTypes(IntEnum):
    Factory = 0
    Transportation = 1
    Source = 2

class GridEntryId(ABC):
    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def is_connected_to(self, to_id: GridEntryId) -> bool:
        pass

class GridEntryMovableId(GridEntryId):
    def __init__(self, entry_id: int):
        self.id = str(entry_id)

    def get_id(self) -> str:
        return self.id

    def is_connected_to(self, to_id: GridEntryId) -> bool:
        return False

class GridEntryTransportationId(GridEntryId):
    def __init__(self, from_id: GridEntryId, to_id: GridEntryId):
        self.from_id = from_id
        self.to_id = to_id

    def get_id(self) -> str:
        return self.from_id.get_id() + "-" + self.to_id.get_id()

    def is_connected_to(self, con_id: GridEntryId) -> bool:
        return con_id == self.from_id or con_id == self.to_id

class GridEntry:
    """
    Represents an elements in the grid.
    """

    def __init__(
        self,
        entry_id: GridEntryId,
        name: str,
        orientation: int = 0,
        entry_type: GridEntryTypes = GridEntryTypes.Transportation
    ):
        self.id = entry_id
        self.name = name
        self.orientation = orientation
        self.entry_type = entry_type
        self.surroundings = set()

    def add_surrounding(self, cord: tuple):
        self.surroundings.add(cord)

    def is_factory(self):
        return self.entry_type == GridEntryTypes.Factory

    def is_source(self):
        return self.entry_type == GridEntryTypes.Source

    def is_movable(self):
        return self.is_factory() or self.is_source()

    def get_id(self):
        return self.id

    def get_id_text(self):
        return self.id.get_id()

    def is_connected_to(self, con_id: GridEntryId) -> bool:
        return self.id.is_connected_to(con_id)

    def get_detailed_name(self):
        if self.is_factory():
            return self.name + "-factory"
        elif self.is_source():
            return self.name + "-source"
        else:
            return self.name

    def __str__(self):
        return self.get_id_text()
        return self.name[:2]
