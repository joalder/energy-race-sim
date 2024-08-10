import logging

from simulation.car import Car
from simulation.environment import Environment
from simulation.track import TrackLocation

SECONDS_PER_TICK = 2
MAX_RUNTIME_SECONDS = 60 * 10  # 24 * 60 * 60  # for 24h

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Simulation:
    def __init__(self, car, environment):
        self.time = 0
        self.environment: Environment = environment
        self.car: Car = car
        self.car_history: dict[int, Car] = {self.time: self.car}

    def loop(self):
        self.setup()

        while not self.is_done():
            self.tick()

        log.info(f"Simulation done. Total time: {self.time}s")

    def is_done(self) -> bool:
        return self.time >= MAX_RUNTIME_SECONDS

    def setup(self):
        self.car.location = TrackLocation(self.environment.track, self.environment.track.starting_tile, 0.0)

    def tick(self, seconds_per_tick: int = 1):
        self._advance_time(seconds_per_tick)

        log.debug(f"Processing tick at {self.time}s")

        self.car = self.car.apply(self.environment, seconds_per_tick)
        self.car_history[self.time] = self.car

        log.info(self.environment.status())

    def _advance_time(self, seconds_per_tick):
        self.time += seconds_per_tick
