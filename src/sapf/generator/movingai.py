from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple, Union

from ..core.map import GridMap
from ..core.types import Coord


PathLike = Union[str, Path]


@dataclass(frozen=True, slots=True)
class MovingAIScenarioEntry:
    """
    One line/record from a MovingAI .scen file.

    Typical .scen format includes:
      - bucket, map, width, height, startx, starty, goalx, goaly, optimalLength
    """
    start: Coord
    goal: Coord
    optimal_length: Optional[float] = None


def load_movingai_map(path: PathLike) -> GridMap:
    """
    Load a MovingAI .map file into a GridMap.

    TODO (future tasks)
    -------------------
    1) Parse file header:
       - expect:
           type octile
           height H
           width W
           map
       - then H lines of W characters

    2) Terrain mapping policy:
       Common chars:
         '.' = free
         '@' = obstacle
         'T' = trees (often blocked)
         'S','W' etc. may appear depending on dataset
       Decide policy:
         - simplest: free iff char == '.'
         - or allow config-driven mapping for weighted terrains later

    3) Coordinate convention:
       MovingAI uses (x, y) where x is column and y is row.
       Our GridMap uses the same (x, y) convention.

    4) Start/goal:
       .map files do not contain start/goal; return GridMap with start=None, goal=None.

    5) Robust errors:
       - missing headers
       - incorrect dimensions
       - line length mismatch

    6) Tests:
       - parse a minimal embedded map fixture
       - verify width/height and obstacle positions
    """
    raise NotImplementedError("TODO: Implement MovingAI .map parser (see docstring tasks).")


def load_movingai_scenarios(path: PathLike) -> List[MovingAIScenarioEntry]:
    """
    Load a MovingAI .scen file into a list of scenario entries.

    TODO (future tasks)
    -------------------
    1) Parse the first line:
       - expects: "version 1" (commonly)

    2) Parse each subsequent line:
       Typical columns:
         bucket map width height startx starty goalx goaly optimalLength
       Extract:
         start=(startx, starty)
         goal=(goalx, goaly)
         optimal_length (float) if present

    3) Robustness:
       - ignore blank lines / comments (if present)
       - handle variable whitespace
       - validate int/float conversions

    4) Tests:
       - parse minimal scenarios fixture
       - verify first few extracted pairs
    """
    raise NotImplementedError("TODO: Implement MovingAI .scen parser (see docstring tasks).")


def movingai_instance(map_path: PathLike, scen_path: PathLike, index: int) -> GridMap:
    """
    Convenience helper:
      - loads a .map into GridMap
      - loads scenarios
      - sets start/goal from scenario entry `index`

    TODO (future tasks)
    -------------------
    1) Validate index within range
    2) Ensure start/goal are in-bounds and not obstacles
    3) Return a new GridMap with start/goal set
    4) Optional: validate connectivity; warn if unreachable
    """
    raise NotImplementedError("TODO: Implement movingai_instance helper (see docstring tasks).")
