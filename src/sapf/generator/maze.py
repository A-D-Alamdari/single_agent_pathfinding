from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ..core.map import GridMap
from ..core.types import Coord


class MazeAlgorithm(str, Enum):
    DFS = "dfs"
    PRIM = "prim"
    KRUSKAL = "kruskal"


@dataclass(frozen=True, slots=True)
class MazeSpec:
    """
    Specification for perfect maze generation.

    Notes
    -----
    A "perfect maze" is a maze with:
      - exactly one unique path between any two free cells (i.e., it is a tree).

    Recommended representation:
      - generate over a logical cell grid (cell_width x cell_height)
      - upscale to a wall grid size: (2*cell_width + 1) x (2*cell_height + 1)
      - carve corridors between odd-indexed cells, leaving walls on even indices
    """
    cell_width: int
    cell_height: int
    algorithm: MazeAlgorithm = MazeAlgorithm.DFS
    seed: Optional[int] = None

    # Optional: enforce that start/goal are on corridor cells (odd coordinates) after scaling
    start: Optional[Coord] = None
    goal: Optional[Coord] = None


def perfect_maze(spec: MazeSpec) -> GridMap:
    """
    Generate a perfect maze as a GridMap.

    TODO (future tasks)
    -------------------
    1) Input validation:
       - cell_width/cell_height > 0
       - enforce minimum sizes (e.g., >= 2) if needed
       - if start/goal provided, validate and later map into scaled grid

    2) Choose algorithm implementation:
       - DFS recursive backtracker (fast; produces long corridors)
       - Randomized Prim (bushy; more uniform)
       - Kruskal with Union-Find (uniform spanning tree)

    3) Implement internal maze representation:
       - represent logical maze as adjacency between cells (graph)
       - or represent as wall grid carved directly

    4) Upscaling to wall grid:
       - grid_w = 2*cell_width + 1
       - grid_h = 2*cell_height + 1
       - initialize all walls as obstacles
       - carve corridors at odd coordinates
       - carve passages between neighboring cells

    5) Start/goal placement:
       - if spec.start/spec.goal provided, map/validate them on the scaled grid
       - otherwise choose defaults (e.g., top-left corridor and bottom-right corridor)
       - ensure they are not obstacles

    6) Determinism:
       - use random.Random(spec.seed) for reproducible generation

    7) Tests:
       - connectivity: all corridor cells reachable from each other
       - perfect property: unique path (can be validated by checking edges = nodes-1 on graph)
       - ensure start/goal are free and within bounds
    """
    raise NotImplementedError("TODO: Implement perfect maze generator (see docstring tasks).")
