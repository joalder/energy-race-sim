from simulation.environment import Position
from simulation.track import TrackBuilder, Direction


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
