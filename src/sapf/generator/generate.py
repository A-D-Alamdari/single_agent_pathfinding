from __future__ import annotations

import random
from typing import Iterable, Optional, Set

from ..core.map import GridMap
from ..core.types import Coord


def generate_map(
        width: int,
        height: int,
        start: Optional[Coord] = None,
        goal: Optional[Coord] = None,
        obstacles: Optional[Iterable[Coord]] = None,
) -> GridMap:
    obs_set: Set[Coord] = set(obstacles) if obstacles is not None else set()

    return GridMap(width=width, height=height, obstacles=obs_set, start=start, goal=goal)


def generate_random_obstacles(
        width: int,
        height: int,
        *,
        start: Optional[Coord] = None,
        goal: Optional[Coord] = None,
        obstacle_ratio: float = .2,
        seed: Optional[int] = None
) -> Set[Coord]:
    """
    Generate a random obstacle set.

    obstacle_ratio is the fraction of cells to mark as obstacles (0.0..1.0).
    start/goal (if provided) are guaranteed to not be obstacles.
    """

    if obstacle_ratio < .0 or obstacle_ratio > 1.:
        raise ValueError(f"obstacle_ratio must be between 0 and 1.")

    rng = random.Random(seed)
    total = width * height
    target = int(round(total * obstacle_ratio))

    forbidden: Set[Coord] = set()

    if start is not None:
        forbidden.add(start)

    if goal is not None:
        forbidden.add(goal)

    all_cells = [(x, y) for y in range(height) for x in range(width) if (x, y) not in forbidden]
    rng.shuffle(all_cells)

    # Cap to available cells
    target = min(target, len(all_cells))

    return set(all_cells[:target])

