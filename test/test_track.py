import pytest
from assertpy import assert_that

from simulation.environment import Position
from simulation.track import StraightTile

testdata = [
    (Position(0, 0, 0, 0), 20, Position(20, 0, 0, 0)),
    (Position(0, 0, 0, 30), 20, Position(17.321, 10, 0, 30)),
    (Position(0, 0, 0, 45), 20, Position(14.142, 14.142, 0, 45)),
    (Position(0, 0, 0, 90), 20, Position(0, 20, 0, 90)),
    (Position(0, 0, 0, 180), 20, Position(-20, 0, 0, 180)),
    (Position(0, 0, 0, 225), 20, Position(-14.142, -14.142, 0, 225)),
    (Position(0, 0, 0, 270), 20, Position(0, -20, 0, 270)),
    (Position(0, 0, 0, 315), 20, Position(14.142, -14.142, 0, 315)),
]


@pytest.mark.parametrize("origin,length,destination_expected", testdata)
def test__straight_line(origin, length, destination_expected):
    tile = StraightTile(origin, 20)

    destination = tile.get_destination()

    assert_that(destination).is_equal_to(destination_expected)
