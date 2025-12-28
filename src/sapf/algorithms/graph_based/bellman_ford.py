from __future__ import annotations

from typing import Dict, Iterator, List, Optional, Sequence, Tuple

from ...algorithms.base import PathfindingAlgorithm, SearchStatus, SearchStep
from ...algorithms.utils import reconstruct_path
from ...core.map import GridMap
from ...core.types import Coord


def _neighbors_4(c: Coord) -> Sequence[Coord]:
    x, y = c
    return (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)


class BellmanFordAlgorithm(PathfindingAlgorithm):
    @property
    def name(self) -> str:
        return "Bellman-Ford"

    def find_path(self, grid_map: GridMap, *, step_mode: bool):
        if grid_map.start is None or grid_map.goal is None:
            raise ValueError("Bellman-Ford requires both start and goal.")

        start = grid_map.start
        goal = grid_map.goal

        # Bellman-Ford Setup
        # Initialize distances to infinity, start to 0
        dist: Dict[Coord, float] = {}
        came_from: Dict[Coord, Coord] = {}

        # We need to iterate over all valid nodes in the grid
        # For a grid, V = width * height (minus obstacles)
        all_nodes: List[Coord] = []
        for y in range(grid_map.height):
            for x in range(grid_map.width):
                c = (x, y)
                if not grid_map.is_blocked(c):
                    all_nodes.append(c)
                    dist[c] = float('inf')

        dist[start] = 0

        # Max iterations = |V| - 1
        max_iterations = len(all_nodes) - 1

        def _run_steps() -> Iterator[SearchStep]:
            for i in range(max_iterations):
                changed = False
                updated_nodes: List[Coord] = []

                # Iterate over ALL edges (u -> v)
                # In a grid, this means iterating all nodes u, then their neighbors v
                for u in all_nodes:
                    if dist[u] == float('inf'):
                        continue

                    for v in _neighbors_4(u):
                        if not grid_map.in_bound(v) or grid_map.is_blocked(v):
                            continue

                        # Relaxation step:
                        # Weight is always 1 in this grid
                        new_dist = dist[u] + 1
                        if new_dist < dist[v]:
                            dist[v] = new_dist
                            came_from[v] = u
                            changed = True
                            updated_nodes.append(v)

                # Visualization Logic
                # open_set -> Nodes updated in this pass (Green/Active)
                # closed_set -> All nodes with finite distance (Visited)
                visited_nodes = [n for n in all_nodes if dist[n] != float('inf')]

                current_path = []
                if goal in came_from:
                    current_path = reconstruct_path(came_from, goal)

                status = SearchStatus.RUNNING
                log_msg = f"Iteration {i + 1}/{max_iterations}. Updated {len(updated_nodes)} nodes."

                if not changed:
                    # OPTIMIZATION: Early exit if no changes occurred
                    log_msg = "Converged early (no changes). Path found."
                    status = SearchStatus.FOUND if dist[goal] != float('inf') else SearchStatus.NO_PATH
                elif i == max_iterations - 1:
                    # Final iteration check
                    if dist[goal] != float('inf'):
                        status = SearchStatus.FOUND
                        log_msg = "Max iterations reached. Path found."
                    else:
                        status = SearchStatus.NO_PATH
                        log_msg = "Max iterations reached. Goal unreachable."

                yield SearchStep(
                    current=start,  # Bellman-Ford doesn't have a single "current" node, keep start
                    open_set=updated_nodes,
                    closed_set=visited_nodes,
                    open_added=[],
                    best_path=current_path,
                    log=log_msg,
                    status=status
                )

                if not changed:
                    break

        if step_mode:
            return _run_steps()

        # Non-step mode
        path = []
        for step in _run_steps():
            if step.status == SearchStatus.FOUND:
                path = step.best_path or []
        return path