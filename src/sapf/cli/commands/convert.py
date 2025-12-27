from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

from ...core.map import GridMap


def add_convert_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("convert", help="Convert map file between JSON and pickle.")
    p.add_argument("--in", dest="inp", type=str, required=True, help="Input map (.json/.pkl/.pickle).")
    p.add_argument("--out", type=str, required=True, help="Output map (.json/.pkl/.pickle).")
    p.set_defaults(func=_run_convert)


def _load_map_auto(path: Path) -> GridMap | Callable[..., GridMap]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return GridMap.load_json(path)
    if suffix in {".pkl", ".pickle"}:
        return GridMap.load_pickle(path)
    raise ValueError("Unsupported input extension. Use .json, .pkl, or .pickle.")


def _save_map_auto(grid_map: GridMap, path: Path) -> None:
    suffix = path.suffix.lower()
    if suffix == ".json":
        grid_map.save_json(path)
        return
    if suffix in {".pkl", ".pickle"}:
        grid_map.save_pickle(path)
        return
    raise ValueError("Unsupported output extension. Use .json, .pkl, or .pickle.")


def _run_convert(args: argparse.Namespace) -> int:
    inp = Path(args.inp)
    out = Path(args.out)

    if not inp.exists():
        raise FileNotFoundError(f"Input map not found: {inp}")

    grid_map = _load_map_auto(inp)
    _save_map_auto(grid_map, out)

    print(f"Converted: {inp} -> {out}")
    return 0
