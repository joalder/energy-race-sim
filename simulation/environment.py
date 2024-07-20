import math
from typing import Self


# TODO: maybe move to cm or mm precision and avoid most float errors on positioning, currently rounding on calc

class Position:
    def __init__(self, x=0, y=0, z=0, orientation=0):
        self.x = x
        self.y = y
        self.z = z
        self.orientation = orientation

    @property
    def orientation_rad(self):
        return math.radians(self.orientation)

    def derive(self, x=None, y=None, z=None, orientation=None) -> Self:
        return Position(
            self.x if x is None else x,
            self.y if y is None else y,
            self.z if z is None else z,
            self.orientation if orientation is None else orientation,
        )

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.__dict__ == other.__dict__

        return False

    def __str__(self):
        return f"Position: {self.x}x {self.y}y {self.z}z {self.orientation}deg"

class Environment:
    pass
