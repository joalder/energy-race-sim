import math
from abc import ABC, abstractmethod
from enum import Enum

from simulation.position import Position
from simulation.units import DISTANCE_PRECISION, abs_angle


class Tile(ABC):
    def __init__(self, origin: Position, width: float = 10):
        self.origin: Position = origin
        self.width: float = width

    @abstractmethod
    def get_destination(self) -> Position:
        pass

    def get_defining_points(self) -> tuple[Position, Position, Position, Position]:
        """
        :return: the 4 defining points of the tile in the following order:
        origin left, origin right, destination left, destination right
        """
        destination = self.get_destination()
        return (
            self.origin,
            self.origin.translate(self.width, 90),
            destination,
            destination.translate(self.width, 90)
        )

    @abstractmethod
    def path_length(self) -> float:
        """
        :return: length of the "ideal" path on the tile
        """
        # TODO: eventually needs to include last/next tile
        pass

    @abstractmethod
    def get_absolute_position(self, progress):
        pass

    @abstractmethod
    def max_speed(self, tire_friction_coefficient: float, vehicle_height: float, vehicle_track_width: float) -> float:
        pass


class Direction(Enum):
    """
    Values represent clock wise (right) vs. anti-clockwise (left)
    """
    RIGHT = 1
    LEFT = -1


class CornerTile(Tile):
    def __init__(self, origin: Position, alpha: int, inner_radius: float, direction: Direction, width=10):
        super().__init__(origin, width)
        # TODO: add some validation for limits, e.g < 360 deg etc.
        self.alpha: int = alpha
        self.inner_radius: float = inner_radius
        self.direction: Direction = direction

    @property
    def alpha_rad(self):
        return math.radians(self.alpha)

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

    def get_radius_center(self) -> Position:
        radius = self.width + self.inner_radius if self.direction == Direction.RIGHT else self.inner_radius
        return self.origin.derive(orientation=abs_angle(self.origin.orientation + 90 * self.direction.value)) \
            .translate(radius)

    def path_length(self):
        # TODO: implement properly based on previous/next tile and some sort of racing line
        # 2r * pi / ratio of a full circle + 0% removed buffer for now
        return round(self.inner_radius * math.pi / (math.pi / math.radians(self.alpha)), DISTANCE_PRECISION)

    def max_speed(self, tire_friction_coefficient: float, vehicle_height: float, vehicle_track_width: float) -> float:
        """
        Help: https://engineering.icalculator.com/cornering-force-calculator.html
        or https://calculator.academy/maximum-cornering-speed-calculator/
        """
        # TODO: figure out a better radius, rather than inner_radius
        return math.sqrt(tire_friction_coefficient * 9.81 * self.inner_radius
                         / (1 - tire_friction_coefficient * vehicle_height / vehicle_track_width))

    def get_absolute_position(self, progress):
        return self.get_radius_center().derive(orientation=self.origin.orientation - 90 * self.direction.value) \
            .translate(self.inner_radius + self.width / 2, self.alpha * self.direction.value * (progress / 100))

    def __str__(self):
        return f"Corner {self.origin} -> {self.alpha}° {self.direction} radius {self.inner_radius}m"


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
        return round(self.length, DISTANCE_PRECISION)

    def max_speed(self, tire_friction_coefficient: float, vehicle_height: float, vehicle_track_width: float) -> float:
        return math.inf

    def get_absolute_position(self, progress) -> Position:
        return self.origin.translate(self.width / 2, 90).translate(self.length * (progress / 100))

    def __str__(self) -> str:
        return f"Straight {self.origin} -> {self.length}m"
