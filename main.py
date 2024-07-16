#!/usr/bin/env python3
'''
Units used
time: second (for now)
distance: meter
speed: meter / second
acceleration meter / second*seconds
power: W
energy: Wh
'''

import logging
from abc import ABC, abstractmethod

SECONDS_PER_TICK = 5
MAX_RUNTIME_SECONDS = 60 * 10  # 24 * 60 * 60  # for 24h
STANDBY_POWER = 1000

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Environment:
    pass


class Tickable(ABC):
    @abstractmethod
    def apply(self, environment: Environment, time_delta_second: int):
        pass


def power_for_velocity(velocity):
    # calculate air resistance
    roh = 1.2041
    coefficient_of_drag = 0.23
    area = 1.433 * 1.850  # from model 3 width * height
    cw_a = coefficient_of_drag * area
    force_air = cw_a * velocity * velocity / 2 * roh

    # calculate roll resistance
    c_r = 0.012  # asphalt 0.011-0,015 according Wikipedia.
    force_roll_resistance = c_r * 1950 * 9.81  # model 3 incl driver = 1,95t*g=F

    # vehicle has standby power, lets say 1kW. I think it was 500W in sentry mode only???
    power_standby = STANDBY_POWER

    # calculate power needed for specific velocity
    return (force_air + force_roll_resistance) * velocity + power_standby


class Car(Tickable):
    max_acceleration = 2
    max_speed_ms = 33

    current_speed = 0
    distance_driven = 0
    energy_used = 0
    energy_stored = 2_000

    def apply(self, environment: Environment, time_delta):
        old_speed = self.current_speed

        # TODO: figure out action to do i.e. react to environment
        acceleration = self.max_acceleration if self.energy_stored > 0 else -self.max_acceleration

        speed_delta = acceleration * time_delta
        new_speed = max(min(self.current_speed + speed_delta, self.max_speed_ms), 0)

        average_speed = (old_speed + new_speed) / 2
        distance_delta = average_speed * time_delta

        # TODO: calculate energy needed/gained for velocity change specifically in relation to the rate of change and thus resistance/efficiency
        # + energy for keeping velocity (as of now)
        energy_delta = power_for_velocity(average_speed) * (time_delta / (60 * 60)) if acceleration >= 0 else STANDBY_POWER * (time_delta / (60 * 60))

        self.current_speed = new_speed
        self.distance_driven += distance_delta
        self.energy_used += energy_delta
        self.energy_stored -= energy_delta
        log.info(self.status(energy_delta, speed_delta, acceleration, distance_delta))

    def status(self, energy_delta: float, speed_delta: float, acceleration: float, distance_delta: float) -> str:
        return f"""
        Speed (m/s): {self.current_speed}
        Speed delta Target (m/s): {speed_delta}
        Acceleration Target (m/ss): {acceleration}
        Distance Driven (m): {self.distance_driven}
        Distance Delta (m): {distance_delta}
        Energy Delta (Wh): {energy_delta}
        Total Energy Used (Wh): {self.energy_used}
        Current Energy Stored (Wh): {self.energy_stored}
        Energy per Distance (Wh/m): {self.energy_used / self.distance_driven}
        """

class SimulationState:
    time_seconds = 0
    environment: Environment = Environment()
    objects: list[Tickable] = [Car()]

    def is_done(self) -> bool:
        return self.time_seconds >= MAX_RUNTIME_SECONDS

    def advance_time(self):
        self.time_seconds += SECONDS_PER_TICK

    def tick(self):
        self.advance_time()

        log.debug(f"Processing tick at {self.time_seconds}s")

        for object in self.objects:
            object.apply(self.environment, SECONDS_PER_TICK)


def main() -> None:
    state = SimulationState()

    while not state.is_done():
        state.tick()

    log.info(f"Simulation done. Total time: {state.time_seconds}s")


if __name__ == "__main__":
    main()
