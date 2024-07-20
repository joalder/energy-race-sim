import math
from abc import ABC, abstractmethod
from enum import Enum

from simulation.environment import Position

SIN_90_DEGREES = math.sin(math.radians(90))


class Tile(ABC):
    def __init__(self, origin: Position, width: int = 10):
        self.origin: Position = origin
        self.width: int = width

    @abstractmethod
    def get_destination(self) -> Position:
        pass


class Direction(Enum):
    LEFT = 'l'
    RIGHT = 'r'


class CornerTile(Tile):
    def __init__(self, origin, alpha: int, inner_radius: int, direction: Direction, width=10):
        super().__init__(origin, width)
        self.alpha: int = alpha
        self.inner_radius: int = inner_radius
        self.direction: Direction = direction

    def get_destination(self) -> Position:
        raise NotImplementedError()


class StraightTile(Tile):
    """
    Origin defines the corner on the left where the specific tile starts.
    Destination is the equivalent on the end of the tile.
    """

    def __init__(self, origin: Position, length: int, width: int = 10):
        super().__init__(origin, width)
        self.length = length

    def get_destination(self) -> Position:
        # TODO: is C always 90deg? Just remove it as it is 1

        precision = 3
        new_x = round(self.length * math.sin(math.radians(180 - 90 - self.origin.orientation)) / SIN_90_DEGREES,
                      precision)
        new_y = round(self.length * math.sin(self.origin.orientation_rad) / SIN_90_DEGREES, precision)
        return self.origin.derive(x=new_x, y=new_y)

    def __str__(self):
        return f"Straight {self.origin} -> {self.length}m -> {self.get_destination()}"


class Track:
    pass
