import logging
import math
from abc import ABC, abstractmethod
from enum import Enum
from typing import Self

from simulation.environment import Position

log = logging.getLogger(__name__)


class Tile(ABC):
    def __init__(self, origin: Position, width: float = 10):
        self.origin: Position = origin
        self.width: float = width

    @abstractmethod
    def get_destination(self) -> Position:
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

    def __str__(self):
        return f"Straight {self.origin} -> {self.length}m"


class Track:
    def __init__(self, name: str, tiles: list[Tile]):
        self.name = name
        self.tiles = tiles
        self.origin = tiles[0].origin

    def __str__(self):
        result = f"Track {self.name} \n\n"
        for tile in self.tiles:
            result += f"Tile {tile}\n"
        return result

class TrackDoesNotLoopException(Exception):
    def __init__(self, tiles: list[Tile]):
        super().__init__()
        self.tiles = tiles


class TrackIsEmptyException(Exception):
    pass


class TrackBuilder:

    def __init__(self, name: str, position: Position):
        self.name = name
        self.track_origin: Position = position
        self.current_end: Position = position
        self.tiles: list[Tile] = []

    def into(self, tile: Tile) -> Self:
        self.current_end = tile.get_destination()
        self.tiles.append(tile)
        return self

    def into_straight(self, length: float):
        return self.into(StraightTile(self.current_end, length))

    def into_corner(self, direction: Direction, angle: int, inner_radius: float):
        return self.into(CornerTile(self.current_end, angle, inner_radius, direction))

    def loop(self) -> Track:
        if not self.tiles:
            raise TrackIsEmptyException()
        if self.current_end != self.track_origin:
            raise TrackDoesNotLoopException(self.tiles)
        return Track(self.name, self.tiles)
