from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

from ...core.map import GridMap


def add_validate_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("validate", help="Validate a map file (JSON/pickle).")
    p.add_argument("--map", type=str, required=True, help="Path to map (.json/.pkl/.pickle).")
    p.set_defaults(func=_run_validate)


def _load_map_auto(path: Path) -> GridMap | Callable[..., GridMap]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return GridMap.load_json(path)
    if suffix in {".pkl", ".pickle"}:
        return GridMap.load_pickle(path)
    raise ValueError("Unsupported map extension. Use .json, .pkl, or .pickle.")


def _run_validate(args: argparse.Namespace) -> int:
    path = Path(args.map)
    if not path.exists():
        raise FileNotFoundError(f"Map not found: {path}")

    grid_map = _load_map_auto(path)

    # If we got here, validation passed (GridMap ctor/load enforces invariants)
    print("OK")
    print(f"Map: {path.name}")
    print(f"Size: {grid_map.width}x{grid_map.height}")
    print(f"Start: {grid_map.start}")
    print(f"Goal: {grid_map.goal}")
    print(f"Obstacles: {len(grid_map.obstacles)}")
    return 0
