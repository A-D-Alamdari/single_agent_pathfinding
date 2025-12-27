# tests/test_step_interface.py
from __future__ import annotations

from typing import Iterator, List, Sequence

import pytest

from src.sapf.algorithms.base import PathfindingAlgorithm, SearchStatus, SearchStep
from src.sapf.algorithms.utils import reconstruct_path, reconstruct_path_if_reachable
from src.sapf.core.map import GridMap
from src.sapf.core.types import Coord


class DummyTwoStepAlgorithm(PathfindingAlgorithm):
    """
    A deterministic dummy algorithm used ONLY for validating the step-by-step interface.
    It does not implement real search; it emits consistent, contract-compliant snapshots.
    """

    @property
    def name(self) -> str:
        return "DummyTwoStep"

    def find_path(self, grid_map: GridMap, *, step_mode: bool):
        if grid_map.start is None or grid_map.goal is None:
            raise ValueError("DummyTwoStepAlgorithm requires start and goal")

        if not step_mode:
            # Minimal "solution": return direct path if adjacent (for test), else empty.
            sx, sy = grid_map.start
            gx, gy = grid_map.goal
            if abs(sx - gx) + abs(sy - gy) == 1 and grid_map.goal not in grid_map.obstacles:
                return [grid_map.start, grid_map.goal]
            return []

        def gen() -> Iterator[SearchStep]:
            start = grid_map.start  # type: ignore[assignment]
            goal = grid_map.goal  # type: ignore[assignment]
            assert start is not None and goal is not None

            # Step 1: initialize
            open_set = [start]
            closed_set: list[Coord] = []
            came_from = {}

            yield SearchStep(
                current=start,
                open_set=open_set.copy(),
                closed_set=closed_set.copy(),
                open_added=[start],
                best_path=[start],
                log="Initialized frontier with start.",
                status=SearchStatus.RUNNING,
            )

            # Step 2: "expand" start, "discover" goal (if not blocked)
            closed_set.append(start)
            if goal in grid_map.obstacles:
                yield SearchStep(
                    current=start,
                    open_set=[],
                    closed_set=closed_set.copy(),
                    open_added=[],
                    best_path=[start],
                    log="Goal is blocked; no path.",
                    status=SearchStatus.NO_PATH,
                )
                return

            came_from[goal] = start
            open_set = [goal]
            best_path = reconstruct_path(came_from, goal)

            yield SearchStep(
                current=goal,
                open_set=open_set.copy(),
                closed_set=closed_set.copy(),
                open_added=[goal],
                best_path=best_path,
                log="Goal discovered.",
                status=SearchStatus.FOUND,
            )

        return gen()


def _assert_step_invariants(steps: Sequence[SearchStep]) -> None:
    assert len(steps) >= 1

    # Basic invariants applicable to most searches:
    # - closed_set should be unique (no duplicates)
    # - open_set should be unique (no duplicates) for set-based algorithms (we enforce in dummy)
    # - current should be present in open_set or closed_set (depending on when snapshot taken)
    for s in steps:
        assert len(set(s.closed_set)) == len(s.closed_set)
        assert len(set(s.open_set)) == len(s.open_set)
        assert s.current in set(s.open_set) | set(s.closed_set)

    # Monotonicity: closed_set should not shrink over time (common search invariant)
    for prev, nxt in zip(steps, steps[1:]):
        assert set(prev.closed_set).issubset(set(nxt.closed_set))


def test_reconstruct_path_basic() -> None:
    came_from = {(1, 0): (0, 0), (2, 0): (1, 0)}
    assert reconstruct_path(came_from, (2, 0)) == [(0, 0), (1, 0), (2, 0)]


def test_reconstruct_path_cycle_detection() -> None:
    came_from = {(1, 0): (0, 0), (0, 0): (1, 0)}
    with pytest.raises(ValueError):
        reconstruct_path(came_from, (1, 0))


def test_reconstruct_path_if_reachable_none_when_goal_missing() -> None:
    came_from = {(1, 0): (0, 0)}
    assert reconstruct_path_if_reachable(came_from, start=(0, 0), goal=(2, 0)) is None


def test_step_generator_consistency_found_tiny_map() -> None:
    m = GridMap(width=2, height=1, start=(0, 0), goal=(1, 0), obstacles=set())
    algo = DummyTwoStepAlgorithm()

    it = algo.find_path(m, step_mode=True)
    assert hasattr(it, "__iter__")

    steps = list(it)  # type: ignore[arg-type]
    assert len(steps) == 2

    # Step 1 expectations
    s0 = steps[0]
    assert s0.status == SearchStatus.RUNNING
    assert s0.current == (0, 0)
    assert list(s0.open_set) == [(0, 0)]
    assert list(s0.closed_set) == []
    assert s0.best_path == [(0, 0)]
    assert isinstance(s0.log, str) and s0.log

    # Step 2 expectations
    s1 = steps[1]
    assert s1.status == SearchStatus.FOUND
    assert s1.current == (1, 0)
    assert list(s1.open_set) == [(1, 0)]
    assert set(s1.closed_set) == {(0, 0)}
    assert s1.best_path == [(0, 0), (1, 0)]
    assert isinstance(s1.log, str) and s1.log

    _assert_step_invariants(steps)


def test_step_generator_consistency_no_path_when_goal_blocked() -> None:
    m = GridMap(width=2, height=1, start=(0, 0), goal=(1, 0), obstacles={(1, 0)})
    algo = DummyTwoStepAlgorithm()

    steps = list(algo.find_path(m, step_mode=True))  # type: ignore[arg-type]
    assert len(steps) == 2
    assert steps[-1].status == SearchStatus.NO_PATH

    _assert_step_invariants(steps)
