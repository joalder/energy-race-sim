from dataclasses import dataclass

from simulation.car import Car
from simulation.environment import Environment
from simulation.position import Position
from simulation.simulation import Simulation
from simulation.tile import Direction
from simulation.track import TrackBuilder


def create_simulation():
    car = Car(max_acceleration=2, max_speed=33, energy_stored=10_000, height=1.5, track_width=1.9,
              tire_friction_coefficient=0.8)
    track = TrackBuilder("Basic Oval", Position(50, 50, 0, 0)) \
        .into_straight(500) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(50) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(500) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(50) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .loop()
    environment = Environment(track)
    simulation = Simulation(car, environment)
    simulation.setup()
    return simulation


@dataclass
class UiState:
    simulation_running: bool = False
    simulation: Simulation = create_simulation()
    ticks_per_second: int = 1
    seconds_per_tick: int = 1
    single_step: bool = False


ui_state = UiState()
