from dataclasses import dataclass

from simulation.environment import Environment
from simulation.position import Position
from simulation.simulation import Simulation
from simulation.tile import Direction
from simulation.track import TrackBuilder, Track
from simulation.vehicle import Vehicle


def create_basic_oval() -> Track:
    return TrackBuilder("Basic Oval", Position(50, 50, 0, 0)) \
        .into_straight(500) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(50) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(500) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .into_straight(50) \
        .into_corner(Direction.RIGHT, 90, 10) \
        .loop()


def create_hockenheimring_short_2() -> Track:
    """
    protractor radius ~38m on current zoom

    Raw measure on the go
    s1 = 0 to 231 = 231
    c1 = 52.2, ~25m
    s2 = 248.58 to 325.15 = 76.57
    c2 = 17.2, ~500m?
    s3 = 464.92 to 538.23 = 73.31
    c3 = 46, ~45m
    c4 = 57.6, ~35m
    s4 = 602.13 to 637.50 = 35.37
    c5 = 25.8, 40m
    s5 = 683.92 to 722.71 = 38.79
    c6 = 30 L, 100m
    s6 = 824.84 to 1010 = 185.16
    c7 = 41.1 L, 90m
    s7 = 1130 to 1210 = 80
    c8 = 115.7, 12m
    s8 = 1240 to 1280 = 40
    c9 = 50 L, 25m
    s9 = 1300 to 1320 = 20
    c10 = 70, 20m
    s10 = 1340 to 1380 = 40
    c11 = 83, 50m
    s11 = 1480 to 1720 = 240
    c12 = 155.1 L, 30m
    s11 = 1800 to 1870 = 70
    c13 = 50.7 L, 45m
    s12 = 1930 to 1940 = 10
    c14 = 28.3, 45m
    s13 = 1990 to 2050 = 60
    c15 = 91.8, 32m
    s15 = 2100 to 2180 = 80
    c16 = 98, 40m
    s16 = 2260 to 2520 = 260
    """

    # https://www.racingcircuits.info/europe/germany/hockenheimring.html
    return TrackBuilder("Hockenheimring Short Circuit 2 1.0", Position(440, 50, 0, 0)) \
        .into_straight(231) \
        .into_corner(Direction.RIGHT, 52.2, 25) \
        .into_straight(76.57) \
        .into_corner(Direction.RIGHT, 17.2, 500) \
        .into_straight(73.31) \
        .into_corner(Direction.RIGHT, 46, 45) \
        .into_corner(Direction.RIGHT, 56, 35) \
        .into_straight(35.37) \
        .into_corner(Direction.RIGHT, 33, 75) \
        .into_straight(38.79) \
        .into_corner(Direction.LEFT, 34, 145) \
        .into_straight(225) \
        .into_corner(Direction.LEFT, 45, 180) \
        .into_straight(80) \
        .into_corner(Direction.RIGHT, 116, 14) \
        .into_straight(40) \
        .into_corner(Direction.LEFT, 48, 25) \
        .into_straight(15) \
        .into_corner(Direction.RIGHT, 70, 20) \
        .into_straight(43) \
        .into_corner(Direction.RIGHT, 83, 80) \
        .into_straight(240) \
        .into_corner(Direction.LEFT, 154, 38) \
        .into_straight(70) \
        .into_corner(Direction.LEFT, 58, 69) \
        .into_straight(10) \
        .into_corner(Direction.RIGHT, 37, 85) \
        .into_straight(60) \
        .into_corner(Direction.RIGHT, 91.8, 40) \
        .into_straight(77) \
        .into_corner(Direction.RIGHT, 96.8, 52) \
        .into_straight(292) \
        .loop()


def create_simulation():
    vehicle_red = Vehicle("Default Car", "red", 2, max_speed=33, energy_stored=10_000, height=1.5, track_width=1.9,
                      tire_friction_coefficient=0.8)
    vehicle_blue = Vehicle("Fast Car", "blue", 4, max_speed=40, energy_stored=10_000, height=1.5, track_width=1.9,
                          tire_friction_coefficient=0.8)

    track = create_hockenheimring_short_2()

    environment = Environment(track)
    simulation = Simulation([vehicle_red, vehicle_blue], environment)
    simulation.setup()
    return simulation


@dataclass
class UiState:
    simulation_running: bool = False
    simulation: Simulation = create_simulation()
    ticks_per_second: int = 1
    seconds_per_tick: int = 1
    single_step: bool = False
    render_scale: float = 0.7


ui_state = UiState()
