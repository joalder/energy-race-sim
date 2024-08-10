import logging
from typing import Self

from simulation.base import Tickable
from simulation.environment import Environment
from simulation.physics import power_for_velocity
from simulation.position import Position
from simulation.track import TrackLocation
from simulation.units import convert_seconds_to_hours

# vehicle has standby power, lets say 1kW. I think it was 500W in sentry mode only???
STANDBY_POWER = 1000

log = logging.getLogger(__name__)


class Car(Tickable):
    def __init__(self, max_acceleration: float, max_speed, energy_stored=0, energy_used=0, position=Position(),
                 current_speed=0, distance_driven=0, location: TrackLocation = None):
        self.max_acceleration: float = max_acceleration
        self.max_speed: int = max_speed
        self.energy_stored: float = energy_stored
        self.energy_used = energy_used
        self.location = location
        self.position: Position = position
        self.current_speed = current_speed
        self.distance_driven = distance_driven

    def apply(self, environment: Environment, time_delta: int) -> Self:
        log.info(self.status_static())

        # TODO: figure out action to do i.e. react to environment
        # TODO: find max speed in relevant future (max lookahead -> max_speed * time_per_tick)
        # TODO: adapt acceleration based on future max speed
        acceleration: float = self.max_acceleration if self.energy_stored > 0 else -self.max_acceleration

        speed_delta_ideal: float = acceleration * time_delta
        new_speed: float = max(min(self.current_speed + speed_delta_ideal, self.max_speed), 0)
        speed_delta = new_speed - self.current_speed

        average_speed: float = (self.current_speed + new_speed) / 2
        distance_delta: float = average_speed * time_delta

        # TODO: either remove completely or derive from tile & progress
        # new_position = self.position.derive(x=self.position.x + distance_delta)
        new_location, passed_finish_line = self.location.move(distance_delta)

        if passed_finish_line:
            environment.increase_lap_counter()

        # TODO: calculate energy needed/gained for velocity change specifically in relation to the rate of change and thus resistance/efficiency
        # + energy for keeping velocity (as of now)
        energy_delta = -power_for_velocity(average_speed) * convert_seconds_to_hours(
            time_delta) if acceleration >= 0 else 0 + -STANDBY_POWER * convert_seconds_to_hours(time_delta)

        log.info(self.status_delta(time_delta, energy_delta, speed_delta, acceleration, distance_delta, passed_finish_line))
        return self.derive_car(energy_delta, speed_delta, distance_delta, self.position, new_location)

    def status_static(self) -> str:
        return f"""
        Speed (m/s): {self.current_speed}
        Position (x/y/z): {self.position.x}/{self.position.y}/{self.position.z}
        Location (tile/progress): {self.location}
        Orientation (0-359): {self.position.orientation}
        Distance Driven (m): {self.distance_driven}
        Total Energy Used (Wh): {self.energy_used}
        Current Energy Stored (Wh): {self.energy_stored}
        Energy per Distance (Wh/m): {(self.energy_used / self.distance_driven) if self.distance_driven > 0 else "♾️"}
        """

    @staticmethod
    def status_delta(time_delta: int, energy_delta: float, speed_delta: float, acceleration: float,
                     distance_delta: float, passed_finish_line: bool) -> str:
        return f"""
        Time delta (s): {time_delta} 
        Speed delta Target (m/s): {speed_delta}
        Acceleration Target (m/ss): {acceleration}
        Distance Delta (m): {distance_delta}
        Energy Delta (Wh): {energy_delta}
        Passed Finish Line: {passed_finish_line}
        """

    def derive_car(self, energy_delta, speed_delta, distance_delta, new_position, new_location):
        return Car(
            max_acceleration=self.max_acceleration,
            max_speed=self.max_speed,
            energy_stored=self.energy_stored + energy_delta,
            energy_used=self.energy_used - energy_delta,
            position=new_position,
            location=new_location,
            current_speed=self.current_speed + speed_delta,
            distance_driven=self.distance_driven + distance_delta
        )
