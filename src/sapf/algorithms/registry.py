from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Type

from ..algorithms.base import PathfindingAlgorithm

# Built-in algorithms
# Informed Algorithms -----------------------------------
from ..algorithms.uninformed.bfs import BFS4
from ..algorithms.uninformed.dijkstra import Dijkstra4
from ..algorithms.uninformed.dfs import DFS4

# Uninformed Algorithms ---------------------------------
from ..algorithms.informed.astar import AStarAlgorithm
from ..algorithms.informed.greedy_best_first import GreedyBestFirstAlgorithm
from ..algorithms.informed.weighted_astar import WeightedAStarAlgorithm

# Incremental Algorithms --------------------------------
from ..algorithms.incremental.dstar_lite import DStarLiteAlgorithm

# Graph-Based Algorithms --------------------------------
from ..algorithms.graph_based.bellman_ford import BellmanFordAlgorithm


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
            AlgorithmSpec("greedy", "Greedy Best-First", "Informed", GreedyBestFirstAlgorithm),
            AlgorithmSpec("wastar", "Weighted A* (w=1.5)", "Informed", WeightedAStarAlgorithm),

            # Incremental
            AlgorithmSpec("dstarlite", "D* Lite", "Incremental", DStarLiteAlgorithm),

            # Graph-Based
            AlgorithmSpec("bellmanford", "Bellman-Ford", "Graph-Based", BellmanFordAlgorithm),
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