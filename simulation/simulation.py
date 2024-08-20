import logging

from simulation.vehicle import Vehicle
from simulation.environment import Environment
from simulation.track import TrackLocation

SECONDS_PER_TICK = 2
MAX_RUNTIME_SECONDS = 24 * 60 * 60  # 24h

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Simulation:
    def __init__(self, vehicle, environment, max_runtime_seconds=MAX_RUNTIME_SECONDS):
        self.time = 0
        self.environment: Environment = environment
        self.vehicle: Vehicle = vehicle
        self.vehicle_history: dict[int, Vehicle] = {self.time: self.vehicle}
        self.max_runtime_seconds = max_runtime_seconds

    def loop(self):
        self.setup()

        while not self.is_done():
            self.tick()

        log.info(f"Simulation done. Total time: {self.time}s")

    def is_done(self) -> bool:
        return self.time >= self.max_runtime_seconds

    def setup(self):
        self.vehicle.location = TrackLocation(self.environment.track, self.environment.track.starting_tile, 0.0)

    def tick(self, seconds_per_tick: int = 1):
        self._advance_time(seconds_per_tick)

        log.debug(f"Processing tick at {self.time}s")

        self.vehicle = self.vehicle.apply(self.environment, seconds_per_tick)
        self.vehicle_history[self.time] = self.vehicle

        log.info(self.environment.status())

    def _advance_time(self, seconds_per_tick):
        self.time += seconds_per_tick
