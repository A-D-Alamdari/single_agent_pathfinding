# src/single_agent_pathfinding/gui/run_controller.py
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterator, Optional

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QLabel

from ..algorithms.base import PathfindingAlgorithm, SearchStatus, SearchStep
from ..core.map import GridMap
from ..gui.grid_view import GridView
from ..gui.widgets.log_panel import LogPanel
from ..gui.widgets.stats_panel import Stats, StatsPanel


@dataclass(frozen=True, slots=True)
class RunMetrics:
    status: SearchStatus
    visited: int
    distance: Optional[int]
    expansions: int
    runtime_ms: float


class RunController(QObject):
    """
    Drives algorithm execution in step-generator mode and updates the UI safely.

    Execution model
    ---------------
    - Algorithms run in *step mode* and return an iterator/generator that yields SearchStep.
    - The controller advances one step per QTimer tick (prevents UI freezing).
    - Also supports manual stepping (Step button), which advances exactly one step.

    UI Updates
    ----------
    - GridView overlays: open set, closed set, the best path, current node highlight.
    - LogPanel: append step.log messages.
    - Status label: live status summary + final summary.
    - Optional StatsPanel: visited, distance, expansions, runtime.

    Signals
    -------
    - finished(metrics): emitted when run reaches FOUND/NO_PATH or iterator ends.
    - started(algo_name): emitted when run starts.
    """

    finished = Signal(object)  # emits RunMetrics
    started = Signal(str)

    def __init__(
        self,
        *,
        grid_view: GridView,
        log_panel: LogPanel,
        status_label: QLabel,
        stats_panel: Optional[StatsPanel] = None,
    ) -> None:
        super().__init__()
        self._grid_view = grid_view
        self._log_panel = log_panel
        self._status_label = status_label
        self._stats_panel = stats_panel

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)

        self._it: Optional[Iterator[SearchStep]] = None
        self._algo_name: str = ""
        self._running: bool = False

        self._interval_ms: int = 100
        self._t0: float = 0.0

        # Metrics (expansions = how many steps processed; visited computed from closed set)
        self._expansions: int = 0
        self._last_step: Optional[SearchStep] = None

    # -------------------------
    # Public control API
    # -------------------------
    def set_interval_ms(self, interval_ms: int) -> None:
        self._interval_ms = max(10, int(interval_ms))
        if self._timer.isActive():
            self._timer.setInterval(self._interval_ms)

    def is_running(self) -> bool:
        return self._timer.isActive() and self._running

    def start(self, *, algo: PathfindingAlgorithm, grid_map: GridMap, interval_ms: int) -> None:
        """
        Start an animated run.
        """
        if grid_map.start is None or grid_map.goal is None:
            raise ValueError("Map must define start and goal before running.")

        self.stop()
        self.set_interval_ms(interval_ms)

        it = algo.find_path(grid_map, step_mode=True)
        # In our contract, step_mode=True must produce an iterator of SearchStep.
        self._it = iter(it)  # type: ignore[arg-type]

        self._algo_name = algo.name
        self._running = True
        self._expansions = 0
        self._last_step = None
        self._t0 = time.perf_counter()

        # Clear overlays (keep base map)
        self._grid_view.clear_overlays()

        self._status_label.setText(f"RUNNING | algo={self._algo_name}")
        if self._stats_panel is not None:
            self._stats_panel.set_stats(Stats(status="RUNNING"))

        self.started.emit(self._algo_name)
        self._timer.start(self._interval_ms)

    def stop(self) -> None:
        """
        Stop animation (does not clear overlays/logs).
        """
        self._timer.stop()
        self._running = False

    def reset(self, *, clear_log: bool) -> None:
        """
        Stop and clear run state and overlays. Optionally clear log.
        """
        self.stop()
        self._it = None
        self._algo_name = ""
        self._expansions = 0
        self._last_step = None
        self._t0 = 0.0

        self._grid_view.clear_overlays()
        if clear_log:
            self._log_panel.clear()
        if self._stats_panel is not None:
            self._stats_panel.reset()

    def step_once(self) -> None:
        """
        Advance exactly one step. If animation is active, it is paused.
        """
        self._timer.stop()
        if self._it is None:
            self._status_label.setText("Step: no active run. Press Start first.")
            return

        self._running = True
        self._advance_one()

    # -------------------------
    # Timer tick
    # -------------------------
    def _on_tick(self) -> None:
        if not self._running or self._it is None:
            return
        self._advance_one()

    # -------------------------
    # Core step advancement
    # -------------------------
    def _advance_one(self) -> None:
        assert self._it is not None

        try:
            step = next(self._it)
        except StopIteration:
            # Generator ended without producing a terminal step.
            if self._last_step is not None:
                self._finish(self._last_step)
            else:
                self._timer.stop()
                self._running = False
                self._status_label.setText("Finished (no steps produced).")
                self.finished.emit(
                    RunMetrics(
                        status=SearchStatus.NO_PATH,
                        visited=0,
                        distance=None,
                        expansions=self._expansions,
                        runtime_ms=self._runtime_ms(),
                    )
                )
            return

        self._last_step = step
        self._expansions += 1

        # Log
        if step.log:
            self._log_panel.append(step.log)

        # Update grid visualization
        self._grid_view.update_search_state(
            open_set=list(step.open_set),
            closed_set=list(step.closed_set),
            best_path=list(step.best_path) if step.best_path is not None else None,
            current=step.current,
            status=step.status,
        )

        # Compute and publish metrics (live)
        metrics = self._compute_metrics(step)
        self._update_labels(metrics)

        if step.status in (SearchStatus.FOUND, SearchStatus.NO_PATH):
            self._finish(step)

    # -------------------------
    # Finalization + metrics
    # -------------------------
    def _runtime_ms(self) -> float:
        if self._t0 <= 0.0:
            return 0.0
        return (time.perf_counter() - self._t0) * 1000.0

    def _compute_metrics(self, step: SearchStep) -> RunMetrics:
        visited = len(step.closed_set)

        distance: Optional[int] = None
        if step.status == SearchStatus.FOUND and step.best_path is not None:
            # Unit-cost grid distance in moves
            distance = max(0, len(step.best_path) - 1)

        return RunMetrics(
            status=step.status,
            visited=visited,
            distance=distance,
            expansions=self._expansions,
            runtime_ms=self._runtime_ms(),
        )

    def _update_labels(self, metrics: RunMetrics) -> None:
        # Keep status label concise but informative
        dist_str = "—" if metrics.distance is None else str(metrics.distance)
        self._status_label.setText(
            f"{metrics.status.value} | visited={metrics.visited} | distance={dist_str} | "
            f"expansions={metrics.expansions} | {metrics.runtime_ms:.1f} ms"
        )

        if self._stats_panel is not None:
            self._stats_panel.set_stats(
                Stats(
                    status=metrics.status.value,
                    visited=metrics.visited,
                    distance=metrics.distance,
                    expansions=metrics.expansions,
                    runtime_ms=metrics.runtime_ms,
                )
            )

    def _finish(self, step: SearchStep) -> None:
        self._timer.stop()
        self._running = False

        metrics = self._compute_metrics(step)
        self._update_labels(metrics)
        self.finished.emit(metrics)
