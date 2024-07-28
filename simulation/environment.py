from simulation.track import Track


class Environment:
    def __init__(self, track: Track):
        self.track = track
        self.lap_counter: int = 0

    def increase_lap_counter(self):
        self.lap_counter += 1

    def status(self) -> str:
        return f"""
        Environment Status
        Lap Counter (int): {self.lap_counter}
        """
