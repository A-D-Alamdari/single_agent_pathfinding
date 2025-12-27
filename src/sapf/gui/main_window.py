from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .editor_controller import EditorController
from ..algorithms.registry import create_algorithms, list_algorithms_for_gui
from ..core.map import GridMap
from ..gui.grid_view import GridView
from ..gui.run_controller import RunController
from ..gui.widgets.algorithm_picker import AlgorithmPicker
from ..gui.widgets.log_panel import LogPanel
from ..gui.widgets.stats_panel import StatsPanel


@dataclass
class _UiState:
    map_path: Optional[Path] = None
    grid_map: Optional[GridMap] = None


class MainWindow(QMainWindow):
    """
    Main GUI window: map view + panels + controls.

    Features
    --------
    - Load map from JSON / pickle
    - Interactive editing:
        s + click: start
        e + click: goal
        o + click: obstacle
        x + click: erase
    - Algorithm execution:
        Start (animated via QTimer)
        Step (advance one generator step)
        Stop / Reset
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Single-Agent Pathfinding")

        self._ui = _UiState()
        self._algos = create_algorithms()

        # Core widgets
        self.grid_view = GridView()
        self.log_panel = LogPanel()
        self.stats_panel = StatsPanel()

        # Controls
        self.algo_picker = AlgorithmPicker(list_algorithms_for_gui())

        self.btn_load = QPushButton("Load Map")
        self.btn_save = QPushButton("Save Map As…")
        self.btn_start = QPushButton("Start")
        self.btn_step = QPushButton("Step")
        self.btn_stop = QPushButton("Stop")
        self.btn_reset = QPushButton("Reset")

        self.speed_label = QLabel("Speed (ms/step):")
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(10, 2000)
        self.speed_spin.setValue(100)

        self.mode_label = QLabel("Edit mode: OBSTACLE (s/e/o/x)")
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.status_label = QLabel("No map loaded.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Controllers
        self.run_controller = RunController(
            grid_view=self.grid_view,
            log_panel=self.log_panel,
            status_label=self.status_label,
        )
        self.editor = EditorController()

        # Layout + wiring
        self._build_layout()
        self._wire()

        # Attach editor to view
        self.editor.attach_to_view(self.grid_view)
        self.editor.mapChanged.connect(self._on_map_edited)
        self.editor.message.connect(self._on_editor_message)
        self.editor.modeChanged.connect(self._on_mode_changed)

        self._set_controls_enabled(False)

    # -------------------------
    # Layout
    # -------------------------
    def _build_layout(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.btn_load)
        top_bar.addWidget(self.btn_save)
        top_bar.addSpacing(12)

        top_bar.addWidget(QLabel("Algorithm:"))
        top_bar.addWidget(self.algo_picker)
        top_bar.addSpacing(12)

        top_bar.addWidget(self.btn_start)
        top_bar.addWidget(self.btn_step)
        top_bar.addWidget(self.btn_stop)
        top_bar.addWidget(self.btn_reset)
        top_bar.addSpacing(12)

        top_bar.addWidget(self.speed_label)
        top_bar.addWidget(self.speed_spin)
        top_bar.addStretch(1)

        # Right-side panel: stats + log
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.stats_panel)
        right_layout.addWidget(self.log_panel, stretch=1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.grid_view)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout = QVBoxLayout(root)
        layout.addLayout(top_bar)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.status_label)
        layout.addWidget(splitter)

    # -------------------------
    # Wiring
    # -------------------------
    def _wire(self) -> None:
        self.btn_load.clicked.connect(self._on_load_map)
        self.btn_save.clicked.connect(self._on_save_map_as)

        self.btn_start.clicked.connect(self._on_start)
        self.btn_step.clicked.connect(self._on_step)
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_reset.clicked.connect(self._on_reset)

        self.speed_spin.valueChanged.connect(self._on_speed_changed)

    def _set_controls_enabled(self, enabled: bool) -> None:
        self.btn_save.setEnabled(enabled)
        self.btn_start.setEnabled(enabled)
        self.btn_step.setEnabled(enabled)
        self.btn_stop.setEnabled(enabled)
        self.btn_reset.setEnabled(enabled)
        self.algo_picker.setEnabled(enabled)
        self.speed_spin.setEnabled(enabled)

    # -------------------------
    # Map load/save
    # -------------------------
    def _on_load_map(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Open Map",
            "",
            "Map files (*.json *.pkl *.pickle);;All files (*.*)",
        )
        if not path_str:
            return

        path = Path(path_str)
        try:
            if path.suffix.lower() == ".json":
                grid_map = GridMap.load_json(path)
            elif path.suffix.lower() in {".pkl", ".pickle"}:
                grid_map = GridMap.load_pickle(path)
            else:
                raise ValueError("Unsupported extension. Use .json, .pkl, or .pickle.")
        except Exception as e:
            QMessageBox.critical(self, "Failed to Load Map", str(e))
            return

        self._ui.map_path = path
        self._ui.grid_map = grid_map

        # Reset visualization + controllers
        self.run_controller.reset(clear_log=True)
        self.stats_panel.reset()

        self.grid_view.set_map(grid_map)
        self.editor.set_map(grid_map)
        self.editor.set_enabled(True)

        self.status_label.setText(f"Loaded map: {path.name} ({grid_map.width}x{grid_map.height})")
        self._set_controls_enabled(True)

        if grid_map.start is None or grid_map.goal is None:
            self.log_panel.append(
                "Warning: map has no start/goal. Use editor keys (s/e) and click to set them."
            )

    def _on_save_map_as(self) -> None:
        if self._ui.grid_map is None:
            QMessageBox.warning(self, "No Map", "Load or create a map first.")
            return

        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save Map As",
            "",
            "JSON (*.json);;Pickle (*.pkl *.pickle)",
        )
        if not path_str:
            return

        path = Path(path_str)
        try:
            suffix = path.suffix.lower()
            if suffix == ".json":
                self._ui.grid_map.save_json(path)
            elif suffix in {".pkl", ".pickle"}:
                self._ui.grid_map.save_pickle(path)
            else:
                raise ValueError("Unsupported extension. Use .json, .pkl, or .pickle.")
        except Exception as e:
            QMessageBox.critical(self, "Failed to Save Map", str(e))
            return

        self.status_label.setText(f"Saved map: {path.name}")

    # -------------------------
    # Editor callbacks
    # -------------------------
    def _on_map_edited(self, grid_map: GridMap) -> None:
        # Stop any run overlays but keep logs
        self.run_controller.stop()
        self.stats_panel.reset()

        self._ui.grid_map = grid_map
        self.grid_view.set_map(grid_map)
        self.editor.set_map(grid_map)

    def _on_editor_message(self, msg: str) -> None:
        # Log user-facing editor messages (also handy for debugging)
        self.log_panel.append(msg)

    def _on_mode_changed(self, mode_value: str) -> None:
        self.mode_label.setText(f"Edit mode: {mode_value} (s/e/o/x)")

    # -------------------------
    # Run controls
    # -------------------------
    def _on_start(self) -> None:
        if self._ui.grid_map is None:
            QMessageBox.warning(self, "No Map", "Load a map first.")
            return

        if self._ui.grid_map.start is None or self._ui.grid_map.goal is None:
            QMessageBox.warning(
                self,
                "Missing Start/Goal",
                "Please set both start and goal using the editor:\n"
                "Press 's' then click for start, 'e' then click for goal.",
            )
            return

        algo_key = self.algo_picker.current_key()
        algo = self._algos.get(algo_key)
        if algo is None:
            QMessageBox.critical(self, "Algorithm Error", f"Algorithm '{algo_key}' not available.")
            return

        # Disable editing while running
        self.editor.set_enabled(False)

        try:
            self.run_controller.start(
                algo=algo,
                grid_map=self._ui.grid_map,
                interval_ms=int(self.speed_spin.value()),
            )
        except Exception as e:
            self.editor.set_enabled(True)
            QMessageBox.critical(self, "Run Error", str(e))
            return

        self.log_panel.append(f"Run started: {algo.name}")

        # Note: RunController currently does not emit a completion signal.
        # Users can press Stop/Reset to re-enable editing.
        # If you want auto re-enable on completion, add a finished signal in RunController.

    def _on_step(self) -> None:
        if self._ui.grid_map is None:
            QMessageBox.warning(self, "No Map", "Load a map first.")
            return
        if self._ui.grid_map.start is None or self._ui.grid_map.goal is None:
            QMessageBox.warning(self, "Missing Start/Goal", "Set start and goal first (s/e + click).")
            return

        # Disable editing while stepping through an active run
        self.editor.set_enabled(False)

        try:
            self.run_controller.step_once()
        except Exception as e:
            self.editor.set_enabled(True)
            QMessageBox.critical(self, "Step Error", str(e))
            return

    def _on_stop(self) -> None:
        self.run_controller.stop()
        self.editor.set_enabled(True)
        self.status_label.setText("Stopped.")
        self.log_panel.append("Run stopped. Editing enabled.")

    def _on_reset(self) -> None:
        self.run_controller.reset(clear_log=True)
        self.stats_panel.reset()
        self.editor.set_enabled(True)

        if self._ui.grid_map is not None:
            # Re-render base map
            self.grid_view.set_map(self._ui.grid_map)
            self.editor.set_map(self._ui.grid_map)

        self.status_label.setText("Reset.")
        self.log_panel.append("Reset completed. Editing enabled.")

    def _on_speed_changed(self, value: int) -> None:
        self.run_controller.set_interval_ms(int(value))
