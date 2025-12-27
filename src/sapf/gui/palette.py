from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QPen


@dataclass(frozen=True, slots=True)
class Palette:
    # Cell fills
    empty: QBrush
    obstacle: QBrush
    start: QBrush
    goal: QBrush
    open_set: QBrush
    closed_set: QBrush
    path: QBrush
    current: QBrush

    # Grid line
    grid_pen: QPen

    @staticmethod
    def default() -> Palette:
        grid_pen = QPen(Qt.GlobalColor.gray)
        grid_pen.setWidth(1)

        return Palette(
            empty=QBrush(Qt.GlobalColor.white),
            obstacle=QBrush(Qt.GlobalColor.darkGray),
            start=QBrush(Qt.GlobalColor.green),
            goal=QBrush(Qt.GlobalColor.red),
            open_set=QBrush(Qt.GlobalColor.cyan),  # blue-ish
            closed_set=QBrush(Qt.GlobalColor.lightGray),  # gray-ish
            path=QBrush(Qt.GlobalColor.yellow),  # yellow-ish
            current=QBrush(Qt.GlobalColor.magenta),  # highlight
            grid_pen=grid_pen,
        )

