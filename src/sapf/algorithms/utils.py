from __future__ import annotations

from typing import List, Mapping, Optional

from ..core.types import Coord
from ..core.map import GridMap


def reconstruct_path(came_from: Mapping[Coord, Coord], current: Coord) -> List[Coord]:
    """
    Reconstruct a path ending at `current` by following `came_from` pointers.

    `came_from` maps child -> parent.
    Returns path from start to `current` (inclusive).

    Raises:
      - ValueError if a cycle is detected.
    """
    path: List[Coord] = [current]
    seen: set[Coord] = {current}

    while current in came_from:
        current = came_from[current]
        if current in seen:
            raise ValueError("Cycle detected in came_from; cannot reconstruct path.")
        seen.add(current)
        path.append(current)

    path.reverse()
    return path


def reconstruct_path_if_reachable(
        came_from: Mapping[Coord, Coord],
        *,
        start: Coord,
        goal: Coord,
) -> Optional[List[Coord]]:
    """
    Attempt to reconstruct a start->goal path.

    Returns None if `goal` is not reachable from `start` via `came_from`
    (i.e., goal not in came_from chain and goal != start).
    """
    if goal == start:
        return [start]
    if goal not in came_from:
        return None

    path = reconstruct_path(came_from, goal)
    if not path or path[0] != start:
        return None
    return path


def neighbors_4(grid_map: GridMap, coord: Coord) -> List[Coord]:
    """
    4-neighborhood (Von Neumann): left, right, up, down.

    Uses GridMap.in_bounds() and GridMap.is_blocked().
    """
    x, y = coord
    candidates = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    out: List[Coord] = []
    for nx, ny in candidates:
        nc = (nx, ny)
        if grid_map.in_bound(nc) and not grid_map.is_blocked(nc):
            out.append(nc)
    return out
