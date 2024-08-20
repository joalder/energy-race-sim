import logging

from simulation.vehicle import Vehicle
from simulation.environment import Environment
from simulation.position import Position
from simulation.simulation import Simulation
from simulation.tile import Direction
from simulation.track import TrackBuilder

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def test__10kwh_33max_2acceleration_on_basic_oval():
    vehicle = Vehicle(max_acceleration=2, max_speed=33, energy_stored=10_000, tire_friction_coefficient=0.8, height=1.5,
                  track_width=2)
    track = TrackBuilder("Basic Oval", Position(0, 0, 0, 0)) \
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

    Simulation(vehicle, environment, 60).loop()
