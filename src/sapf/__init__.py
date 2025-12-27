"""
sapf: Single-Agent Pathfinding (Grid World)

This package provides:
- Core data model (GridMap, types, exceptions)
- Pluggable pathfinding algorithms with step-by-step visualization events
- IO utilities (JSON / pickle)
- CLI and GUI entrypoints

Recommended usage:
- GUI: python -m sapf.gui.app
- CLI: python -m sapf.cli --help
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

# -----------------------------
# Public API re-exports (stable)
# -----------------------------

# Core model
from .core.map import GridMap
from .core.types import Coord

# Algorithms public types
from .algorithms.base import PathfindingAlgorithm, SearchStatus, SearchStep
from .algorithms.utils import reconstruct_path

# Registry helpers (preferred)
from .algorithms.registry import (
    create_algorithm,
    create_algorithms,
    get_registry,
    list_algorithms_for_gui,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "GridMap",
    "Coord",
    # Algorithms base types
    "PathfindingAlgorithm",
    "SearchStatus",
    "SearchStep",
    "reconstruct_path",
    # Registry helpers
    "get_registry",
    "create_algorithms",
    "create_algorithm",
    "list_algorithms_for_gui",
]

# -----------------------------
# Package version
# -----------------------------
try:
    __version__ = version("sapf")
except PackageNotFoundError:  # running from source tree without installation
    __version__ = "0.0.0"