from __future__ import annotations

from typing import Dict, Iterator, List, Optional, Sequence, Set

from ...algorithms.base import PathfindingAlgorithm, SearchStatus, SearchStep
from ...algorithms.utils import reconstruct_path
from ...core.map import GridMap
from ...core.types import Coord


def _neighbors_4(c: Coord) -> Sequence[Coord]:
    x, y = c
    return (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)


class DFS4(PathfindingAlgorithm):
    @property
    def name(self) -> str:
        return "DFS (4-neighborhood)"

    def find_path(self, grid_map: GridMap, *, step_mode: bool):
        if grid_map.start is None or grid_map.goal is None:
            raise ValueError("DFS requires both start and goal to be set")

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
                        log="Start equals goal. Trivial path found.",
                        status=SearchStatus.FOUND,
                    )
                return _gen()
            return [start]

        def _run_steps() -> Iterator[SearchStep]:
            stack: List[Coord] = [start]
            in_open: Set[Coord] = {start}
            closed: Set[Coord] = set()
            came_from: Dict[Coord, Coord] = {}

            while stack:
                current = stack.pop()
                in_open.discard(current)

                if current in closed:
                    continue

                closed.add(current)

                log_lines: List[str] = [f"Expanding {current} (DFS)."]
                open_added: List[Coord] = []

                if current == goal:
                    path = reconstruct_path(came_from, goal)
                    yield SearchStep(
                        current=current,
                        open_set=stack.copy(),
                        closed_set=sorted(closed),
                        open_added=[],
                        best_path=path,
                        log="\n".join(log_lines + ["Goal reached by expansion. Path found."]),
                        status=SearchStatus.FOUND,
                    )
                    return

                # For DFS, pushing neighbors in reverse order affects traversal deterministically.
                # Keep it consistent with BFS neighbor order by reversing at push time.
                nbs = list(_neighbors_4(current))
                for nb in reversed(nbs):
                    if not grid_map.in_bound(nb) or grid_map.is_blocked(nb) or nb in closed:
                        continue
                    if nb in in_open:
                        continue
                    came_from[nb] = current
                    stack.append(nb)
                    in_open.add(nb)
                    open_added.append(nb)
                    log_lines.append(f"  Pushed neighbor {nb}.")

                best_path: Optional[List[Coord]] = [start] if current == start else reconstruct_path(came_from, current)

                yield SearchStep(
                    current=current,
                    open_set=stack.copy(),
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
                log="Stack exhausted. No path exists to goal.",
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
