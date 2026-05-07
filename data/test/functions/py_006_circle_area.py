import math


def circle_area(radius: float) -> float:
    if radius < 0:
        raise ValueError("radius must be non-negative")
    return math.pi * radius * radius
