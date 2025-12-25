from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional, Set, Tuple, Callable

from .exceptions import MapValidationError
from .types import Coord


def _coerce_coord(value: Any, *, name: str) -> Coord:
    if (
        not isinstance(value, (tuple, list))
        or len(value) != 2
        or not isinstance(value[0], int)
        or not isinstance(value[2], int)
    ):
        raise MapValidationError(f"{name} must be a 2-tuple/list of ints, got: {value!r}")
    return (int(value[0]), int(value[1]))

def _coerce_obstacles(value: Any) -> Set[Coord]:
    if value is None:
        return set()
    if not isinstance(value, (list, set, tuple)):
        raise MapValidationError(f"obstacles must be a list/set/tuple of coords, got: {type(value).__name__}")

    obs: Set[Coord] = set()

    for item in value:
        obs.add(_coerce_coord(item, name="obstacle"))

    return obs


@dataclass(frozen=True, slots=True)
class GridMap:
    """
    Canonical grid-world map representation.

    Coordinates are (x, y) where:
      - 0 <= x < width
      - 0 <= y < height
    """

    width: int
    height: int
    obstacles: Set[Coord] = field(default_factory=set)
    start: Optional[Coord] = None
    goal: Optional[Coord] = None

    def __post_init__(self) -> None:
        if not isinstance(self.width, int) or not isinstance(self.height, int):
            raise MapValidationError("Width and Height must be integers")
        if self.width <= 0 or self.height <= 0:
            raise MapValidationError("Width and Height must be positive")

        # Validate Obstacles
        for obstacle in self.obstacles:
            self._validate_coord(obstacle, name="obstacle")

        # Validate Start/Goal
        if self.start is not None:
            self._validate_coord(self.start, name="start")
            if self.start in self.obstacles:
                raise MapValidationError("Start cannot be on an obstacle")

        if self.goal is not None:
            self._validate_coord(self.goal, name="goal")
            if self.goal in self.obstacles:
                raise MapValidationError("Goal cannot be on an obstacle")

        if self.start is not None and self.goal is not None and self.start == self.goal:
            raise MapValidationError("Start and Goal cannot be the same")

    def _validate_coord(self, coord: Coord, *, name: str) -> None:
        if not isinstance(coord, tuple) or len(coord) != 2:
            raise MapValidationError(f"{name} must be a tuple (x,y), got: {coord!r}")

        x, y = coord

        if not isinstance(x, int) or not isinstance(y, int):
            raise MapValidationError(f"{name} coordinates must be integers, got: {coord!r}")

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise MapValidationError(f"{name} out of bounds: {coord!r} not in [0,{self.width})x[0,{self.height})")

    def in_bound(self, coord: Coord) -> bool:
        x, y = coord
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, coord: Coord) -> bool:
        return coord in self.obstacles

    # --------------------
    # Serialization (pure)
    # --------------------
    def to_json_dict(self) -> Dict[str, Any]:
        """
        Convert to a JSON-serializable dict.

        Uses:
          - start/goal as [x, y] or null
          - obstacles as a list of [x, y]
        """
        obstacle_list = [[x, y] for (x, y) in sorted(self.obstacles)]

        return {
            "width": self.width,
            "height": self.height,
            "start": None if self.start is None else [self.start[0], self.start[1]],
            "goal": None if self.goal is None else [self.goal[0], self.goal[1]],
            "obstacles": obstacle_list,
        }

    @classmethod
    def from_json_dict(cls, data: Dict[str, Any]) -> "GridMap":
        if not isinstance(data, dict):
            raise MapValidationError(f"map JSON must be an object/dict, got: {type(data).__name__}")

        if "width" not in data or "height" not in data:
            raise MapValidationError("map json must include 'width' and 'height' keys")

        width = data["width"]
        height = data["height"]

        start_raw = data.get("start", None)
        goal_raw = data.get("goal", None)
        obstacles_raw = data.get("obstacles", [])

        start = None if start_raw is None else _coerce_coord(start_raw, name="start")
        goal = None if goal_raw is None else _coerce_coord(goal_raw, name="goal")
        obstacles = _coerce_obstacles(obstacles_raw)

        # Construction triggers validation
        return cls(width=int(width), height=int(height), obstacles=obstacles, start=start, goal=goal)


    # ---------------------------------------------------------
    # IO convenience methods (delegate to io.* to keep isolation)
    # ---------------------------------------------------------

    def save_json(self, path: "str | Any") -> None:
        """Convenience wrapper; delegates to io.json_io.save_json."""
        from ..io.json_io import save_json as _save_json

        _save_json(self, path)

    @staticmethod
    def load_json(path: "str | Any") -> "GridMap":
        """Convenience wrapper; delegates to io.json_io.load_json."""
        from ..io.json_io import load_json as _load_json

        return _load_json(path)

    def save_pickle(self, path: "str | Any") -> None:
        """Convenience wrapper; delegates to io.pickle_io.save_pickle."""
        from ..io.pickle_io import save_pickle as _save_pickle

        _save_pickle(self, path)

    @staticmethod
    def load_pickle(path: "str | Any") -> Callable[..., GridMap]:
        """Convenience wrapper; delegates to io.pickle_io.load_pickle."""
        from ..io.pickle_io import load_pickle as _load_pickle

        return _load_pickle



