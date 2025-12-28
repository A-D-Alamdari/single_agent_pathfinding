# src/single_agent_pathfinding/algorithms/dijkstra.py
from __future__ import annotations

import heapq
from typing import Dict, Iterator, List, Optional, Sequence, Set, Tuple

from ...algorithms.base import PathfindingAlgorithm, SearchStatus, SearchStep
from ...algorithms.utils import reconstruct_path
from ...core.map import GridMap
from ...core.types import Coord


def _neighbors_4(c: Coord) -> Sequence[Coord]:
    x, y = c
    return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))


class Dijkstra4(PathfindingAlgorithm):
    @property
    def name(self) -> str:
        return "Dijkstra (4-neighborhood)"

    def find_path(self, grid_map: GridMap, *, step_mode: bool):
        if grid_map.start is None or grid_map.goal is None:
            raise ValueError("Dijkstra requires both start and goal to be set")

        start = grid_map.start
        goal = grid_map.goal

        if start == goal:
            if step_mode:
                def _gen() -> Iterator[SearchStep]:
                    yield SearchStep(
                        current=start,
                        open_set=[start],
                        closed_set=[],
                        open_added=[start],
                        best_path=[start],
                        log="Start equals goal. Trivial path found (cost=0).",
                        status=SearchStatus.FOUND,
                    )
                return _gen()
            return [start]

        def _run_steps() -> Iterator[SearchStep]:
            open_heap: List[Tuple[int, int, Coord]] = []
            open_g: Dict[Coord, int] = {start: 0}
            closed: Set[Coord] = set()
            came_from: Dict[Coord, Coord] = {}

            tie = 0
            heapq.heappush(open_heap, (0, tie, start))

            while open_heap:
                g_cur, _, current = heapq.heappop(open_heap)

                if current in closed:
                    continue
                # Skip stale entries
                if open_g.get(current, None) != g_cur:
                    continue

                closed.add(current)
                open_g.pop(current, None)

                log_lines: List[str] = [f"Expanding {current} (Dijkstra): g={g_cur}."]
                open_added: List[Coord] = []

                if current == goal:
                    path = reconstruct_path(came_from, goal)
                    yield SearchStep(
                        current=current,
                        open_set=sorted(open_g.keys(), key=lambda c: (open_g[c], c)),
                        closed_set=sorted(closed),
                        open_added=[],
                        best_path=path,
                        log="\n".join(log_lines + ["Goal reached by expansion. Path found."]),
                        status=SearchStatus.FOUND,
                    )
                    return

                for nb in _neighbors_4(current):
                    if not grid_map.in_bound(nb) or grid_map.is_blocked(nb) or nb in closed:
                        continue
                    tentative = g_cur + 1
                    prev = open_g.get(nb)
                    if prev is None or tentative < prev:
                        came_from[nb] = current
                        open_g[nb] = tentative
                        tie += 1
                        heapq.heappush(open_heap, (tentative, tie, nb))
                        open_added.append(nb)
                        if prev is None:
                            log_lines.append(f"  Added neighbor {nb}: g={tentative}.")
                        else:
                            log_lines.append(f"  Updated neighbor {nb}: g {prev}->{tentative}.")

                open_snapshot = sorted(open_g.keys(), key=lambda c: (open_g[c], c))
                best_path: Optional[List[Coord]] = [start] if current == start else reconstruct_path(came_from, current)

                yield SearchStep(
                    current=current,
                    open_set=open_snapshot,
                    closed_set=sorted(closed),
                    open_added=open_added,
                    best_path=best_path,
                    log="\n".join(log_lines),
                    status=SearchStatus.RUNNING,
                )

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

        final: List[Coord] = []
        for step in _run_steps():
            if step.status == SearchStatus.FOUND:
                final = list(step.best_path or [])
                break
            if step.status == SearchStatus.NO_PATH:
                final = []
                break
        return final
