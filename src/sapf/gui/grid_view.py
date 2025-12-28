from __future__ import annotations

from typing import Dict, Optional, Sequence

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsView

from ..algorithms.base import SearchStatus
from ..core.map import GridMap
from ..core.types import Coord
from ..gui.palette import Palette


class GridView(QGraphicsView):
    """
    QGraphicsView grid renderer + click-to-cell detection.
    """

    cellClicked = Signal(int, int)

    CELL_SIZE = 24

    def __init__(self) -> None:
        super().__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._grid_map: Optional[GridMap] = None
        self._cells: Dict[Coord, QGraphicsRectItem] = {}

        self._palette = Palette.default()

    def resizeEvent(self, event) -> None:
        """Auto-fit the map whenever the view is resized."""
        super().resizeEvent(event)
        if self._scene.sceneRect().isValid():
            self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def set_palette(self, palette: Palette) -> None:
        self._palette = palette
        if self._grid_map is not None:
            self.set_map(self._grid_map)

    def set_map(self, grid_map: GridMap) -> None:
        self._grid_map = grid_map
        self._scene.clear()
        self._cells.clear()

        w, h = grid_map.width, grid_map.height

        # --- FIX START: Explicitly set the scene bounds ---
        # This forces the scene to "forget" any previous large map size
        # and shrink/grow exactly to the new map's dimensions.
        total_w = w * self.CELL_SIZE
        total_h = h * self.CELL_SIZE
        self._scene.setSceneRect(0, 0, total_w, total_h)
        # --- FIX END ---

        for y in range(h):
            for x in range(w):
                rect = QRectF(
                    x * self.CELL_SIZE,
                    y * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE,
                )
                item = QGraphicsRectItem(rect)
                item.setPen(self._palette.grid_pen)
                item.setBrush(self._palette.empty)
                self._scene.addItem(item)
                self._cells[(x, y)] = item

        self._apply_base_layer()

        # Reset any previous zoom/transform before fitting
        self.resetTransform()
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def clear_overlays(self) -> None:
        if self._grid_map is None:
            return
        for item in self._cells.values():
            item.setBrush(self._palette.empty)
        self._apply_base_layer()

    def _apply_base_layer(self) -> None:
        if self._grid_map is None:
            return

        for c in self._grid_map.obstacles:
            self._set_cell_brush(c, self._palette.obstacle)

        if self._grid_map.start is not None:
            self._set_cell_brush(self._grid_map.start, self._palette.start)
        if self._grid_map.goal is not None:
            self._set_cell_brush(self._grid_map.goal, self._palette.goal)

    def update_search_state(
            self,
            *,
            open_set: Sequence[Coord],
            closed_set: Sequence[Coord],
            best_path: Optional[Sequence[Coord]],
            current: Coord,
            status: SearchStatus,
    ) -> None:
        if self._grid_map is None:
            return

        self.clear_overlays()

        for c in closed_set:
            if c not in (self._grid_map.start, self._grid_map.goal):
                self._set_cell_brush(c, self._palette.closed_set)

        for c in open_set:
            if c not in (self._grid_map.start, self._grid_map.goal):
                self._set_cell_brush(c, self._palette.open_set)

        if best_path is not None:
            for c in best_path:
                if c not in (self._grid_map.start, self._grid_map.goal):
                    self._set_cell_brush(c, self._palette.path)

        if status == SearchStatus.RUNNING:
            if current not in (self._grid_map.start, self._grid_map.goal):
                self._set_cell_brush(current, self._palette.current)

        if self._grid_map.start is not None:
            self._set_cell_brush(self._grid_map.start, self._palette.start)
        if self._grid_map.goal is not None:
            self._set_cell_brush(self._grid_map.goal, self._palette.goal)

    def mousePressEvent(self, event) -> None:
        self.setFocus(Qt.FocusReason.MouseFocusReason)

        if self._grid_map is None:
            super().mousePressEvent(event)
            return

        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        scene_pos = self.mapToScene(event.pos())
        x = int(scene_pos.x() // self.CELL_SIZE)
        y = int(scene_pos.y() // self.CELL_SIZE)

        if 0 <= x < self._grid_map.width and 0 <= y < self._grid_map.height:
            self.cellClicked.emit(x, y)

        super().mousePressEvent(event)

    def _set_cell_brush(self, c: Coord, brush: QBrush) -> None:
        item = self._cells.get(c)
        if item is not None:
            item.setBrush(brush)
