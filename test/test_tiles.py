import pytest
from assertpy import assert_that

from simulation.position import Position
from simulation.tile import Direction, CornerTile, StraightTile

POSITION_0_0_0_0 = Position(0, 0, 0, 0)

test_data_straight = [
    (POSITION_0_0_0_0, 20, Position(20, 0, 0, 0)),
    (Position(0, 0, 0, 30), 20, Position(17.321, 10, 0, 30)),
    (Position(0, 0, 0, 45), 20, Position(14.142, 14.142, 0, 45)),
    (Position(0, 0, 0, 90), 20, Position(0, 20, 0, 90)),
    (Position(0, 0, 0, 180), 20, Position(-20, 0, 0, 180)),
    (Position(0, 0, 0, 225), 20, Position(-14.142, -14.142, 0, 225)),
    (Position(0, 0, 0, 270), 20, Position(0, -20, 0, 270)),
    (Position(0, 0, 0, 315), 20, Position(14.142, -14.142, 0, 315)),
]


@pytest.mark.parametrize("origin,length,destination_expected", test_data_straight)
def test__straight_line(origin, length, destination_expected):
    tile = StraightTile(origin, 20)

    destination = tile.get_destination()

    assert_that(destination).is_equal_to(destination_expected)


test_data_straight_points = [
    (POSITION_0_0_0_0, 20, Position(0, 0, 0, 0), Position(0, 10, 0, 0), Position(20, 0, 0, 0), Position(20, 10, 0, 0)),
    (Position(15, 15, 0, 0), 20, Position(15, 15, 0, 0), Position(15, 25, 0, 0), Position(35, 15, 0, 0),
     Position(35, 25, 0, 0)),
    (Position(10, 10, 0, 180), 20, Position(10, 10, 0, 180), Position(10, 0, 0, 180), Position(-10, 10, 0, 180),
     Position(-10, 0, 0, 180)),
    (Position(10, 10, 0, 90), 20, Position(10, 10, 0, 90), Position(0, 10, 0, 90), Position(10, 30, 0, 90),
     Position(0, 30, 0, 90))
]


@pytest.mark.parametrize("origin,length,origin_left, origin_right, destination_left, destination_right",
                         test_data_straight_points)
def test__straight_line__defining_points(origin, length, origin_left, origin_right, destination_left,
                                         destination_right):
    tile = StraightTile(origin, length)

    defining_points = tile.get_defining_points()

    assert_that(defining_points).contains(origin_left, origin_right, destination_left, destination_right)


test_data_straight_off_center = [
    (Position(7, 7, 0, 30), 20, Position(24.321, 17, 0, 30)),
    (Position(-7, -7, 0, 45), 20, Position(7.142, 7.142, 0, 45)),
    (Position(7, -7, 0, 90), 20, Position(7, 13, 0, 90)),
    (Position(-7, 7, 0, 180), 20, Position(-27, 7, 0, 180)),
    (Position(14.142, 14.142, 0, 225), 20, Position(0, 0, 0, 225)),
    (Position(0, 20, 0, 270), 20, Position(0, 0, 0, 270)),
    (Position(-42, 42, 0, 315), 20, Position(-27.858, 27.858, 0, 315)),
]


@pytest.mark.parametrize("origin,length,destination_expected", test_data_straight_off_center)
def test__straight_line_off_center(origin, length, destination_expected):
    tile = StraightTile(origin, 20)

    destination = tile.get_destination()

    assert_that(destination).is_equal_to(destination_expected)


test_data_corners = [
    (POSITION_0_0_0_0, 90, 10, Direction.RIGHT, Position(20, 20, 0, 90)),
    (POSITION_0_0_0_0, 45, 10, Direction.RIGHT, Position(14.142, 5.858, 0, 45)),
    # TODO: this is currently not supported, validate or auto split
    # (POSITION_0_0_0_0, 180, 10, Direction.RIGHT, Position(0, 40, 0, 180)),
    (POSITION_0_0_0_0, 90, 10, Direction.LEFT, Position(10, -10, 0, 270)),
    (POSITION_0_0_0_0, 45, 10, Direction.LEFT, Position(7.071, -2.929, 0, 315)),
]


@pytest.mark.parametrize("origin,alpha,inner_radius,direction,destination_expected", test_data_corners)
def test__corner(origin, alpha: int, inner_radius: int, direction: Direction, destination_expected):
    tile = CornerTile(origin, alpha, inner_radius, direction)

    destination = tile.get_destination()

    assert_that(destination).is_equal_to(destination_expected)


def test__corner__double_to_180():
    expected_final_position = Position(0, 40, 0, 180)
    first_tile = CornerTile(POSITION_0_0_0_0, 90, 10, Direction.RIGHT)
    second_tile = CornerTile(first_tile.get_destination(), 90, 10, Direction.RIGHT)

    final_destination = second_tile.get_destination()

    assert_that(final_destination).is_equal_to(expected_final_position)


def test__corner__full_circle_right():
    expected_final_position = Position(0, 0, 0, 0)
    first_tile = CornerTile(POSITION_0_0_0_0, 90, 10, Direction.RIGHT)
    second_tile = CornerTile(first_tile.get_destination(), 90, 10, Direction.RIGHT)
    third_tile = CornerTile(second_tile.get_destination(), 90, 10, Direction.RIGHT)
    fourth_tile = CornerTile(third_tile.get_destination(), 90, 10, Direction.RIGHT)

    final_destination = fourth_tile.get_destination()

    assert_that(final_destination).is_equal_to(expected_final_position)


def test__corner__full_circle_left():
    expected_final_position = Position(0, 0, 0, 0)
    first_tile = CornerTile(POSITION_0_0_0_0, 90, 10, Direction.LEFT)
    second_tile = CornerTile(first_tile.get_destination(), 90, 10, Direction.LEFT)
    third_tile = CornerTile(second_tile.get_destination(), 90, 10, Direction.LEFT)
    fourth_tile = CornerTile(third_tile.get_destination(), 90, 10, Direction.LEFT)

    final_destination = fourth_tile.get_destination()

    assert_that(final_destination).is_equal_to(expected_final_position)


test_data_corners_path_length = [
    (POSITION_0_0_0_0, 90, 10, Direction.RIGHT, 17.279),  # 15.708 + 10%
    (POSITION_0_0_0_0, 45, 10, Direction.RIGHT, 8.639),  # 7.854 + 10%
    (POSITION_0_0_0_0, 90, 10, Direction.LEFT, 17.279),
    (POSITION_0_0_0_0, 45, 10, Direction.LEFT, 8.639),
]


@pytest.mark.parametrize("origin,alpha,inner_radius,direction,path_length_expected", test_data_corners_path_length)
def test__corner__path_length(origin, alpha: int, inner_radius: int, direction: Direction, path_length_expected: float):
    tile = CornerTile(origin, alpha, inner_radius, direction)

    assert_that(tile.path_length()).is_equal_to(path_length_expected)


test_data_straight_path_length = [
    (POSITION_0_0_0_0, 10, 10),  # 10 + 0% for now
    (POSITION_0_0_0_0, 20, 20),  # 20 + 0% for now
]


@pytest.mark.parametrize("origin,length,path_length_expected", test_data_straight_path_length)
def test__corner__path_length(origin, length: float, path_length_expected: float):
    tile = StraightTile(origin, length)

    assert_that(tile.path_length()).is_equal_to(path_length_expected)
