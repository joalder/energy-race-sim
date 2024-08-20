import pytest
from assertpy import assert_that

from simulation.position import Position
from simulation.track import TrackBuilder, TrackLocation
from simulation.tile import Direction


def test__simple_track():
    track = TrackBuilder("Simple Track", Position(0, 0, 0, 0)) \
        .into_straight(20) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(10) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(20) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(10) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .loop()

    print(track)


simple_track = TrackBuilder("Simple Track", Position(0, 0, 0, 0)) \
    .into_straight(20) \
    .into_corner(Direction.RIGHT, 90, 10) \
    .into_straight(10) \
    .into_corner(Direction.RIGHT, 90, 10) \
    .into_straight(20) \
    .into_corner(Direction.RIGHT, 90, 10) \
    .into_straight(10) \
    .into_corner(Direction.RIGHT, 90, 10) \
    .loop()
test_data_straight_move = [
    (TrackLocation(simple_track, simple_track.starting_tile, 0.0), 10,
     TrackLocation(simple_track, simple_track.starting_tile, 50), False),
    (TrackLocation(simple_track, simple_track.starting_tile, 0.0), 20,
     TrackLocation(simple_track, simple_track.tiles[1], 0), False),
    (TrackLocation(simple_track, simple_track.starting_tile, 0.0), simple_track.total_length,
     TrackLocation(simple_track, simple_track.starting_tile, 0.0), True),
]


@pytest.mark.parametrize("track_location,distance_to_move,track_location_expected,finish_line_passed_expected",
                         test_data_straight_move)
def test__track_location__move(track_location, distance_to_move, track_location_expected, finish_line_passed_expected):
    new_location, finish_line_passed = track_location.move(distance_to_move)

    assert_that(new_location).is_equal_to(track_location_expected)
    assert_that(finish_line_passed).is_equal_to(finish_line_passed_expected)
