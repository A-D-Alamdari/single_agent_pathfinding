from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple, Union

Point2D = Tuple[float, float]


@dataclass(frozen=True, slots=True)
class CircleObstacle:
    center: Point2D
    radius: float


@dataclass(frozen=True, slots=True)
class RectObstacle:
    """
    Axis-aligned rectangle obstacle.
    """
    x_min: float
    y_min: float
    x_max: float
    y_max: float


Obstacle = Union[CircleObstacle, RectObstacle]


@dataclass(frozen=True, slots=True)
class ContinuousMap:
    """
    Continuous-space environment model.

    TODO (future tasks)
    -------------------
    1) Validation:
       - width/height > 0
       - start/goal within bounds
       - obstacle parameters valid (radius>0, x_min<x_max, etc.)

    2) Collision checks:
       - point_in_obstacle(p) -> bool
       - segment_intersects_obstacle(a, b) -> bool (for motion planning)

    3) Distance metrics:
       - Euclidean distance
       - optionally configurable metrics

    4) Serialization:
       - define JSON schema (io/schema_continuous.py)
       - save/load to JSON

    5) Discretization utilities (optional):
       - rasterize to GridMap at resolution R for visualization
       - useful for reusing discrete GUI

    6) Tests:
       - bounds validation
       - obstacle intersection checks
       - serialization round-trip
    """
    width: float
    height: float
    start: Point2D
    goal: Point2D
    obstacles: List[Obstacle] = field(default_factory=list)