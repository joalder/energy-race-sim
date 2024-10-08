DISTANCE_PRECISION = 3
PROGRESS_PERCENTAGE_PRECISION = 4


def convert_seconds_to_hours(seconds: int) -> float:
    return seconds / (60 * 60)


def abs_angle(angle: float) -> float:
    return (angle + 360) % 360
