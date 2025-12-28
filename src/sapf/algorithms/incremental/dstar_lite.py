from __future__ import annotations

import heapq
from typing import Dict, Iterator, List, Optional, Sequence, Set, Tuple

from ...algorithms.base import PathfindingAlgorithm, SearchStatus, SearchStep
from ...algorithms.utils import reconstruct_path
from ...core.map import GridMap
from ...core.types import Coord


def _manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _neighbors_4(c: Coord) -> Sequence[Coord]:
    x, y = c
    return (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)


class DStarLiteAlgorithm(PathfindingAlgorithm):
    """
    D* Lite Implementation (Basic/Static version).

    In a static context, D* Lite behaves like a Backward A* search.
    It calculates rhs/g values from Goal -> Start.
    """

    @property
    def name(self) -> str:
        return "D* Lite (Incremental)"

    def find_path(self, grid_map: GridMap, *, step_mode: bool):
        if grid_map.start is None or grid_map.goal is None:
            raise ValueError("D* Lite requires both start and goal.")

        # D* Lite searches BACKWARDS from Goal to Start
        start_node = grid_map.start
        goal_node = grid_map.goal

        # --- Data Structures ---
        # g: current consistent cost estimates
        # rhs: one-step lookahead cost estimates
        g: Dict[Coord, float] = {}
        rhs: Dict[Coord, float] = {}

        # Priority Queue: (key1, key2, coord)
        open_queue: List[Tuple[float, float, Coord]] = []
        open_set: Set[Coord] = set()  # For fast lookup

        # Tracking for visualization
        closed_set: Set[Coord] = set()
        # In D*, 'parents' aren't explicitly stored the same way, but we track
        # gradients for visualization purposes.
        came_from: Dict[Coord, Coord] = {}

        # --- Initialization ---
        def get_g(u: Coord) -> float:
            return g.get(u, float('inf'))

        def get_rhs(u: Coord) -> float:
            return rhs.get(u, float('inf'))

        def calculate_key(u: Coord) -> Tuple[float, float]:
            # Key = [min(g, rhs) + h, min(g, rhs)]
            # Note: We use Start as the "heuristic target" because we search backward
            val = min(get_g(u), get_rhs(u))
            return (val + _manhattan(start_node, u), val)

        def update_vertex(u: Coord):
            if u != goal_node:
                # rhs(u) = min over succ(u) of (cost(u, s) + g(s))
                # backward: neighbors are successors
                best_val = float('inf')
                best_parent = None

                for s in _neighbors_4(u):
                    if not grid_map.in_bound(s) or grid_map.is_blocked(s):
                        continue
                    # cost is always 1 for grid
                    val = get_g(s) + 1
                    if val < best_val:
                        best_val = val
                        best_parent = s

                rhs[u] = best_val
                if best_parent:
                    came_from[u] = best_parent

            # Manage Heap
            if u in open_set:
                # In standard python heapq, we can't remove easily.
                # We perform "lazy deletion" by ignoring stale entries in loop.
                pass

            if get_g(u) != get_rhs(u):
                k = calculate_key(u)
                heapq.heappush(open_queue, (k[0], k[1], u))
                open_set.add(u)
            elif u in open_set:
                # Ideally remove from open_set, but lazy handle in loop
                # Just mark it not needing processing by consistency check
                pass

        # Init Goal
        rhs[goal_node] = 0.0
        # Calculate key for goal and push
        k_init = calculate_key(goal_node)
        heapq.heappush(open_queue, (k_init[0], k_init[1], goal_node))
        open_set.add(goal_node)

        # --- Compute Shortest Path Loop ---
        def _run_steps() -> Iterator[SearchStep]:
            while open_queue:
                # Check if we are done:
                # (Start is consistent) AND (Top key >= Start key)
                # But for visualization, we just run until queue empty or start is consistent

                k_top = open_queue[0]  # peek
                k_start = calculate_key(start_node)

                # Standard D* Lite termination condition
                if (k_top[0] >= k_start[0] and k_top[1] >= k_start[1]) and (get_rhs(start_node) == get_g(start_node)):
                    break

                # Pop
                k_old = heapq.heappop(open_queue)
                u = k_old[2]

                if u in open_set:
                    open_set.remove(u)

                # Lazy removal check: if key is outdated, skip
                k_new = calculate_key(u)
                if k_old[0] < k_new[0] or (k_old[0] == k_new[0] and k_old[1] < k_new[1]):
                    continue

                closed_set.add(u)
                log_lines = [f"Processing {u}: g={get_g(u)}, rhs={get_rhs(u)}"]
                open_added = []

                g_u = get_g(u)
                rhs_u = get_rhs(u)

                if g_u > rhs_u:
                    # Overconsistent -> make consistent
                    g[u] = rhs_u
                    # Propagate to neighbors
                    for s in _neighbors_4(u):
                        if grid_map.in_bound(s) and not grid_map.is_blocked(s):
                            update_vertex(s)
                            if s in open_set:
                                open_added.append(s)
                else:
                    # Underconsistent
                    g[u] = float('inf')
                    update_vertex(u)  # Re-insert u
                    if u in open_set: open_added.append(u)

                    for s in _neighbors_4(u):
                        if grid_map.in_bound(s) and not grid_map.is_blocked(s):
                            update_vertex(s)
                            if s in open_set: open_added.append(s)

                # --- Visualization ---
                # Reconstruct Path: Trace forward from Start -> Goal using g-values (Greedy descent)
                # Since we computed cost-to-goal (g), we move to neighbor with min g.
                curr_viz = start_node
                viz_path = [curr_viz]

                # Limit path tracing to avoid infinite loops in early stages
                steps = 0
                while curr_viz != goal_node and steps < (grid_map.width * grid_map.height):
                    best_n = None
                    min_g = float('inf')
                    for n in _neighbors_4(curr_viz):
                        if get_g(n) < min_g:
                            min_g = get_g(n)
                            best_n = n

                    if best_n and min_g < float('inf'):
                        curr_viz = best_n
                        viz_path.append(curr_viz)
                    else:
                        break
                    steps += 1

                status = SearchStatus.RUNNING
                if get_g(start_node) != float('inf'):
                    status = SearchStatus.FOUND  # Technically found, but D* continues optimizing

                yield SearchStep(
                    current=u,
                    open_set=list(open_set),
                    closed_set=sorted(closed_set),
                    open_added=open_added,
                    best_path=viz_path,
                    log="\n".join(log_lines),
                    status=status,
                )

            # Final check
            if get_g(start_node) == float('inf'):
                yield SearchStep(
                    current=start_node,
                    open_set=[],
                    closed_set=sorted(closed_set),
                    open_added=[],
                    best_path=[],
                    log="No path found.",
                    status=SearchStatus.NO_PATH,
                )
            else:
                # Generate final clean path
                final_path = [start_node]
                curr = start_node
                while curr != goal_node:
                    best_n = None
                    min_g = float('inf')
                    for n in _neighbors_4(curr):
                        if get_g(n) < min_g:
                            min_g = get_g(n)
                            best_n = n
                    if best_n:
                        curr = best_n
                        final_path.append(curr)
                    else:
                        break

                yield SearchStep(
                    current=start_node,
                    open_set=[],
                    closed_set=sorted(closed_set),
                    open_added=[],
                    best_path=final_path,
                    log="D* Lite Search Converged.",
                    status=SearchStatus.FOUND,
                )

        if step_mode:
            return _run_steps()

        # Non-step mode
        path = []
        for step in _run_steps():
            if step.status == SearchStatus.FOUND:
                path = step.best_path or []
        return path