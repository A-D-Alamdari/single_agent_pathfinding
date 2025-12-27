from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator, List, Union

from ..core.map import GridMap
from ..core.types import Coord
from ..core.events import SearchStep, SearchStatus


# Type alias for the return type
FindPathReturn = Union[List[Coord], Iterator[SearchStep]]


class PathfindingAlgorithm(ABC):
    """
    Base interface for all single-agent pathfinding algorithms.

    Contract:
      - `name` is displayed in GUI lists (stable human-readable label).
      - `find_path(grid_map, step_mode=False)` returns:
          * step_mode=False: final path as List[Coord] (empty list if no path)
          * step_mode=True : an iterator/generator yielding SearchStep snapshots
    """

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def find_path(self, grid_map: GridMap, *, step_mode: bool) -> FindPathReturn:
        """
        Execute the pathfinding search.

        Args:
            grid_map: The environment map.
            step_mode: If True, yield SearchStep objects for visualization.
                       If False, return the final List[Coord].
        """
        raise NotImplementedError