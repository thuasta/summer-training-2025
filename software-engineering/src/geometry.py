from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class Vector2D:
    x: float
    y: float

@dataclass
class Segment:
    begin: Vector2D
    end: Vector2D

@dataclass
class Circle:
    center: Vector2D
    radius: float

@dataclass
class MovingCircle:
    current_pos: Circle
    velocity: Vector2D

def is_tangent(line: Segment, circle: Circle) -> bool:
    """Tells if `line` is the tangent of  `circle`

    Note that Segment is a line with finite length. If the point of 
    tangency is not on the segment, will return false.

    Args:
        line (Segment): The segment
        circle (Circle): The circle
    """
    raise NotImplementedError

def will_collide(wall: Segment, ball: MovingCircle) -> Tuple[Optional[float], Optional[Vector2D]]:
    """Tells if the `ball` will collide on the wall.

    Args:
        wall (Segment): The wall.
        ball (MovingCircle): The ball. Assuming that the ball is in uniform linear motion.

    Returns:
        Tuple[int, Vector2D]: The time and the position when collision happens.
        If the collision won't happen, return (None, None)
    """
    raise NotImplementedError
