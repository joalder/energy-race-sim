from abc import ABC, abstractmethod
from typing import Self

from simulation.environment import Environment


class TickableDelta(ABC):
    def __init__(self, speed_delta, acceleration, energy_delta, distance_delta, new_location, passed_finish_line):
        self.speed_delta = speed_delta
        self.acceleration = acceleration
        self.energy_delta = energy_delta
        self.distance_delta = distance_delta
        self.new_location = new_location
        self.passed_finish_line = passed_finish_line


class Tickable(ABC):
    @abstractmethod
    def apply(self, environment: Environment, time_delta_second: int) -> Self:
        pass

    @abstractmethod
    def calculate_delta(self, environment: Environment, time_delta_second: int) -> TickableDelta:
        pass

    @abstractmethod
    def derive(self, delta: TickableDelta) -> Self:
        pass
