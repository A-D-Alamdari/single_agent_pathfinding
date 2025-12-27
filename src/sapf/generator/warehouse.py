from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Set

from ..core.map import GridMap
from ..core.types import Coord


@dataclass(frozen=True, slots=True)
class WarehouseAisleSpec:
    """
    Specification for warehouse-style aisle map generation.

    Concept
    -------
    Warehouse maps typically contain:
      - repeated shelf blocks (obstacles)
      - long vertical aisles (free corridors)
      - cross-aisles (horizontal corridors) every N rows
      - margin/border clearance

    This generator should be parameterized rather than fully random to support reproducibility.
    """
    width: int
    height: int

    aisle_width: int = 1
    shelf_block_width: int = 2
    shelf_block_height: int = 6
    cross_aisle_every: int = 8
    margin: int = 1

    seed: Optional[int] = None
    start: Optional[Coord] = None
    goal: Optional[Coord] = None


def warehouse_aisles(spec: WarehouseAisleSpec) -> GridMap:
    """
    Generate a warehouse-like aisle layout.

    TODO (future tasks)
    -------------------
    1) Input validation:
       - width/height positive
       - aisle_width >= 1
       - shelf_block_width/height >= 1
       - cross_aisle_every >= 0 (0 to disable)
       - margin >= 0
       - sanity check: parameters must fit into width/height

    2) Layout algorithm (deterministic base layout):
       - define a set of shelf blocks arranged in a grid
       - leave aisles between shelf columns
       - enforce margin clearance

    3) Cross-aisles:
       - every `cross_aisle_every` rows, clear obstacles to form a horizontal corridor
       - ensure cross-aisle rows do not remove start/goal placement constraints

    4) Optional perturbations (seeded randomness):
       - randomly remove small shelf segments to vary paths
       - randomly block tiny aisle segments (careful: may disconnect)

    5) Start/goal placement:
       - if provided: validate not obstacle
       - else choose typical positions:
           * start near a border or “packing station”
           * goal deeper inside (or opposite corner)
       - ensure reachable connectivity if desired (optional enforcement)

    6) Connectivity checks (optional):
       - run a lightweight BFS from start to ensure goal reachable; if not, regenerate/adjust

    7) Tests:
       - structural invariants (e.g., margin clear, cross-aisles present)
       - start/goal not obstacles
       - reachable for default configs
    """
    raise NotImplementedError("TODO: Implement warehouse aisle generator (see docstring tasks).")
