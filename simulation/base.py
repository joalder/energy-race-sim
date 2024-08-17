from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from simulation.environment import Environment
from simulation.track import TrackLocation


@dataclass
class TickableDelta(ABC):
    speed_delta: float = 0.0
    acceleration: float = 0.0
    energy_delta: float = 0.0
    distance_delta: float = 0.0
    new_location: TrackLocation = None
    delta_lap: int = 0


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
