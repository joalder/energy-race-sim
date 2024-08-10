from assertpy import assert_that

from simulation.position import Position


def test__position__equality__same_values_different_instance():
    position_a = Position(1, 2, 3, 4)
    position_b = Position(1, 2, 3, 4)

    assert_that(position_a).is_equal_to(position_b)


def test__position__equality__same_instance():
    position_a = Position(1, 2, 3, 4)

    assert_that(position_a).is_equal_to(position_a)


def test__position__equality__all_values_different():
    position_a = Position(1, 2, 3, 4)
    position_b = Position(10, 20, 30, 40)

    assert_that(position_a).is_not_equal_to(position_b)


def test__position__equality__different_x():
    position_a = Position(1, 2, 3, 4)
    position_b = Position(10, 2, 3, 4)

    assert_that(position_a).is_not_equal_to(position_b)


def test__position__equality__different_y():
    position_a = Position(1, 2, 3, 4)
    position_b = Position(1, 20, 3, 4)

    assert_that(position_a).is_not_equal_to(position_b)


def test__position__equality__different_z():
    position_a = Position(1, 2, 3, 4)
    position_b = Position(1, 2, 30, 4)

    assert_that(position_a).is_not_equal_to(position_b)


def test__position__equality__different_orientation():
    position_a = Position(1, 2, 3, 4)
    position_b = Position(1, 2, 3, 40)

    assert_that(position_a).is_not_equal_to(position_b)


def test__position__translate__distance_only():
    position = Position(0, 0, 0, 0)

    new_position = position.translate(20)

    assert_that(new_position).is_equal_to(Position(20, 0, 0, 0))


def test__position__translate_initial_angle_180():
    position = Position(0, 0, 0, 180)

    new_position = position.translate(20)

    assert_that(new_position).is_equal_to(Position(-20, 0, 0, 180))


def test__position__translate__angle_90():
    position = Position(10, 10, 0, 0)

    new_position = position.translate(20, 90)

    assert_that(new_position).is_equal_to(Position(10, 30, 0, 0))


def test__position__translate__angle_180():
    position = Position(10, 10, 0, 0)

    new_position = position.translate(20, 180)

    assert_that(new_position).is_equal_to(Position(-10, 10, 0, 0))


def test__position__translate__angle_270():
    position = Position(10, 10, 0, 0)

    new_position = position.translate(20, 270)

    assert_that(new_position).is_equal_to(Position(10, -10, 0, 0))


def test__position__translate__simple__initial_angle_180_angle_180():
    position = Position(0, 0, 0, 180)

    new_position = position.translate(20, 180)

    assert_that(new_position).is_equal_to(Position(20, 0, 0, 180))


def test__position__translate__simple__initial_angle_270_angle_180():
    position = Position(0, 0, 0, 270)

    new_position = position.translate(20, 180)

    assert_that(new_position).is_equal_to(Position(0, 20, 0, 270))
