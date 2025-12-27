# from __future__ import annotations
#
# from dataclasses import dataclass
# from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Type
#
# from ..algorithms.base import PathfindingAlgorithm
#
# # Built-in algorithms (explicit import list is acceptable and predictable)
# from ..algorithms.astar import AStarAlgorithm
# from ..algorithms.bfs import BFS4
# from ..algorithms.dijkstra import Dijkstra4
# from ..algorithms.dfs import DFS4  # if present
# # from ..algorithms.greedy_best_first import GreedyBestFirstAlgorithm  # if present
#
#
# @dataclass(frozen=True, slots=True)
# class AlgorithmSpec:
#     """
#     Registry specification for an algorithm.
#
#     key:
#         Stable identifier used by CLI and GUI (e.g., "astar", "bfs").
#     display:
#         Human-friendly display name shown in GUI (e.g., "A* (Manhattan)").
#     cls:
#         Class implementing PathfindingAlgorithm.
#     """
#     key: str
#     display: str
#     cls: Type[PathfindingAlgorithm]
#
#
# class AlgorithmRegistry:
#     """
#     Production-friendly algorithm registry.
#
#     Goals
#     -----
#     - Provide stable keys for CLI/GUI selection.
#     - Avoid fragile dynamic imports at runtime.
#     - Allow controlled plugin-style registration later.
#
#     Current discovery approach:
#     - Explicit import list of built-in algorithms (predictable for packaging).
#     - Optional external registration via `register()`.
#
#     If you later want true plugin discovery, you can extend this class to load
#     entry points via importlib.metadata (see TODO in `discover_entry_points()`).
#     """
#
#     def __init__(self) -> None:
#         self._specs: Dict[str, AlgorithmSpec] = {}
#
#     def register(self, spec: AlgorithmSpec) -> None:
#         key = spec.key.strip().lower()
#         if not key:
#             raise ValueError("Algorithm key must be non-empty.")
#         if key in self._specs:
#             raise ValueError(f"Algorithm key already registered: '{key}'")
#         self._specs[key] = AlgorithmSpec(key=key, display=spec.display, cls=spec.cls)
#
#     def get_spec(self, key: str) -> Optional[AlgorithmSpec]:
#         return self._specs.get(key.strip().lower())
#
#     def keys(self) -> List[str]:
#         return sorted(self._specs.keys())
#
#     def list_specs(self) -> List[AlgorithmSpec]:
#         return [self._specs[k] for k in self.keys()]
#
#     def create(self, key: str) -> PathfindingAlgorithm:
#         spec = self.get_spec(key)
#         if spec is None:
#             raise KeyError(f"Unknown algorithm: '{key}'. Available: {', '.join(self.keys())}")
#         return spec.cls()
#
#     def create_all(self) -> Dict[str, PathfindingAlgorithm]:
#         return {k: self._specs[k].cls() for k in self.keys()}
#
#     def list_for_gui(self) -> List[Tuple[str, str]]:
#         """
#         Return a list of (key, display_name) pairs suitable for GUI dropdown.
#         """
#         return [(spec.key, spec.display) for spec in self.list_specs()]
#
#     # -------------------------
#     # Discovery helpers
#     # -------------------------
#     def register_builtins(self) -> None:
#         """
#         Register built-in algorithms explicitly.
#
#         This is the recommended approach for packaging stability.
#         """
#         # NOTE: If some modules are optional in your repo, remove those imports/specs.
#         builtins: Sequence[AlgorithmSpec] = [
#             AlgorithmSpec(key="astar", display="A* (Manhattan)", cls=AStarAlgorithm),
#             AlgorithmSpec(key="bfs", display="BFS", cls=BFS4),
#             AlgorithmSpec(key="dijkstra", display="Dijkstra", cls=Dijkstra4),
#         ]
#
#         # Optional algorithms (only if implemented in your repo)
#         try:
#             builtins = list(builtins) + [AlgorithmSpec(key="dfs", display="DFS", cls=DFS4)]
#         except Exception:
#             pass
#
#         # try:
#         #     builtins = list(builtins) + [
#         #         AlgorithmSpec(key="greedy", display="Greedy Best-First", cls=GreedyBestFirstAlgorithm)
#         #     ]
#         # except Exception:
#         #     pass
#
#         for spec in builtins:
#             # Avoid failing hard if duplicates occur from optional imports
#             if spec.key not in self._specs:
#                 self.register(spec)
#
#     def discover_entry_points(self) -> None:
#         """
#         TODO (future): Discover algorithms via Python entry points.
#
#         Example future approach:
#           - use importlib.metadata.entry_points(group="single_agent_pathfinding.algorithms")
#           - each entry point loads a PathfindingAlgorithm subclass or factory
#
#         Keeping this unimplemented by default is intentional:
#           - explicit built-ins are stable
#           - plugin discovery introduces packaging complexity
#         """
#         return
#
#
# # -------------------------
# # Public convenience API
# # -------------------------
# _DEFAULT_REGISTRY: Optional[AlgorithmRegistry] = None
#
#
# def get_registry() -> AlgorithmRegistry:
#     global _DEFAULT_REGISTRY
#     if _DEFAULT_REGISTRY is None:
#         reg = AlgorithmRegistry()
#         reg.register_builtins()
#         # reg.discover_entry_points()  # optional in the future
#         _DEFAULT_REGISTRY = reg
#     return _DEFAULT_REGISTRY
#
#
# def create_algorithms() -> Dict[str, PathfindingAlgorithm]:
#     """
#     Return instantiated algorithms keyed by stable algorithm key.
#     Used by GUI for algo selection and execution.
#     """
#     return get_registry().create_all()
#
#
# def list_algorithms_for_gui() -> List[Tuple[str, str]]:
#     """
#     Return (key, display) pairs for GUI dropdown.
#     """
#     return get_registry().list_for_gui()
#
#
# def create_algorithm(key: str) -> PathfindingAlgorithm:
#     """
#     Create one algorithm instance by key (useful for CLI).
#     """
#     return get_registry().create(key)


