from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Connectivity(str, Enum):
    FOUR = "4"
    EIGHT = "8"


@dataclass(frozen=True, slots=True)
class SearchConfig:
    """
    Shared search configuration.

    Note: your current built-in algorithms implement only 4-neighborhood,
    but this config keeps the interface forward-compatible.
    """
    connectivity: Connectivity = Connectivity.FOUR
    allow_diagonal: bool = False