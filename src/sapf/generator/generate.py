from __future__ import annotations

import random
from typing import Iterable, Optional, Set

from ..core.map import GridMap
from ..core.types import Coord


def generate_map(
        width: int,
        height: int,
        *,
        start: Optional[Coord] = None,
        goal: Optional[Coord] = None,
        obstacles: Optional[Iterable[Coord]] = None,
) -> GridMap:
    """
    Create a GridMap from explicit parameters.

    This function performs no randomization.
    All validation is handled by GridMap itself.
    """
    obs_set: Set[Coord] = set(obstacles) if obstacles is not None else set()
    return GridMap(
        width=width,
        height=height,
        obstacles=obs_set,
        start=start,
        goal=goal,
    )


def generate_random_obstacles(
        width: int,
        height: int,
        *,
        obstacle_ratio: float = 0.2,
        start: Optional[Coord] = None,
        goal: Optional[Coord] = None,
        seed: Optional[int] = None,
) -> Set[Coord]:
    """
    Generate a random obstacle set.

    Parameters
    ----------
    obstacle_ratio : float
        Fraction of cells to be obstacles (0.0–1.0)
    seed : int, optional
        RNG seed for reproducibility
    """
    if not 0.0 <= obstacle_ratio <= 1.0:
        raise ValueError("obstacle_ratio must be in [0.0, 1.0]")

    rng = random.Random(seed)

    forbidden: Set[Coord] = set()
    if start is not None:
        forbidden.add(start)
    if goal is not None:
        forbidden.add(goal)

    all_cells = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in forbidden
    ]

    rng.shuffle(all_cells)
    obstacle_count = int(round(len(all_cells) * obstacle_ratio))
    return set(all_cells[:obstacle_count])
