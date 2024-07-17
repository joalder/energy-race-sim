#!/usr/bin/env python3
"""
Units used
time: second (for now)
distance: meter
speed: meter / second
acceleration meter / second*seconds
power: W
energy: Wh
"""

import logging

from simulation.car import Car
from simulation.environment import Environment

SECONDS_PER_TICK = 5
MAX_RUNTIME_SECONDS = 60 * 10  # 24 * 60 * 60  # for 24h

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Simulation:
    def __init__(self):
        self.time = 0
        self.environment: Environment = Environment()
        self.car: Car = Car(max_acceleration=2, max_speed=33, energy_stored=10_000)
        self.car_history: dict[int, Car] = {self.time: self.car}

    def is_done(self) -> bool:
        return self.time >= MAX_RUNTIME_SECONDS

    def advance_time(self):
        self.time += SECONDS_PER_TICK

    def tick(self):
        self.advance_time()

        log.debug(f"Processing tick at {self.time}s")

        self.car = self.car.apply(self.environment, SECONDS_PER_TICK)
        self.car_history[self.time] = self.car

    def loop(self):
        while not self.is_done():
            self.tick()

        log.info(f"Simulation done. Total time: {self.time}s")


def main() -> None:
    Simulation().loop()


if __name__ == "__main__":
    main()
