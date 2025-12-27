from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, cast

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True, slots=True)
class LogPanelConfig:
    """
    Log panel configuration.

    - max_lines: when exceeded, the oldest lines are dropped
    - timestamps: prefix each appended entry with [HH:MM:SS]
    """
    max_lines: int = 5000
    timestamps: bool = True


class LogPanel(QWidget):
    """
    A production-oriented log panel widget.

    Features
    --------
    - Append logs safely without freezing the UI
    - Optional timestamps
    - Max line retention (drops old lines)
    - Clear button
    - Copy button
    - Text filter (client-side search highlight by jumping to next match)
    """

    def __init__(self, config: Optional[LogPanelConfig] = None) -> None:
        super().__init__()
        self._cfg = config or LogPanelConfig()

        self._title = QLabel("Log")
        self._title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._btn_clear = QPushButton("Clear")
        self._btn_copy = QPushButton("Copy All")

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Filter / Find… (Enter = next match)")
        self._filter.returnPressed.connect(self._find_next_match)

        self._view = QPlainTextEdit()
        self._view.setReadOnly(True)
        self._view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._view.setTextInteractionFlags(
            cast(
                Qt.TextInteractionFlag,
                Qt.TextInteractionFlag.TextSelectableByKeyboard
                | Qt.TextInteractionFlag.TextSelectableByMouse
            )
        )

        mono = QFont("Monospace")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        self._view.setFont(mono)

        # Toolbar layout
        top = QHBoxLayout()
        top.addWidget(self._title)
        top.addWidget(self._btn_copy)
        top.addWidget(self._btn_clear)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._filter)
        layout.addWidget(self._view)

        # Signals
        self._btn_clear.clicked.connect(self.clear)
        self._btn_copy.clicked.connect(self.copy_all)

    # -------------------------
    # Public API
    # -------------------------
    def append(self, text: str) -> None:
        """
        Append a log entry (multi-line supported).

        This method is safe to call frequently. It:
        - adds optional timestamp
        - appends to the document
        - enforces max_lines
        - scrolls to bottom
        """
        text = (text or "").rstrip("\n")
        if not text:
            return

        prefix = ""
        if self._cfg.timestamps:
            prefix = datetime.now().strftime("[%H:%M:%S] ")

        # Preserve multi-line messages with a single timestamp at the start
        entry = prefix + text

        self._view.appendPlainText(entry)

        self._trim_to_max_lines(self._cfg.max_lines)
        self._scroll_to_bottom()

    def clear(self) -> None:
        self._view.clear()

    def copy_all(self) -> None:
        self._view.selectAll()
        self._view.copy()
        # Restore cursor to end (avoid leaving selection)
        cursor = self._view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._view.setTextCursor(cursor)

    def set_timestamps(self, enabled: bool) -> None:
        self._cfg = LogPanelConfig(max_lines=self._cfg.max_lines, timestamps=bool(enabled))

    def set_max_lines(self, max_lines: int) -> None:
        max_lines = int(max_lines)
        if max_lines <= 0:
            raise ValueError("max_lines must be positive")
        self._cfg = LogPanelConfig(max_lines=max_lines, timestamps=self._cfg.timestamps)
        self._trim_to_max_lines(self._cfg.max_lines)

    # -------------------------
    # Internal helpers
    # -------------------------
    def _scroll_to_bottom(self) -> None:
        cursor = self._view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._view.setTextCursor(cursor)

    def _trim_to_max_lines(self, max_lines: int) -> None:
        """
        Remove the oldest lines if the document exceeds max_lines.

        QPlainTextEdit stores blocks (= lines). We remove from the start.
        """
        doc = self._view.document()
        block_count = doc.blockCount()
        if block_count <= max_lines:
            return

        # Remove extra blocks from top
        remove_count = block_count - max_lines
        cursor = QTextCursor(doc)
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        for _ in range(remove_count):
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()  # remove newline

    def _find_next_match(self) -> None:
        """
        Find next occurrence of filter text and select it.
        """
        needle = self._filter.text()
        if not needle:
            return

        # Use built-in find; it wraps by resetting cursor to start when needed
        found = self._view.find(needle)
        if not found:
            cursor = self._view.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self._view.setTextCursor(cursor)
            self._view.find(needle)
