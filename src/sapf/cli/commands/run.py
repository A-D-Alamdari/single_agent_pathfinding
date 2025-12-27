from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Optional, Callable

from src.sapf import GridMap
from ...algorithms.base import SearchStatus, SearchStep
from ...algorithms.registry import create_algorithm, get_registry
from ...core.map import GridMap


def add_run_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("run", help="Run a pathfinding algorithm on a map.")
    p.add_argument("--map", type=str, required=True, help="Map file (.json/.pkl/.pickle).")
    p.add_argument(
        "--algo",
        type=str,
        required=True,
        help="Algorithm key (e.g., astar, bfs, dijkstra).",
    )
    p.add_argument(
        "--step",
        type=str,
        default="false",
        help="If true, runs in step mode (still prints summary).",
    )
    p.add_argument(
        "--save-path",
        type=str,
        default=None,
        help="Optional output JSON file to store resulting path.",
    )

    p.set_defaults(func=_run_run)


def _load_map_auto(path: Path) -> GridMap | Callable[..., GridMap]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return GridMap.load_json(path)
    if suffix in {".pkl", ".pickle"}:
        return GridMap.load_pickle(path)
    raise ValueError("Unsupported map extension. Use .json, .pkl, or .pickle.")


def _parse_bool(s: str) -> bool:
    s = str(s).strip().lower()
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: '{s}' (use true/false)")


def _run_run(args: argparse.Namespace) -> int:
    map_path = Path(args.map)
    if not map_path.exists():
        raise FileNotFoundError(f"Map not found: {map_path}")

    grid_map = _load_map_auto(map_path)
    if grid_map.start is None or grid_map.goal is None:
        raise ValueError("Map must define start and goal to run an algorithm.")

    algo_key = str(args.algo).strip().lower()
    algo = create_algorithm(algo_key)

    step_mode = _parse_bool(args.step)
    t0 = time.perf_counter()

    expansions = 0
    status = SearchStatus.NO_PATH
    path = []

    if not step_mode:
        # Direct run
        path = algo.find_path(grid_map, step_mode=False)  # type: ignore[assignment]
        status = SearchStatus.FOUND if path else SearchStatus.NO_PATH
        runtime_ms = (time.perf_counter() - t0) * 1000.0
        expansions = 0  # not available in non-step mode for now
    else:
        # Step mode: consume steps for metrics
        it = algo.find_path(grid_map, step_mode=True)
        last_step: Optional[SearchStep] = None
        for step in it:  # type: ignore[assignment]
            expansions += 1
            last_step = step
            if step.status in (SearchStatus.FOUND, SearchStatus.NO_PATH):
                break

        runtime_ms = (time.perf_counter() - t0) * 1000.0
        if last_step is None:
            status = SearchStatus.NO_PATH
            path = []
        else:
            status = last_step.status
            path = list(last_step.best_path) if last_step.best_path is not None else []

    # Summary
    if status == SearchStatus.FOUND:
        dist = max(0, len(path) - 1)
        print("FOUND")
        print(f"algo: {algo_key}")
        print(f"path length (nodes): {len(path)}")
        print(f"distance (moves): {dist}")
    else:
        print("NO_PATH")
        print(f"algo: {algo_key}")

    print(f"expansions: {expansions}")
    print(f"runtime_ms: {runtime_ms:.1f}")

    # Optional path save
    if args.save_path is not None:
        out_path = Path(args.save_path)
        payload = {"status": status.value, "path": path}
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"saved_path: {out_path}")

    return 0
