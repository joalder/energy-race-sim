import logging
from dataclasses import dataclass, field
from typing import Self

from simulation.base import Tickable, TickableDelta
from simulation.environment import Environment
from simulation.physics import power_for_velocity
from simulation.track import TrackLocation
from simulation.units import convert_seconds_to_hours

# vehicle has standby power, lets say 1kW. I think it was 500W in sentry mode only???
STANDBY_POWER = 1000

log = logging.getLogger(__name__)


@dataclass
class Vehicle(Tickable):
    max_acceleration: float
    max_speed: int
    height: float
    track_width: float
    tire_friction_coefficient: float
    energy_stored: float = 0
    energy_used: float = 0
    location: TrackLocation = None
    current_speed: float = 0.0
    distance_driven: float = 0
    lap_counter: int = 0
    delta_input: TickableDelta = field(default_factory=TickableDelta)

    @property
    def energy_used_per_distance(self) -> float:
        return self.energy_used / self.distance_driven if self.distance_driven > 0 else float("inf")

    def apply(self, environment: Environment, time_delta: int) -> Self:
        log.info(self.status_static())

        delta = self.calculate_delta(environment, time_delta)

        log.info(self.status_delta(time_delta, delta))
        return self.derive(delta)

    def calculate_delta(self, environment: Environment, time_delta_seconds: int) -> TickableDelta:
        lookahead_factor = 20
        lookahead_distance = self.max_speed * time_delta_seconds * lookahead_factor
        speed_limit_locations = self.location.get_upcoming_max_speed_locations(lookahead_distance,
                                                                               self.tire_friction_coefficient,
                                                                               self.height,
                                                                               self.track_width)
        speed_limit_most_relevant = min(speed_limit_locations,
                                        key=lambda x: (x.speed_limit - self.current_speed) / time_delta_seconds)
        acceleration: float = self.max_acceleration

        acceleration_safety_factor = 0.90
        acceleration_safety_distance = 40  # always decelerate if distance is less than this
        # average deceleration to reach speed limit with the given distance
        if speed_limit_most_relevant.distance > 0:
            # This calculation is entirely based on co-pilot, not sure if it is correct
            deceleration = (self.current_speed ** 2 - speed_limit_most_relevant.speed_limit ** 2) / (
                        2 * speed_limit_most_relevant.distance)
            # TODO: also check for minimum distance to avoid unnecessary acceleration
            if deceleration >= self.max_acceleration * acceleration_safety_factor or speed_limit_most_relevant.distance < acceleration_safety_distance:
                acceleration = -deceleration
        elif self.current_speed > speed_limit_most_relevant.speed_limit * acceleration_safety_factor:
            # Assume we already did all the
            acceleration = 0

        # Apply acceleration limits
        acceleration = min(acceleration, self.max_acceleration)
        acceleration = acceleration if self.energy_stored > 0 else -self.max_acceleration

        speed_delta_ideal: float = acceleration * time_delta_seconds
        new_speed: float = max(min(self.current_speed + speed_delta_ideal, self.max_speed), 0)
        speed_delta = new_speed - self.current_speed

        acceleration = speed_delta / time_delta_seconds

        average_speed: float = (self.current_speed + new_speed) / 2
        distance_delta: float = average_speed * time_delta_seconds

        new_location, passed_finish_line = self.location.move(distance_delta)

        # This does not work if multiple laps are done in one tick, but probably not relevant
        delta_lap = 1 if passed_finish_line else 0

        # TODO: calculate energy needed/gained for velocity change specifically in relation to the rate of change and thus resistance/efficiency
        # + energy for keeping velocity (as of now)
        energy_delta = -power_for_velocity(average_speed) * convert_seconds_to_hours(time_delta_seconds) \
            if acceleration >= 0 else 0 + -STANDBY_POWER * convert_seconds_to_hours(time_delta_seconds)

        return TickableDelta(speed_delta, acceleration, energy_delta, distance_delta, new_location, delta_lap)

    def derive(self, delta: TickableDelta) -> Self:
        return Vehicle(
            max_acceleration=self.max_acceleration,
            max_speed=self.max_speed,
            height=self.height,
            track_width=self.track_width,
            tire_friction_coefficient=self.tire_friction_coefficient,
            energy_stored=self.energy_stored + delta.energy_delta,
            energy_used=self.energy_used - delta.energy_delta,
            location=delta.new_location,
            current_speed=self.current_speed + delta.speed_delta,
            distance_driven=self.distance_driven + delta.distance_delta,
            lap_counter=self.lap_counter + delta.delta_lap,
            delta_input=delta
        )

    def status_static(self) -> str:
        return f"""
        Speed (m/s): {self.current_speed}
        Location (tile/progress): {self.location}
        Distance Driven (m): {self.distance_driven}
        Total Energy Used (Wh): {self.energy_used}
        Current Energy Stored (Wh): {self.energy_stored}
        Energy per Distance (Wh/m): {self.energy_used_per_distance if self.distance_driven > 0 else "♾️"}
        """

    @staticmethod
    def status_delta(time_delta: int, delta: TickableDelta) -> str:
        return f"""
        Time delta (s): {time_delta} 
        Speed delta Target (m/s): {delta.speed_delta}
        Acceleration Target (m/ss): {delta.acceleration}
        Distance Delta (m): {delta.distance_delta}
        Energy Delta (Wh): {delta.energy_delta}
        Passed Finish Line: {delta.delta_lap}
        """
