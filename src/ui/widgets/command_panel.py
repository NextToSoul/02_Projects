"""PPCU TestBench — 指令发送面板"""

from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QGroupBox,
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QListWidget, QListWidgetItem, QLineEdit,
    QPushButton, QTextEdit, QGroupBox,
)

from ...core.signals import EngineSignals
from ...core.engine.async_worker import AsyncWorker


class CommandPanel(QWidget):
    def __init__(self, ctx, worker: AsyncWorker, signals: EngineSignals):
        super().__init__()
        self._ctx = ctx
        self._worker = worker
        self._signals = signals
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # \u6307\u4ee4\u5217\u8868 (\u6eda\u52a8\u680f)\n        self._list_group = QGroupBox("\u6307\u4ee4\u5217\u8868")\n        self._list_group.setCheckable(True)\n        self._list_group.setChecked(True)\n        lg = QVBoxLayout(self._list_group)\n        self._cmd_list = QListWidget()\n        if self._ctx.command_registry:
            for cmd in self._ctx.command_registry.list_commands():
                item = QListWidgetItem(f"{cmd.id} - {cmd.name}")
                item.setData(Qt.UserRole, cmd.id)
                self._cmd_list.addItem(item)
        self._cmd_list.currentItemChanged.connect(self._on_cmd_selected)
        lg.addWidget(self._cmd_list)
        layout.addWidget(self._list_group, stretch=1)

        # \u6307\u4ee4\u8be6\u60c5 (\u53ef\u6298\u53e0)
        self._detail_group = QGroupBox("指\u4ee4\u8be6\u60c5")
        self._detail_group.setCheckable(True)
        self._detail_group.setChecked(True)
        detail = QFormLayout(self._detail_group)
        self._code_label = QLabel("--")
        detail.addRow("指\u4ee4\u7801:", self._code_label)
        self._hdr_label = QLabel("--")
        detail.addRow("帧\u5934:", self._hdr_label)
        self._param_input = QLineEdit()
        self._param_input.setPlaceholderText("hex \u503c, \u5982 00 00 00 78")
        self._param_input.textChanged.connect(self._update_preview)
        detail.addRow("参\u6570\u503c:", self._param_input)
        layout.addWidget(self._detail_group)

        # \u62a5\u6587\u9884\u89c8
        layout.addWidget(QLabel("报\u6587\u9884\u89c8:"))
        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(QFont("Consolas", 9))
        self._preview.setMaximumHeight(70)
        layout.addWidget(self._preview)

        # \u53d1\u9001\u6309\u94ae + \u72b6\u6001
        row = QHBoxLayout()
        self._send_btn = QPushButton("▶ \u53d1\u9001")
        self._send_btn.clicked.connect(self._on_send)
        row.addWidget(self._send_btn)
        self._status = QLabel("就\u7eea")
        self._status.setStyleSheet("color: gray;")
        row.addWidget(self._status, stretch=1)
        layout.addLayout(row)

    def connect_signals(self):
        self._signals.raw_frame_sent.connect(self._on_frame_sent)

    def _on_cmd_selected(self, cur, prev):
        if not cur:
            return
        cmd_id = cur.data(Qt.UserRole)
        cmd = self._ctx.command_registry.get_command(cmd_id) if self._ctx.command_registry else None
        if cmd:
            code = cmd.command_code.replace(" ", "")
            self._code_label.setText(f"0x{code}" if code else "--")
            self._hdr_label.setText(f"{cmd.frame_header} APID={cmd.app_process_id}")
        self._update_preview()

    def _update_preview(self):
        item = self._cmd_list.currentItem()
        if not item or not hasattr(self._ctx, 'protocol'):
            self._preview.clear(); return
        cmd_id = item.data(Qt.UserRole)
        cmd = self._ctx.command_registry.get_command(cmd_id)
        if cmd:
            try:
                param = self._param_input.text().strip()
                frame = self._ctx.protocol.encode_command(cmd, 0, {"value": param} if param else None)
                self._preview.setText(frame.hex(" ").upper())
                return
            except: pass
        self._preview.clear()

    def _on_send(self):
        item = self._cmd_list.currentItem()
        if not item:
            return
        cmd_id = item.data(Qt.UserRole)
        param = self._param_input.text().strip()
        self._status.setText("正\u5728\u53d1\u9001...")
        self._status.setStyleSheet("color: blue;")
        if hasattr(self._worker, "send_command"):
            self._worker.send_command(cmd_id, param)

    @Slot(str, str)
    def _on_frame_sent(self, ts, hex_str):
        self._status.setText(f"\u5df2\u53d1\u9001 {ts}")
        self._status.setStyleSheet("color: green;")
