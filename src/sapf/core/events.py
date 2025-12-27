from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .node import Node


class SearchStatus(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"


@dataclass(frozen=True)
class SearchStep:
    """
    Represents a single atomic update from the algorithm to the GUI.
    """
    status: SearchStatus
    # Current node being processed (optional)
    current: Optional[Node] = None
    # Nodes added to open set (frontier)
    opened: list[Node] = None
    # Nodes moved to closed set (visited)
    closed: list[Node] = None

    def __post_init__(self):
        # Ensure lists are never None for safety
        if self.opened is None: object.__setattr__(self, 'opened', [])
        if self.closed is None: object.__setattr__(self, 'closed', [])