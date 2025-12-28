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


class GreedyBestFirstAlgorithm(PathfindingAlgorithm):
    @property
    def name(self) -> str:
        return "Greedy Best-First (Manhattan)"

    def find_path(self, grid_map: GridMap, *, step_mode: bool):
        if grid_map.start is None or grid_map.goal is None:
            raise ValueError("Greedy Best-First requires both start and goal.")

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
                        log="Start equals goal.",
                        status=SearchStatus.FOUND,
                    )

                return _gen_trivial()
            return [start]

        def _run_steps() -> Iterator[SearchStep]:
            # Priority Queue tuple: (h, tie_breaker, coord)
            # Unlike A*, we do NOT include g_score in the priority.
            open_heap: List[Tuple[int, int, Coord]] = []

            # We track 'visited' (closed) and 'came_from' for path reconstruction
            closed: Set[Coord] = set()
            came_from: Dict[Coord, Coord] = {}

            # To avoid adding duplicates to heap that are already efficient enough,
            # we can track if a node is in open.
            # However, standard Greedy often just pushes. We'll use a set for speed.
            in_open: Set[Coord] = {start}

            tie = 0
            h0 = _manhattan(start, goal)
            heapq.heappush(open_heap, (h0, tie, start))

            while open_heap:
                h_cur, _, current = heapq.heappop(open_heap)
                in_open.discard(current)

                if current in closed:
                    continue

                closed.add(current)

                log_lines: List[str] = [f"Expanding {current} (h={h_cur})."]
                open_added: List[Coord] = []

                if current == goal:
                    path = reconstruct_path(came_from, goal)
                    yield SearchStep(
                        current=current,
                        open_set=list(in_open),  # Snapshot of what's essentially "open"
                        closed_set=sorted(closed),
                        open_added=[],
                        best_path=path,
                        log="\n".join(log_lines + ["Goal reached. Path found."]),
                        status=SearchStatus.FOUND,
                    )
                    return

                for nb in _neighbors_4(current):
                    if not grid_map.in_bound(nb):
                        continue
                    if grid_map.is_blocked(nb):
                        continue
                    if nb in closed:
                        continue
                    if nb in in_open:
                        # Simple Greedy often doesn't update paths if found again because
                        # it doesn't care about optimal 'g'. We skip duplicates.
                        continue

                    came_from[nb] = current
                    h = _manhattan(nb, goal)

                    tie += 1
                    heapq.heappush(open_heap, (h, tie, nb))
                    in_open.add(nb)
                    open_added.append(nb)
                    log_lines.append(f"  Added neighbor {nb}: h={h}")

                # Visualization snapshot
                # We reconstruct path to current to show how we got here
                best_path: Optional[List[Coord]] = [start] if current == start else reconstruct_path(came_from, current)

                yield SearchStep(
                    current=current,
                    open_set=list(in_open),  # Just for visualization
                    closed_set=sorted(closed),
                    open_added=open_added,
                    best_path=best_path,
                    log="\n".join(log_lines),
                    status=SearchStatus.RUNNING,
                )

            # Fail
            yield SearchStep(
                current=start,
                open_set=[],
                closed_set=sorted(closed),
                open_added=[],
                best_path=[start],
                log="Open list exhausted. No path exists.",
                status=SearchStatus.NO_PATH,
            )

        if step_mode:
            return _run_steps()

        final_path: List[Coord] = []
        for step in _run_steps():
            if step.status == SearchStatus.FOUND:
                final_path = list(step.best_path or [])
                break
            if step.status == SearchStatus.NO_PATH:
                final_path = []
                break
        return final_path