from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Sequence

from .types import Coord


class SearchStatus(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"  # Generic finish
    FOUND = "FOUND"        # Specific success
    NO_PATH = "NO_PATH"    # Specific failure


@dataclass(frozen=True, slots=True)
class SearchStep:
    """
    A single visualization-ready snapshot of a search.

    This object is created by the algorithm and sent to the GUI.
    """
    # The current node being processed
    current: Optional[Coord]

    # The entire list of nodes currently in the open set (frontier)
    open_set: Sequence[Coord] = field(default_factory=list)

    # The entire list of nodes currently in the closed set (visited)
    closed_set: Sequence[Coord] = field(default_factory=list)

    # Nodes just added to the open set in this step (for highlighting)
    open_added: Sequence[Coord] = field(default_factory=list)

    # The current best known path (from start to current or start to goal)
    best_path: Optional[Sequence[Coord]] = None

    # Text log explaining what happened in this step
    log: str = ""

    # The current status of the search
    status: SearchStatus = SearchStatus.RUNNING

    def __post_init__(self) -> None:
        """Ensure defaults are safe if None is strictly passed."""
        # Note: frozen=True means we must use object.__setattr__ to modify fields
        if self.open_set is None:
            object.__setattr__(self, 'open_set', [])
        if self.closed_set is None:
            object.__setattr__(self, 'closed_set', [])
        if self.open_added is None:
            object.__setattr__(self, 'open_added', [])