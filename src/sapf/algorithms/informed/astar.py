from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Sequence, Set, Tuple

# FIXED: Ensure SearchStep/SearchStatus are imported from the base (which gets them from core)
from ...algorithms.base import PathfindingAlgorithm, SearchStatus, SearchStep
from ...algorithms.utils import reconstruct_path
from ...core.map import GridMap
from ...core.types import Coord


@dataclass(frozen=True, slots=True)
class _Score:
    g: int
    h: int

    @property
    def f(self) -> int:
        return self.g + self.h


def _manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _neighbors_4(c: Coord) -> Sequence[Coord]:
    x, y = c
    return (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)


# FIXED: Renamed class to match registry expectation (was AStarManhattan4)
class AStarAlgorithm(PathfindingAlgorithm):
    @property
    def name(self) -> str:
        return "A* (4-neighborhood, Manhattan)"

    def find_path(self, grid_map: GridMap, *, step_mode: bool):
        if grid_map.start is None or grid_map.goal is None:
            raise ValueError("A* requires both start and goal to be set")

        start = grid_map.start
        goal = grid_map.goal

        if start == goal:
            if step_mode:
                def _gen_trivial() -> Iterator[SearchStep]:
                    yield SearchStep(
                        current=start,
                        open_set=[start],
                        closed_set=[],
                        open_added=[start],
                        best_path=[start],
                        log="Start equals goal. Trivial path found (cost=0).",
                        status=SearchStatus.FOUND,
                    )
                return _gen_trivial()
            return [start]

        def _run_steps() -> Iterator[SearchStep]:
            open_heap: List[Tuple[int, int, Coord]] = []
            open_best: Dict[Coord, _Score] = {}
            closed: Set[Coord] = set()

            came_from: Dict[Coord, Coord] = {}
            g_score: Dict[Coord, int] = {start: 0}

            tie = 0
            h0 = _manhattan(start, goal)
            open_best[start] = _Score(g=0, h=h0)
            heapq.heappush(open_heap, (h0, tie, start))

            # Core A*: yield snapshots after *expanding* a node and pushing neighbors.
            while open_heap:
                f_cur, _, current = heapq.heappop(open_heap)

                # Skip stale heap entries
                if current in closed:
                    continue
                if current not in open_best:
                    continue

                cur_score = open_best[current]
                if cur_score.f != f_cur:
                    # Another stale entry (updated later)
                    continue

                # Expand
                closed.add(current)
                open_best.pop(current, None)

                log_lines: List[str] = []
                log_lines.append(
                    f"Expanding {current}: g={cur_score.g}, h={cur_score.h}, f={cur_score.f}."
                )

                open_added: List[Coord] = []
                for nb in _neighbors_4(current):
                    if not grid_map.in_bound(nb):
                        continue
                    if grid_map.is_blocked(nb):
                        continue
                    if nb in closed:
                        continue

                    tentative_g = cur_score.g + 1
                    prev_g = g_score.get(nb)

                    if prev_g is None or tentative_g < prev_g:
                        g_score[nb] = tentative_g
                        came_from[nb] = current
                        h = _manhattan(nb, goal)
                        open_best[nb] = _Score(g=tentative_g, h=h)
                        tie += 1
                        heapq.heappush(open_heap, (tentative_g + h, tie, nb))
                        open_added.append(nb)

                        if prev_g is None:
                            log_lines.append(
                                f"  Added neighbor {nb}: g={tentative_g}, h={h}, f={tentative_g + h}."
                            )
                        else:
                            log_lines.append(
                                f"  Updated neighbor {nb}: g {prev_g}->{tentative_g}, h={h}, f={tentative_g + h}."
                            )

                # Construct snapshots for GUI
                open_snapshot = sorted(open_best.keys(), key=lambda c: (open_best[c].f, open_best[c].h, c))
                closed_snapshot = sorted(closed)
                best_path: Optional[List[Coord]] = None
                if current in came_from or current == start:
                    # For visualization: path to current (not necessarily to goal).
                    best_path = reconstruct_path(came_from, current) if current != start else [start]

                status = SearchStatus.RUNNING
                if current == goal:
                    # If the goal is expanded, we have a valid optimal path under standard A* assumptions.
                    best_path = reconstruct_path(came_from, goal)
                    status = SearchStatus.FOUND
                    log_lines.append("Goal reached by expansion. Path found.")
                elif goal in open_best:
                    # Optionally show current best-known path to goal if it already has a parent chain.
                    if goal in came_from:
                        best_path = reconstruct_path(came_from, goal)

                yield SearchStep(
                    current=current,
                    open_set=open_snapshot,
                    closed_set=closed_snapshot,
                    open_added=open_added if open_added else [],
                    best_path=best_path,
                    log="\n".join(log_lines),
                    status=status,
                )

                if status == SearchStatus.FOUND:
                    return

            # If we exit loop: no path
            yield SearchStep(
                current=start,
                open_set=[],
                closed_set=sorted(closed),
                open_added=[],
                best_path=[start],
                log="Open list exhausted. No path exists to goal.",
                status=SearchStatus.NO_PATH,
            )

        if step_mode:
            return _run_steps()

        # Non-step mode: run A* to completion and return final path (or empty)
        final_path: List[Coord] = []
        for step in _run_steps():
            if step.status == SearchStatus.FOUND:
                final_path = list(step.best_path or [])
                break
            if step.status == SearchStatus.NO_PATH:
                final_path = []
                break
        return final_path