from abc import ABC, abstractmethod

from simulation.environment import Environment


class Tickable(ABC):
    @abstractmethod
    def apply(self, environment: Environment, time_delta_second: int):
        pass
