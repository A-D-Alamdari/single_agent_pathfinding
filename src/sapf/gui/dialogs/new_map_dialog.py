# src/sapf/gui/dialogs/new_map_dialog.py
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...core.map import GridMap
from ...generator.presets import empty_grid, random_obstacles_grid, simple_maze_grid


class NewMapDialog(QDialog):
    """
    Dialog to generate a new map using available presets.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Map")
        self.setModal(True)
        self.resize(350, 250)

        self._result_map: Optional[GridMap] = None

        # --- Inputs ---
        self._width_spin = QSpinBox()
        self._width_spin.setRange(5, 200)
        self._width_spin.setValue(20)

        self._height_spin = QSpinBox()
        self._height_spin.setRange(5, 200)
        self._height_spin.setValue(20)

        self._type_combo = QComboBox()
        self._type_combo.addItems(["Empty Grid", "Random Obstacles", "Simple Maze"])

        # Param: Obstacle Ratio (only for Random)
        self._ratio_spin = QDoubleSpinBox()
        self._ratio_spin.setRange(0.0, 1.0)
        self._ratio_spin.setSingleStep(0.05)
        self._ratio_spin.setValue(0.2)

        # --- Layouts ---
        layout = QVBoxLayout(self)

        # 1. Dimensions Group
        grp_dim = QGroupBox("Dimensions")
        form_dim = QFormLayout(grp_dim)
        form_dim.addRow("Width:", self._width_spin)
        form_dim.addRow("Height:", self._height_spin)
        layout.addWidget(grp_dim)

        # 2. Generator Group
        grp_gen = QGroupBox("Generator")
        form_gen = QFormLayout(grp_gen)
        form_gen.addRow("Type:", self._type_combo)
        form_gen.addRow("Obstacle Ratio:", self._ratio_spin)
        layout.addWidget(grp_gen)

        # 3. Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Logic wiring
        self._type_combo.currentIndexChanged.connect(self._update_ui_state)
        self._update_ui_state()

    def get_map(self) -> Optional[GridMap]:
        """Returns the generated map if OK was clicked, else None."""
        return self._result_map

    def _update_ui_state(self) -> None:
        """Enable/disable params based on selected type."""
        is_random = (self._type_combo.currentText() == "Random Obstacles")
        self._ratio_spin.setEnabled(is_random)

    def _on_accept(self) -> None:
        """Generate the map and close."""
        w = self._width_spin.value()
        h = self._height_spin.value()
        gen_type = self._type_combo.currentText()

        try:
            if gen_type == "Empty Grid":
                self._result_map = empty_grid(w, h)
            elif gen_type == "Random Obstacles":
                ratio = self._ratio_spin.value()
                self._result_map = random_obstacles_grid(w, h, obstacle_ratio=ratio)
            elif gen_type == "Simple Maze":
                self._result_map = simple_maze_grid(w, h)
            else:
                # Fallback
                self._result_map = empty_grid(w, h)

            self.accept()
        except Exception as e:
            # Should be rare given our SpinBox ranges, but safe to catch
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Generation Error", str(e))