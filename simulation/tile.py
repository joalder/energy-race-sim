import math
from abc import ABC, abstractmethod
from enum import Enum

from simulation.position import Position
from simulation.units import DISTANCE_PRECISION


class Tile(ABC):
    def __init__(self, origin: Position, width: float = 10):
        self.origin: Position = origin
        self.width: float = width

    @abstractmethod
    def get_destination(self) -> Position:
        pass

    @abstractmethod
    def path_length(self) -> float:
        """
        :return: length of the "ideal" path on the tile
        """
        # TODO: eventually needs to include last/next tile
        pass


class Direction(Enum):
    """
    Values represent clock wise (right) vs. anti-clockwise (left)
    """
    RIGHT = 1
    LEFT = -1


class CornerTile(Tile):
    def __init__(self, origin, alpha: int, inner_radius: float, direction: Direction, width=10):
        super().__init__(origin, width)
        # TODO: add some validation for limits, e.g < 360 deg etc.
        self.alpha: int = alpha
        self.inner_radius: float = inner_radius
        self.direction: Direction = direction

    def get_destination(self) -> Position:
        # TODO: check if current approach works for corners >= 180deg

        if self.direction == Direction.RIGHT:
            radius = self.width + self.inner_radius
        else:
            radius = self.inner_radius

        relative_angle_to_destination = (90 - (180 - self.alpha) / 2) * self.direction.value
        angle_to_destination = abs_angle(self.origin.orientation + relative_angle_to_destination)

        hc = (radius ** 2 * math.sin(math.radians(self.alpha))) / radius

        distance_to_destination = hc * 1 / math.sin(math.radians(((180 - self.alpha) / 2)))
        angle_at_destination = abs_angle(self.origin.orientation + self.alpha * self.direction.value)

        return self.origin.derive(orientation=angle_to_destination) \
            .translate(distance_to_destination) \
            .derive(orientation=angle_at_destination)

    def path_length(self):
        # TODO: implement properly based on previous/next tile and some sort of racing line
        # 2r * pi / ratio of a full circle + 10% because of not hugging the inside all the time
        return round(1.1 * self.inner_radius * math.pi / (math.pi / math.radians(self.alpha)), DISTANCE_PRECISION)

    def __str__(self):
        return f"Corner {self.origin} -> {self.alpha}° {self.direction} radius {self.inner_radius}m"


def abs_angle(angle: float) -> float:
    return (angle + 360) % 360


class StraightTile(Tile):
    """
    Origin defines the corner on the left where the specific tile starts.
    Destination is the equivalent on the end of the tile.
    """

    def __init__(self, origin: Position, length: float, width: float = 10):
        super().__init__(origin, width)
        self.length = length

    def get_destination(self) -> Position:
        return self.origin.translate(self.length)

    def path_length(self) -> float:
        # TODO: implement properly based on previous/next tile and some sort of racing line
        return round(self.length * 1.05, DISTANCE_PRECISION)

    def __str__(self):
        return f"Straight {self.origin} -> {self.length}m"
