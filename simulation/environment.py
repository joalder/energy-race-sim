from typing import Self


class Position:
    def __init__(self, x=0, y=0, z=0, orientation=0):
        self.x = x
        self.y = y
        self.z = z
        self.orientation = orientation

    def derive(self, x=None, y=None, z=None, orientation=None) -> Self:
        return Position(
            self.x if x is None else x,
            self.y if y is None else y,
            self.z if z is None else z,
            self.orientation if orientation is None else orientation,
        )


class Environment:
    pass
