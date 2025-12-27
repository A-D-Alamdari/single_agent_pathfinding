from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Iterable, Optional, Set, Tuple

from ...core.map import GridMap
from ...core.types import Coord


def _parse_coord(s: str) -> Coord:
    """
    Parse "x,y" into (x,y).
    """
    parts = s.split(",")
    if len(parts) != 2:
        raise ValueError(f"Invalid coordinate '{s}'. Expected format: x,y")
    x = int(parts[0].strip())
    y = int(parts[1].strip())
    return (x, y)


def _random_obstacles(
    width: int,
    height: int,
    *,
    count: int,
    seed: Optional[int],
    reserved: Set[Coord],
) -> Set[Coord]:
    rng = random.Random(seed)
    candidates = [(x, y) for y in range(height) for x in range(width) if (x, y) not in reserved]
    if count > len(candidates):
        raise ValueError(f"Requested {count} obstacles, but only {len(candidates)} free cells exist.")
    chosen = set(rng.sample(candidates, count))
    return chosen


def add_generate_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "generate",
        help="Generate a grid map and save it (JSON or pickle by extension).",
    )
    p.add_argument("--width", type=int, required=True, help="Grid width (columns).")
    p.add_argument("--height", type=int, required=True, help="Grid height (rows).")
    p.add_argument("--start", type=str, required=True, help='Start coordinate "x,y".')
    p.add_argument("--goal", type=str, required=True, help='Goal coordinate "x,y".')

    p.add_argument(
        "--obstacle",
        action="append",
        default=[],
        help='Obstacle coordinate "x,y". Can be repeated.',
    )

    p.add_argument(
        "--random-obstacles",
        type=int,
        default=0,
        help="Number of random obstacles to add (excludes start/goal).",
    )
    p.add_argument("--seed", type=int, default=None, help="Seed for random obstacle generator.")

    p.add_argument(
        "--out",
        type=str,
        required=True,
        help="Output path (.json, .pkl, .pickle).",
    )

    p.set_defaults(func=_run_generate)


def _run_generate(args: argparse.Namespace) -> int:
    width = int(args.width)
    height = int(args.height)
    start = _parse_coord(args.start)
    goal = _parse_coord(args.goal)

    obstacles: Set[Coord] = set(_parse_coord(s) for s in (args.obstacle or []))

    reserved = {start, goal} | obstacles
    rand_n = int(args.random_obstacles)
    if rand_n > 0:
        obstacles |= _random_obstacles(width, height, count=rand_n, seed=args.seed, reserved=reserved)

    grid_map = GridMap(width=width, height=height, obstacles=obstacles, start=start, goal=goal)

    out = Path(args.out)
    suffix = out.suffix.lower()
    if suffix == ".json":
        grid_map.save_json(out)
    elif suffix in {".pkl", ".pickle"}:
        grid_map.save_pickle(out)
    else:
        raise ValueError("Unsupported output extension. Use .json, .pkl, or .pickle.")

    print(f"Saved map: {out} ({width}x{height}), obstacles={len(obstacles)}")
    return 0
