from __future__ import annotations

import random
from typing import List, Optional

from ...generator.continuous.models import (
    CircleObstacle,
    ContinuousMap,
    Point2D,
    RectObstacle,
)


def continuous_random_circles(
        width: float,
        height: float,
        *,
        start: Point2D,
        goal: Point2D,
        num_obstacles: int = 20,
        radius_range: tuple[float, float] = (0.3, 1.2),
        seed: Optional[int] = None,
) -> ContinuousMap:
    """
    Generate a continuous map with random circular obstacles.

    TODO (future tasks)
    -------------------
    1) Validation:
       - width/height > 0
       - num_obstacles >= 0
       - radius_range valid (min>0, min<=max)

    2) Sampling policy:
       - sample centers uniformly in bounds
       - ensure obstacles do not overlap start/goal (reject sampling or shrink radius)
       - optionally avoid obstacle-overlap (or allow)

    3) Collision guarantees:
       - ensure a feasible path may exist (optional: rejection sampling with max attempts)

    4) Tests:
       - reproducibility with seed
       - obstacles count
       - no start/goal inside obstacle (if enforced)
    """
    raise NotImplementedError("TODO: Implement continuous_random_circles (see docstring tasks).")


def continuous_random_rects(
        width: float,
        height: float,
        *,
        start: Point2D,
        goal: Point2D,
        num_obstacles: int = 15,
        size_range: tuple[float, float] = (0.5, 2.0),
        seed: Optional[int] = None,
) -> ContinuousMap:
    """
    Generate a continuous map with random axis-aligned rectangular obstacles.

    TODO (future tasks)
    -------------------
    1) Validation:
       - width/height > 0
       - num_obstacles >= 0
       - size_range valid

    2) Sampling:
       - sample rectangle center and width/height within size_range
       - clip to bounds
       - avoid start/goal collisions (reject/adjust)

    3) Optional constraints:
       - avoid heavy overlap
       - enforce obstacle density targets

    4) Tests:
       - reproducibility with seed
       - rectangles are inside bounds
    """
    raise NotImplementedError("TODO: Implement continuous_random_rects (see docstring tasks).")
