from simulation.track import Track


class Environment:
    def __init__(self, track: Track):
        self.track = track

    def status(self) -> str:
        return f"""
        Environment Status
        """
