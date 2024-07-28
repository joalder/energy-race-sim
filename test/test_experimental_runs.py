import logging

from simulation.car import Car
from simulation.environment import Environment
from simulation.position import Position
from simulation.simulation import Simulation
from simulation.track import TrackBuilder
from simulation.tile import Direction

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def test__10kwh_33max_2acceleration_on_basic_oval():
    car = Car(max_acceleration=2, max_speed=33, energy_stored=10_000)
    track = TrackBuilder("Simple Track", Position(0, 0, 0, 0)) \
        .into_straight(25) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(12) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(25) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(12) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .loop()
    environment = Environment(track)

    Simulation(car, environment).loop()
