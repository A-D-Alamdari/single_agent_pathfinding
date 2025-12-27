from __future__ import annotations

from typing import Optional

from ..core.map import GridMap
from ..core.types import Coord
from ..generator.generate import (
    generate_map,
    generate_random_obstacles,
)


def empty_grid(
        width: int,
        height: int,
        *,
        start: Optional[Coord] = None,
        goal: Optional[Coord] = None,
) -> GridMap:
    """
    Generate an empty grid with no obstacles.
    """
    return generate_map(
        width=width,
        height=height,
        start=start,
        goal=goal,
        obstacles=[],
    )


def random_obstacles_grid(
        width: int,
        height: int,
        *,
        obstacle_ratio: float = 0.2,
        start: Optional[Coord] = None,
        goal: Optional[Coord] = None,
        seed: Optional[int] = None,
) -> GridMap:
    """
    Generate a grid with uniformly random obstacles.
    """
    obstacles = generate_random_obstacles(
        width=width,
        height=height,
        obstacle_ratio=obstacle_ratio,
        start=start,
        goal=goal,
        seed=seed,
    )
    return generate_map(
        width=width,
        height=height,
        start=start,
        goal=goal,
        obstacles=obstacles,
    )


def simple_maze_grid(
        width: int,
        height: int,
        *,
        start: Optional[Coord] = None,
        goal: Optional[Coord] = None,
) -> GridMap:
    """
    Generate a very simple maze-like grid using a checker-wall pattern.

    This is NOT a perfect maze algorithm.
    It is intended for visualization and teaching.
    """
    obstacles = set()

    for y in range(height):
        for x in range(width):
            if (x % 2 == 1) and (y % 2 == 1):
                obstacles.add((x, y))

    # Ensure start/goal are not blocked
    if start is not None:
        obstacles.discard(start)
    if goal is not None:
        obstacles.discard(goal)

    return generate_map(
        width=width,
        height=height,
        start=start,
        goal=goal,
        obstacles=obstacles,
    )
