from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from ..core.types import Coord


class ResultStatus(str, Enum):
    FOUND = "FOUND"
    NO_PATH = "NO_PATH"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class SearchResult:
    status: ResultStatus
    path: List[Coord] = field(default_factory=list)

    # Common metrics
    expansions: int = 0
    runtime_ms: float = 0.0

    # For future extensions (weights, costs, etc.)
    cost: Optional[float] = None
    extra: Dict[str, object] = field(default_factory=dict)