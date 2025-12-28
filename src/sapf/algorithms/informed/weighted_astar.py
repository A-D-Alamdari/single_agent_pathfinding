from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Sequence, Set, Tuple

from ...algorithms.base import PathfindingAlgorithm, SearchStatus, SearchStep
from ...algorithms.utils import reconstruct_path
from ...core.map import GridMap
from ...core.types import Coord


@dataclass(frozen=True, slots=True)
class _WeightedScore:
    g: int
    h: int
    w: float = 1.5  # The epsilon weight

    @property
    def f(self) -> float:
        return self.g + (self.h * self.w)


def _manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _neighbors_4(c: Coord) -> Sequence[Coord]:
    x, y = c
    return (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)


class WeightedAStarAlgorithm(PathfindingAlgorithm):
    @property
    def name(self) -> str:
        return "Weighted A* (w=1.5)"

    def find_path(self, grid_map: GridMap, *, step_mode: bool):
        if grid_map.start is None or grid_map.goal is None:
            raise ValueError("Weighted A* requires both start and goal.")

        start = grid_map.start
        goal = grid_map.goal
        weight = 1.5  # You can adjust this value to make it greedier

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
            # Heap stores: (f_score, tie_breaker, coord)
            # f_score is float here because of the weight
            open_heap: List[Tuple[float, int, Coord]] = []

            # Map coord -> Score object
            open_best: Dict[Coord, _WeightedScore] = {}

            closed: Set[Coord] = set()
            came_from: Dict[Coord, Coord] = {}
            g_score: Dict[Coord, int] = {start: 0}

            tie = 0
            h0 = _manhattan(start, goal)
            start_score = _WeightedScore(g=0, h=h0, w=weight)

            open_best[start] = start_score
            heapq.heappush(open_heap, (start_score.f, tie, start))

            while open_heap:
                f_cur, _, current = heapq.heappop(open_heap)

                if current in closed:
                    continue
                if current not in open_best:
                    continue

                # Check for stale entries in heap
                # Note: floating point comparison might need tolerance, but usually safe here
                cur_score_obj = open_best[current]
                if cur_score_obj.f != f_cur:
                    continue

                closed.add(current)
                open_best.pop(current, None)

                log_lines: List[str] = [
                    f"Expanding {current}: g={cur_score_obj.g}, h={cur_score_obj.h}, f={cur_score_obj.f:.1f}"
                ]
                open_added: List[Coord] = []

                if current == goal:
                    path = reconstruct_path(came_from, goal)
                    yield SearchStep(
                        current=current,
                        open_set=sorted(open_best.keys(), key=lambda c: (open_best[c].f, open_best[c].h)),
                        closed_set=sorted(closed),
                        open_added=[],
                        best_path=path,
                        log="\n".join(log_lines + ["Goal reached. Path found."]),
                        status=SearchStatus.FOUND,
                    )
                    return

                for nb in _neighbors_4(current):
                    if not grid_map.in_bound(nb) or grid_map.is_blocked(nb) or nb in closed:
                        continue

                    tentative_g = cur_score_obj.g + 1
                    prev_g = g_score.get(nb)

                    if prev_g is None or tentative_g < prev_g:
                        g_score[nb] = tentative_g
                        came_from[nb] = current
                        h = _manhattan(nb, goal)

                        new_score = _WeightedScore(g=tentative_g, h=h, w=weight)
                        open_best[nb] = new_score

                        tie += 1
                        heapq.heappush(open_heap, (new_score.f, tie, nb))
                        open_added.append(nb)

                        log_msg = f"  Neighbor {nb}: g={tentative_g}, h={h}, f={new_score.f:.1f}"
                        log_lines.append(log_msg)

                # Prepare visualization
                open_snapshot = sorted(open_best.keys(), key=lambda c: (open_best[c].f, open_best[c].h))
                best_path: Optional[List[Coord]] = None
                if current in came_from or current == start:
                    best_path = reconstruct_path(came_from, current) if current != start else [start]

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