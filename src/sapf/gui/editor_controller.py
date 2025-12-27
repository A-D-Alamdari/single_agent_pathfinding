from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Set

from PySide6.QtCore import QObject, Signal, Qt, QEvent
from PySide6.QtGui import QKeyEvent

from ..core.map import GridMap
from ..core.types import Coord


class EditMode(str, Enum):
    START = "START"        # 's'
    GOAL = "GOAL"          # 'e'
    OBSTACLE = "OBSTACLE"  # 'o'
    ERASE = "ERASE"        # 'x'


@dataclass
class EditorState:
    mode: EditMode = EditMode.OBSTACLE


class EditorController(QObject):
    """
    Interactive grid editor controller (s/e/o/x + click).

    - Uses a GridView cellClicked signal to apply edits.
    - Uses an eventFilter on the GridView to capture key presses.

    Safety rules:
      - start/goal cannot be placed on an obstacle
      - obstacles cannot be placed on start/goal
      - all edits generate a NEW GridMap instance (GridMap is frozen)
    """

    mapChanged = Signal(object)       # emits GridMap
    message = Signal(str)             # emits user-facing messages/warnings
    modeChanged = Signal(str)         # emits EditMode value string

    def __init__(self) -> None:
        super().__init__()
        self.state = EditorState()
        self._grid_map: Optional[GridMap] = None
        self._enabled: bool = True

    def set_enabled(self, enabled: bool) -> None:
        """
        Disable editing while algorithm is running, etc.
        """
        self._enabled = bool(enabled)

    def set_map(self, grid_map: Optional[GridMap]) -> None:
        """
        Update the active map being edited (typically after load/reset).
        """
        self._grid_map = grid_map

    def attach_to_view(self, grid_view: QObject) -> None:
        """
        Attach this editor to a GridView-like object that has:
          - a Qt signal: cellClicked(x:int, y:int)
          - supports installEventFilter()
        """
        # Expecting GridView from our GUI package.
        if hasattr(grid_view, "cellClicked"):
            grid_view.cellClicked.connect(self._on_cell_clicked)  # type: ignore[attr-defined]
        else:
            raise TypeError("grid_view must expose a 'cellClicked(int,int)' signal")

        grid_view.installEventFilter(self)

        self._emit_mode()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """
        Capture key presses globally for the GridView.
        """
        if not self._enabled:
            return super().eventFilter(watched, event)

        if event.type() == QEvent.Type.KeyPress:
            ev = event  # QKeyEvent
            assert isinstance(ev, QKeyEvent)

            key = ev.key()
            if key == Qt.Key.Key_S:
                self.state.mode = EditMode.START
                self._emit_mode()
                return True
            if key == Qt.Key.Key_E:
                self.state.mode = EditMode.GOAL
                self._emit_mode()
                return True
            if key == Qt.Key.Key_O:
                self.state.mode = EditMode.OBSTACLE
                self._emit_mode()
                return True
            if key == Qt.Key.Key_X:
                self.state.mode = EditMode.ERASE
                self._emit_mode()
                return True

        return super().eventFilter(watched, event)

    def _emit_mode(self) -> None:
        self.modeChanged.emit(self.state.mode.value)
        self.message.emit(
            f"Edit mode: {self.state.mode.value} "
            f"(keys: s=start, e=goal, o=obstacle, x=erase)"
        )

    def _on_cell_clicked(self, x: int, y: int) -> None:
        if not self._enabled:
            self.message.emit("Editing disabled while run is active.")
            return

        if self._grid_map is None:
            self.message.emit("No map loaded.")
            return

        c: Coord = (int(x), int(y))
        if not self._grid_map.in_bound(c):
            self.message.emit(f"Click out of bounds: {c}")
            return

        new_map = self._apply_edit(self._grid_map, c, self.state.mode)
        if new_map is None:
            # message already emitted
            return

        self._grid_map = new_map
        self.mapChanged.emit(new_map)

    def _apply_edit(self, grid_map: GridMap, c: Coord, mode: EditMode) -> Optional[GridMap]:
        """
        Returns a new GridMap if changed; returns None if rejected/no-op.
        """
        obstacles: Set[Coord] = set(grid_map.obstacles)
        start = grid_map.start
        goal = grid_map.goal

        if mode == EditMode.START:
            if c in obstacles:
                self.message.emit(f"Cannot set START at {c}: cell is an obstacle.")
                return None
            start = c
            self.message.emit(f"Set START = {start}")
        elif mode == EditMode.GOAL:
            if c in obstacles:
                self.message.emit(f"Cannot set GOAL at {c}: cell is an obstacle.")
                return None
            goal = c
            self.message.emit(f"Set GOAL = {goal}")
        elif mode == EditMode.OBSTACLE:
            if c == start or c == goal:
                self.message.emit(f"Cannot place obstacle at {c}: cell is START/GOAL.")
                return None
            if c in obstacles:
                # Optional: toggle behavior (comment out if you want only add)
                self.message.emit(f"Obstacle already present at {c}.")
                return None
            obstacles.add(c)
            self.message.emit(f"Added obstacle at {c}")
        elif mode == EditMode.ERASE:
            changed = False
            if c in obstacles:
                obstacles.remove(c)
                changed = True
                self.message.emit(f"Removed obstacle at {c}")
            if start == c:
                start = None
                changed = True
                self.message.emit(f"Cleared START at {c}")
            if goal == c:
                goal = None
                changed = True
                self.message.emit(f"Cleared GOAL at {c}")
            if not changed:
                self.message.emit(f"Nothing to erase at {c}")
                return None
        else:
            self.message.emit(f"Unsupported edit mode: {mode}")
            return None

        try:
            return GridMap(
                width=grid_map.width,
                height=grid_map.height,
                obstacles=obstacles,
                start=start,
                goal=goal,
            )
        except Exception as e:
            # Defensive: GridMap validation should catch invalid states
            self.message.emit(f"Edit rejected by validation: {e}")
            return None
