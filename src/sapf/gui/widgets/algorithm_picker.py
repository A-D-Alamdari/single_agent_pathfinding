# from __future__ import annotations
#
# from dataclasses import dataclass
# from typing import List, Optional, Sequence
#
# from PySide6.QtCore import Signal
# from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget
#
#
# @dataclass(frozen=True, slots=True)
# class AlgorithmItem:
#     """
#     One algorithm entry for GUI selection.
#
#     key:
#         A stable identifier used by registry/CLI (e.g., "astar", "bfs").
#     display:
#         Human-friendly name shown in the dropdown (e.g., "A* (Manhattan)").
#     """
#     key: str
#     display: str
#
#
# class AlgorithmPicker(QWidget):
#     """
#     A small composite widget around QComboBox to select algorithms.
#
#     Features
#     --------
#     - Accepts a list of (key, display) pairs (or AlgorithmItem)
#     - Emits algorithmChanged(key) when selection changes
#     - Provides convenience methods used by MainWindow
#     """
#
#     algorithmChanged = Signal(str)
#
#     def __init__(
#         self,
#         items: Sequence[tuple[str, str]] | Sequence[AlgorithmItem],
#         *,
#         label: str = "",
#         default_key: Optional[str] = None,
#     ) -> None:
#         super().__init__()
#
#         self._label_text = label
#         self._label = QLabel(label) if label else None
#         self._combo = QComboBox()
#
#         # Normalize input items
#         normalized: List[AlgorithmItem] = []
#         for it in items:
#             if isinstance(it, AlgorithmItem):
#                 normalized.append(it)
#             else:
#                 k, d = it
#                 normalized.append(AlgorithmItem(str(k), str(d)))
#
#         if not normalized:
#             # Keep widget usable; show placeholder
#             self._combo.addItem("No algorithms found", userData="")
#             self._combo.setEnabled(False)
#         else:
#             for item in normalized:
#                 self._combo.addItem(item.display, userData=item.key)
#
#         # Layout
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
#         if self._label is not None:
#             layout.addWidget(self._label)
#         layout.addWidget(self._combo)
#
#         # Signals
#         self._combo.currentIndexChanged.connect(self._on_index_changed)
#
#         # Default selection
#         if default_key is not None:
#             self.set_current_key(default_key)
#
#     # -------------------------
#     # Public API
#     # -------------------------
#     def current_key(self) -> str:
#         """
#         Return the currently selected algorithm key.
#         """
#         data = self._combo.currentData()
#         return str(data) if data is not None else ""
#
#     def set_current_key(self, key: str) -> None:
#         """
#         Select an algorithm by its key.
#
#         If key not found, selection is unchanged.
#         """
#         key = str(key)
#         for i in range(self._combo.count()):
#             if str(self._combo.itemData(i)) == key:
#                 self._combo.setCurrentIndex(i)
#                 return
#
#     def set_enabled(self, enabled: bool) -> None:
#         self._combo.setEnabled(bool(enabled))
#
#     def combo_box(self) -> QComboBox:
#         """
#         Expose the underlying QComboBox for advanced customization if needed.
#         """
#         return self._combo
#
#     # -------------------------
#     # Internal
#     # -------------------------
#     def _on_index_changed(self, _: int) -> None:
#         self.algorithmChanged.emit(self.current_key())


from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget

# Ensure AlgorithmSpec is imported
from ...algorithms.registry import AlgorithmSpec


class AlgorithmPicker(QWidget):
    """
    Cascading Algorithm Selector.

    [ Category Dropdown ] -> [ Algorithm Dropdown ]
    """

    algorithmChanged = Signal(str)

    def __init__(
            self,
            specs: Sequence[AlgorithmSpec],
            *,
            label: str = "",
            default_key: Optional[str] = None,
    ) -> None:
        super().__init__()

        # --- Data Organization ---
        # Group algorithms by category: { "Uninformed": [Spec1, Spec2], ... }
        self._grouped_specs: Dict[str, List[AlgorithmSpec]] = {}
        self._category_order: List[str] = []

        # We preserve the order provided by the registry (which is sorted)
        for spec in specs:
            if spec.category not in self._grouped_specs:
                self._grouped_specs[spec.category] = []
                self._category_order.append(spec.category)
            self._grouped_specs[spec.category].append(spec)

        # --- UI Components ---
        self._label = QLabel(label)

        # Master Dropdown (Categories)
        self._cat_combo = QComboBox()
        self._cat_combo.setFixedWidth(130)  # Optional: Fixed width for neatness
        self._cat_combo.addItems(self._category_order)

        # Detail Dropdown (Specific Algorithms)
        self._algo_combo = QComboBox()
        self._algo_combo.setMinimumWidth(150)  # Ensure readable names

        # --- Layout ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)
        layout.addWidget(self._cat_combo)
        layout.addWidget(self._algo_combo)

        # --- Wiring ---
        # When Category changes -> Update Algorithm list
        self._cat_combo.currentTextChanged.connect(self._on_category_changed)

        # When Algorithm changes -> Emit signal
        self._algo_combo.currentIndexChanged.connect(self._on_algo_changed)

        # --- Initial State ---
        if default_key:
            self.set_current_key(default_key)
        elif self._category_order:
            # Trigger initial population
            self._on_category_changed(self._category_order[0])

    # -------------------------
    # Public API
    # -------------------------
    def current_key(self) -> str:
        """Return the currently selected algorithm key."""
        return str(self._algo_combo.currentData())

    def set_current_key(self, key: str) -> None:
        """
        Intelligently select an algorithm.
        1. Find which category it belongs to.
        2. Set Category combo.
        3. Set Algorithm combo.
        """
        key = str(key)
        target_cat = None
        target_spec = None

        # Search for the spec
        for cat, specs in self._grouped_specs.items():
            for spec in specs:
                if spec.key == key:
                    target_cat = cat
                    target_spec = spec
                    break
            if target_cat:
                break

        if target_cat and target_spec:
            # 1. Block signals to prevent premature events
            self._cat_combo.blockSignals(True)
            self._algo_combo.blockSignals(True)

            # 2. Set Category
            self._cat_combo.setCurrentText(target_cat)

            # 3. Force re-population of algo list for this category
            self._populate_algos(target_cat)

            # 4. Set Algorithm
            idx = self._algo_combo.findData(key)
            if idx >= 0:
                self._algo_combo.setCurrentIndex(idx)

            # 5. Unblock
            self._cat_combo.blockSignals(False)
            self._algo_combo.blockSignals(False)

            # 6. Emit manually since we blocked signals
            self.algorithmChanged.emit(key)

    def set_enabled(self, enabled: bool) -> None:
        self._cat_combo.setEnabled(bool(enabled))
        self._algo_combo.setEnabled(bool(enabled))

    # -------------------------
    # Internal Logic
    # -------------------------
    def _on_category_changed(self, category_name: str) -> None:
        """Re-populate the algorithm dropdown based on selected category."""
        self._populate_algos(category_name)

        # Trigger an update for the first item in the new list
        self._on_algo_changed(self._algo_combo.currentIndex())

    def _populate_algos(self, category_name: str) -> None:
        """Helper to fill the second combobox."""
        self._algo_combo.blockSignals(True)
        self._algo_combo.clear()

        specs = self._grouped_specs.get(category_name, [])
        for spec in specs:
            self._algo_combo.addItem(spec.display, userData=spec.key)

        self._algo_combo.blockSignals(False)

    def _on_algo_changed(self, index: int) -> None:
        key = self._algo_combo.itemData(index)
        if key:
            self.algorithmChanged.emit(str(key))