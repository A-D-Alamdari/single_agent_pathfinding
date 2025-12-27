from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget


@dataclass(frozen=True, slots=True)
class AlgorithmItem:
    """
    One algorithm entry for GUI selection.

    key:
        A stable identifier used by registry/CLI (e.g., "astar", "bfs").
    display:
        Human-friendly name shown in the dropdown (e.g., "A* (Manhattan)").
    """
    key: str
    display: str


class AlgorithmPicker(QWidget):
    """
    A small composite widget around QComboBox to select algorithms.

    Features
    --------
    - Accepts a list of (key, display) pairs (or AlgorithmItem)
    - Emits algorithmChanged(key) when selection changes
    - Provides convenience methods used by MainWindow
    """

    algorithmChanged = Signal(str)

    def __init__(
        self,
        items: Sequence[tuple[str, str]] | Sequence[AlgorithmItem],
        *,
        label: str = "",
        default_key: Optional[str] = None,
    ) -> None:
        super().__init__()

        self._label_text = label
        self._label = QLabel(label) if label else None
        self._combo = QComboBox()

        # Normalize input items
        normalized: List[AlgorithmItem] = []
        for it in items:
            if isinstance(it, AlgorithmItem):
                normalized.append(it)
            else:
                k, d = it
                normalized.append(AlgorithmItem(str(k), str(d)))

        if not normalized:
            # Keep widget usable; show placeholder
            self._combo.addItem("No algorithms found", userData="")
            self._combo.setEnabled(False)
        else:
            for item in normalized:
                self._combo.addItem(item.display, userData=item.key)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        if self._label is not None:
            layout.addWidget(self._label)
        layout.addWidget(self._combo)

        # Signals
        self._combo.currentIndexChanged.connect(self._on_index_changed)

        # Default selection
        if default_key is not None:
            self.set_current_key(default_key)

    # -------------------------
    # Public API
    # -------------------------
    def current_key(self) -> str:
        """
        Return the currently selected algorithm key.
        """
        data = self._combo.currentData()
        return str(data) if data is not None else ""

    def set_current_key(self, key: str) -> None:
        """
        Select an algorithm by its key.

        If key not found, selection is unchanged.
        """
        key = str(key)
        for i in range(self._combo.count()):
            if str(self._combo.itemData(i)) == key:
                self._combo.setCurrentIndex(i)
                return

    def set_enabled(self, enabled: bool) -> None:
        self._combo.setEnabled(bool(enabled))

    def combo_box(self) -> QComboBox:
        """
        Expose the underlying QComboBox for advanced customization if needed.
        """
        return self._combo

    # -------------------------
    # Internal
    # -------------------------
    def _on_index_changed(self, _: int) -> None:
        self.algorithmChanged.emit(self.current_key())