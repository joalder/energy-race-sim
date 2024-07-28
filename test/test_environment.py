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
