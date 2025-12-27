from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Union

from ..core.map import GridMap
from ..core.types import Coord

PathLike = Union[str, Path]


@dataclass(frozen=True, slots=True)
class MovingAIScenarioEntry:
    start: Coord
    goal: Coord
    optimal_length: Optional[float] = None


def load_movingai_map(path: PathLike) -> GridMap:
    """
    Load a MovingAI .map file into a GridMap.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse Header
    # Expected format:
    # type octile
    # height 512
    # width 512
    # map

    header_info = {}
    line_idx = 0

    while line_idx < len(lines):
        line = lines[line_idx]
        if line == "map":
            line_idx += 1
            break

        parts = line.split()
        if len(parts) >= 2:
            key = parts[0]
            val = parts[1]
            header_info[key] = val
        line_idx += 1

    if "height" not in header_info or "width" not in header_info:
        raise ValueError("Invalid MovingAI map: missing height/width in header.")

    height = int(header_info["height"])
    width = int(header_info["width"])

    # Parse Grid
    obstacles: Set[Coord] = set()

    # Process the map rows
    # In file: line 0 is y=0. char 0 is x=0.
    current_y = 0

    while line_idx < len(lines) and current_y < height:
        row_str = lines[line_idx]
        # Safety check for width, though some files might be loose
        length = min(len(row_str), width)

        for x in range(length):
            char = row_str[x]
            # MovingAI conventions:
            # . = passable, G = passable, S = swamp (passable)
            # @ = out of bounds, O = out of bounds
            # T = trees, W = water (usually blocked)
            if char not in ('.', 'G', 'S'):
                obstacles.add((x, current_y))

        current_y += 1
        line_idx += 1

    return GridMap(width=width, height=height, obstacles=obstacles)


def load_movingai_scenarios(path: PathLike) -> List[MovingAIScenarioEntry]:
    """
    Load a MovingAI .scen file into a list of scenario entries.
    """
    path = Path(path)
    entries = []

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("version"):
                continue

            parts = line.split()
            # Format: bucket map width height startx starty goalx goaly optimal
            if len(parts) < 9:
                continue

            try:
                sx, sy = int(parts[4]), int(parts[5])
                gx, gy = int(parts[6]), int(parts[7])
                dist = float(parts[8])
                entries.append(MovingAIScenarioEntry(
                    start=(sx, sy),
                    goal=(gx, gy),
                    optimal_length=dist
                ))
            except ValueError:
                continue

    return entries


def movingai_instance(map_path: PathLike, scen_path: PathLike, index: int) -> GridMap:
    """
    Load a map and apply the start/goal from a specific scenario index.
    """
    base_map = load_movingai_map(map_path)
    scenarios = load_movingai_scenarios(scen_path)

    if index < 0 or index >= len(scenarios):
        raise IndexError(f"Scenario index {index} out of range (0-{len(scenarios) - 1})")

    scen = scenarios[index]

    # Return a new GridMap with the start/goal set
    return GridMap(
        width=base_map.width,
        height=base_map.height,
        obstacles=base_map.obstacles,
        start=scen.start,
        goal=scen.goal
    )