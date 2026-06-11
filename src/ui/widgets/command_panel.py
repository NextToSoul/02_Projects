"""PPCU TestBench — 指令发送面板"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QFrame,
)

from ...core.signals import EngineSignals
from ...core.engine.async_worker import AsyncWorker

logger = logging.getLogger(__name__)


class CommandPanel(QWidget):
    def __init__(self, ctx, worker: AsyncWorker, signals: EngineSignals):
        super().__init__()
        self._ctx = ctx
        self._worker = worker
        self._signals = signals
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # \u6307\u4ee4\u4e0b\u62c9
        layout.addWidget(QLabel("指\u4ee4:"))
        self._cmd_combo = QComboBox()
        if self._ctx.command_registry:
            for cmd in self._ctx.command_registry.list_commands():
                self._cmd_combo.addItem(f"{cmd.id} - {cmd.name}", cmd.id)
        self._cmd_combo.currentIndexChanged.connect(self._on_cmd_changed)
        layout.addWidget(self._cmd_combo)

        # \u53c2\u6570\u503c\u8f93\u5165
        f = QFormLayout()
        self._param_input = QLineEdit()
        self._param_input.setPlaceholderText("hex \u503c, \u5982 00 00 00 78")
        f.addRow("参\u6570\u503c:", self._param_input)
        layout.addLayout(f)

        # \u679a\u4e3e\u503c\u4e0b\u62c9
        self._enum_layout = QHBoxLayout()
        self._enum_layout.addWidget(QLabel("枚\u4e3e\u503c:"))
        self._enum_combo = QComboBox()
        self._enum_combo.addItem("--")
        self._enum_combo.currentTextChanged.connect(self._on_enum_selected)
        self._enum_layout.addWidget(self._enum_combo)
        self._enum_widget = QWidget()
        self._enum_widget.setLayout(self._enum_layout)
        self._enum_widget.setVisible(False)
        layout.addWidget(self._enum_widget)

        # \u53d1\u9001\u6309\u94ae
        self._send_btn = QPushButton("▶ \u53d1\u9001\u6307\u4ee4")
        self._send_btn.clicked.connect(self._on_send)
        layout.addWidget(self._send_btn)

        # \u72b6\u6001\u663e\u793a
        self._status_label = QLabel("状\u6001: 就\u7eea")
        self._status_label.setStyleSheet("color: gray;")
        layout.addWidget(self._status_label)

        # \u5386\u53f2\u8bb0\u5f55
        layout.addWidget(QLabel("历\u53f2\u53d1\u9001:"))
        self._history = QListWidget()
        self._history.setMaximumHeight(120)
        layout.addWidget(self._history, stretch=1)

    def _on_cmd_changed(self, idx):
        cmd_id = self._cmd_combo.currentData()
        if cmd_id and self._ctx.command_registry:
            cmd = self._ctx.command_registry.get_command(cmd_id)
            if cmd and cmd.enum_values:
                self._enum_combo.clear()
                for k, v in cmd.enum_values.items():
                    self._enum_combo.addItem(f"{k}: {v}", k)
                self._enum_widget.setVisible(True)
                return
        self._enum_widget.setVisible(False)

    def _on_enum_selected(self, text):
        if text and text != "--":
            key = self._enum_combo.currentData()
            if key:
                self._param_input.setText(str(key))

    def _on_send(self):
        cmd_id = self._cmd_combo.currentData()
        if not cmd_id:
            return
        param = self._param_input.text().strip()
        self._status_label.setText(f"正\u5728\u53d1\u9001 {cmd_id}...")
        self._status_label.setStyleSheet("color: blue;")

        if hasattr(self._worker, "send_command"):
            self._worker.send_command(cmd_id, param)

        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        item = QListWidgetItem(f"[{ts}] {cmd_id}  param={param or "--"}")
        self._history.insertItem(0, item)
        if self._history.count() > 50:
            self._history.takeItem(self._history.count() - 1)
