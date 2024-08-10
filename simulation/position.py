import math
from typing import Self, Optional

from simulation.units import DISTANCE_PRECISION


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

    def translate(self, distance: float, relative_angle: Optional[float] = None) -> Self:
        translation_angle = self.orientation + relative_angle if relative_angle is not None else self.orientation
        new_x = round(self.x + distance * math.sin(math.pi / 2 - math.radians(translation_angle)),
                      DISTANCE_PRECISION)
        new_y = round(self.y + distance * math.sin(math.radians(translation_angle)), DISTANCE_PRECISION)
        return self.derive(x=new_x, y=new_y)

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

    def __repr__(self):
        return self.__str__()
