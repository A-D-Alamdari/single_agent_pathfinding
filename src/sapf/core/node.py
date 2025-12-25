from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..core.types import Coord


@dataclass(frozen=True, slots=True)
class Node:
    """
    Visualization-friendly node projection.

    Algorithms can map internal state to this representation.
    """
    pos: Coord
    g: float = 0.0
    h: float = 0.0
    f: float = 0.0
    parent: Optional[Coord] = None