from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Type

from ..algorithms.base import PathfindingAlgorithm

# Built-in algorithms
from ..algorithms.astar import AStarAlgorithm
from ..algorithms.bfs import BFS4
from ..algorithms.dijkstra import Dijkstra4
from ..algorithms.dfs import DFS4


@dataclass(frozen=True, slots=True)
class AlgorithmSpec:
    """
    Registry specification for an algorithm.
    """
    key: str
    display: str
    category: str
    cls: Type[PathfindingAlgorithm]


class AlgorithmRegistry:
    def __init__(self) -> None:
        self._specs: Dict[str, AlgorithmSpec] = {}

    def register(self, spec: AlgorithmSpec) -> None:
        key = spec.key.strip().lower()
        if not key:
            raise ValueError("Algorithm key must be non-empty.")
        self._specs[key] = spec

    def get_spec(self, key: str) -> Optional[AlgorithmSpec]:
        return self._specs.get(key.strip().lower())

    def create(self, key: str) -> PathfindingAlgorithm:
        spec = self.get_spec(key)
        if spec is None:
            raise KeyError(f"Unknown algorithm: '{key}'")
        return spec.cls()

    def create_all(self) -> Dict[str, PathfindingAlgorithm]:
        return {k: self._specs[k].cls() for k in self._specs}

    def list_specs(self) -> List[AlgorithmSpec]:
        """Return all specs sorted by category then display name."""
        cat_order = {
            "Uninformed": 0,
            "Informed": 1,
            "Incremental": 2,
            "Any-Angle": 3,
            "Sampling": 4,
            "Learning": 5,
            "Optimization": 6
        }

        return sorted(
            self._specs.values(),
            key=lambda s: (cat_order.get(s.category, 99), s.display)
        )

    def register_builtins(self) -> None:
        """
        Register built-in algorithms with their categories.
        """
        specs = [
            # Uninformed
            AlgorithmSpec("bfs", "BFS (4-way)", "Uninformed", BFS4),
            AlgorithmSpec("dfs", "DFS (4-way)", "Uninformed", DFS4),
            AlgorithmSpec("dijkstra", "Dijkstra", "Uninformed", Dijkstra4),

            # Informed
            AlgorithmSpec("astar", "A* (Manhattan)", "Informed", AStarAlgorithm),
        ]

        for spec in specs:
            self.register(spec)


# -------------------------
# Public API (RESTORED)
# -------------------------
_DEFAULT_REGISTRY: Optional[AlgorithmRegistry] = None


def get_registry() -> AlgorithmRegistry:
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        reg = AlgorithmRegistry()
        reg.register_builtins()
        _DEFAULT_REGISTRY = reg
    return _DEFAULT_REGISTRY


def create_algorithms() -> Dict[str, PathfindingAlgorithm]:
    return get_registry().create_all()


def list_algorithms_for_gui() -> List[AlgorithmSpec]:
    return get_registry().list_specs()


def create_algorithm(key: str) -> PathfindingAlgorithm:
    """Create a single algorithm instance by key."""
    return get_registry().create(key)