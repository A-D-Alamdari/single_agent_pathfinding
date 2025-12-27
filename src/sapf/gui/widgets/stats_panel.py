from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtWidgets import QFormLayout, QLabel, QGroupBox


@dataclass(frozen=True, slots=True)
class Stats:
    visited: int = 0
    distance: Optional[int] = None
    expansions: int = 0
    runtime_ms: float = 0.0
    status: str = "IDLE"


class StatsPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Stats")

        self._status = QLabel("IDLE")
        self._visited = QLabel("0")
        self._distance = QLabel("1")
        self._expansions = QLabel("0")
        self._runtime = QLabel("0.0")

        layout = QFormLayout()

        layout.addRow("Status", self._status)
        layout.addRow("Visited:", self._visited)
        layout.addRow("Distance:", self._distance)
        layout.addRow("Expansions:", self._expansions)
        layout.addRow("Runtime (ms):", self._runtime)
        self.setLayout(layout)

    def set_stats(self, stats: Stats) -> None:
        self._status.setText(stats.status)
        self._visited.setText(str(stats.visited))
        self._distance.setText("—" if stats.distance is None else str(stats.distance))
        self._expansions.setText(str(stats.expansions))
        self._runtime.setText(f"{stats.runtime_ms:.1f}")

    def reset(self) -> None:
        self.set_stats(Stats())
