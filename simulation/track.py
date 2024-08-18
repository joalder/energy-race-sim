import logging
from dataclasses import dataclass
from typing import Self

from simulation.position import Position
from simulation.tile import Tile, Direction, CornerTile, StraightTile
from simulation.units import PROGRESS_PERCENTAGE_PRECISION, DISTANCE_PRECISION

log = logging.getLogger(__name__)


class TileNotPartOfTrackError(Exception):
    pass


class Track:
    def __init__(self, name: str, tiles: list[Tile]):
        self.name = name
        self.tiles = tiles
        self.origin = tiles[0].origin

    @property
    def starting_tile(self):
        return self.tiles[0]

    def __str__(self):
        result = f"Track {self.name} \n\n"
        for tile in self.tiles:
            result += f"Tile {tile}\n"
        return result

    def tile_after(self, tile):
        current_index = self.tiles.index(tile)

        if current_index == -1:
            raise TileNotPartOfTrackError()

        if current_index == len(self.tiles) - 1:
            return self.starting_tile

        return self.tiles[current_index + 1]

    def tile_before(self, tile):
        raise NotImplementedError()

    @property
    def total_length(self) -> float:
        total_length = 0
        for tile in self.tiles:
            total_length += tile.path_length()

        return round(total_length, DISTANCE_PRECISION)


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
        # Split any radius > 90 into multiple corners as current calculation only supports up to 90
        if angle > 90:
            return self.into_corner(direction, 90, inner_radius) \
                .into_corner(direction, angle - 90, inner_radius)
        return self.into(CornerTile(self.current_end, angle, inner_radius, direction))

    def loop(self) -> Track:
        if not self.tiles:
            raise TrackIsEmptyException()
        if self.current_end != self.track_origin:
            raise TrackDoesNotLoopException(self.tiles)
        return Track(self.name, self.tiles)


@dataclass
class SpeedLimitDistance:
    distance: float
    speed_limit: float


class TrackLocation:
    def __init__(self, track: Track, tile: Tile, progress: float):
        self.track = track
        self.tile = tile
        self.progress = progress

    def move(self, distance: float, passed_finish_line: bool = False) -> tuple[Self, bool]:
        """
        :param distance: to move in total
        :param passed_finish_line: if finish line has already been passed
        :return: tuple of new location / finish line has been passed
        """
        distance_left_on_tile = self.distance_left_on_tile

        if distance >= distance_left_on_tile:
            next_tile = self.track.tile_after(self.tile)
            new_distance = round(distance - distance_left_on_tile, DISTANCE_PRECISION)
            return TrackLocation(self.track, next_tile, 0.0) \
                .move(new_distance, passed_finish_line or next_tile == self.track.starting_tile)

        new_progress = round(100 - ((distance_left_on_tile - distance) / self.tile.path_length() * 100),
                             PROGRESS_PERCENTAGE_PRECISION)
        return TrackLocation(self.track, self.tile, new_progress), passed_finish_line

    def get_absolute_position(self) -> Position:
        return self.tile.get_absolute_position(self.progress)

    @property
    def distance_left_on_tile(self) -> float:
        return (100 - self.progress) / 100 * self.tile.path_length()

    def get_upcoming_max_speed_locations(self, lookahead_distance: float, tire_friction_coefficient: float,
                                         vehicle_height: float, vehicle_track_width: float,
                                         relative_looking_distance: float = 0.0) -> list[SpeedLimitDistance]:
        result = [SpeedLimitDistance(
            relative_looking_distance,
            self.tile.max_speed(tire_friction_coefficient, vehicle_height, vehicle_track_width)
        )]

        distance_left_on_tile = self.distance_left_on_tile
        if self.distance_left_on_tile <= lookahead_distance:
            next_tile = self.track.tile_after(self.tile)
            result += TrackLocation(self.track, next_tile, 0.0) \
                .get_upcoming_max_speed_locations(lookahead_distance - self.distance_left_on_tile,
                                                  tire_friction_coefficient, vehicle_height, vehicle_track_width,
                                                  distance_left_on_tile + relative_looking_distance)

        return result

    def __str__(self):
        return f"Tile: {self.tile} / Progress: {self.progress:.1f}%"

    def __eq__(self, other):
        if isinstance(other, TrackLocation):
            return self.__dict__ == other.__dict__

        return False
