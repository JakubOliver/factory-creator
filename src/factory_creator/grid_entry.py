from __future__ import annotations

from abc import ABC, abstractmethod
from enum import IntEnum


class GridEntryTypes(IntEnum):
    Factory = 0
    Transportation = 1
    Source = 2


class GridEntryId(ABC):
    @abstractmethod
    def get_id(self) -> str:
        """
        Returns textual representation of the grid entry identifier.

        :return: Textual representation of the grid entry identifier.
        """

        pass

    @abstractmethod
    def is_connected_to(self, to_id: GridEntryId) -> bool:
        """
        Returns whether this identifier is connected to the provided identifier.

        :param to_id: Identifier checked for connection.
        :return: Whether this identifier is connected to the provided identifier.
        """

        pass


class GridEntryMovableId(GridEntryId):
    def __init__(self, entry_id: int) -> None:
        """
        Creates an identifier for a movable grid entry.

        :param entry_id: Numeric identifier of the movable grid entry.
        """

        self.id = str(entry_id)

    def get_id(self) -> str:
        """
        Returns textual representation of the movable grid entry identifier.

        :return: Textual representation of the movable grid entry identifier.
        """

        return self.id

    def is_connected_to(self, to_id: GridEntryId) -> bool:
        """
        Returns whether this movable identifier is connected to the provided identifier.

        :param to_id: Identifier checked for connection.
        :return: Always false because movable identifiers do not connect directly.
        """

        return False


class GridEntryTransportationId(GridEntryId):
    def __init__(self, from_id: GridEntryId, to_id: GridEntryId) -> None:
        """
        Creates an identifier for a transportation connection.

        :param from_id: Identifier of the source grid entry.
        :param to_id: Identifier of the destination grid entry.
        """

        self.from_id = from_id
        self.to_id = to_id

    def get_id(self) -> str:
        """
        Returns textual representation of the transportation identifier.

        :return: Textual representation of the transportation identifier.
        """

        return GridEntryTransportationId.create_belt_id(
            self.from_id.get_id(),
            self.to_id.get_id()
        )

    def is_connected_to(self, con_id: GridEntryId) -> bool:
        """
        Returns whether the transportation identifier is connected to the provided identifier.

        :param con_id: Identifier checked for connection.
        :return: Whether the transportation identifier is connected to the provided identifier.
        """

        return con_id == self.from_id or con_id == self.to_id

    @staticmethod
    def create_belt_id(from_id: str, to_id: str) -> str:
        """
        Creates textual identifier for a transportation connection.

        :param from_id: Textual identifier of the source grid entry.
        :param to_id: Textual identifier of the destination grid entry.
        :return: Textual identifier for a transportation connection.
        """

        return from_id + "-" + to_id


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
    ) -> None:
        """
        Creates an element stored in the grid.

        :param entry_id: Identifier of the grid entry.
        :param name: Name of the grid entry.
        :param orientation: Orientation of the grid entry.
        :param entry_type: Type of the grid entry.
        """

        self.id = entry_id
        self.name = name
        self.orientation = orientation
        self.entry_type = entry_type
        self.surroundings = set()

    def add_surrounding(self, cord: tuple) -> None:
        """
        Adds occupied surrounding coordinates to the grid entry.

        :param cord: Occupied surrounding coordinates.
        """

        self.surroundings.add(cord)

    def is_factory(self) -> bool:
        """
        Returns whether the grid entry represents a factory.

        :return: Whether the grid entry represents a factory.
        """

        return self.entry_type == GridEntryTypes.Factory

    def is_source(self) -> bool:
        """
        Returns whether the grid entry represents a source.

        :return: Whether the grid entry represents a source.
        """

        return self.entry_type == GridEntryTypes.Source

    def is_transportation(self) -> bool:
        return self.entry_type == GridEntryTypes.Transportation

    def is_movable(self) -> bool:
        """
        Returns whether the grid entry can be moved by the evolution process.

        :return: Whether the grid entry can be moved by the evolution process.
        """

        return self.is_factory() or self.is_source()

    def get_id(self) -> GridEntryId:
        """
        Returns identifier of the grid entry.

        :return: Identifier of the grid entry.
        """

        return self.id

    def get_id_text(self) -> str:
        """
        Returns textual identifier of the grid entry.

        :return: Textual identifier of the grid entry.
        """

        return self.id.get_id()

    def is_connected_to(self, con_id: GridEntryId) -> bool:
        """
        Returns whether the grid entry is connected to the provided identifier.

        :param con_id: Identifier checked for connection.
        :return: Whether the grid entry is connected to the provided identifier.
        """

        return self.id.is_connected_to(con_id)

    def get_detailed_name(self) -> str:
        """
        Returns name of the grid entry extended by its type when applicable.

        :return: Name of the grid entry extended by its type when applicable.
        """

        if self.is_factory():
            return self.name + "-factory"
        elif self.is_source():
            return self.name + "-source"
        else:
            return self.name

    def __str__(self) -> str:
        """
        Returns textual representation of the grid entry.

        :return: Textual representation of the grid entry.
        """

        return self.get_id_text()
        return self.name[:2]

    @staticmethod
    def extract_item_name_from_source(name: str) -> str:
        return name.split("_source")[0]
