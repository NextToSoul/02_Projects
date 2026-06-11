"""PPCU TestBench — 参数注入面板"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QGroupBox,
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
)

from ...core.signals import EngineSignals

logger = logging.getLogger(__name__)


class InjectionPanel(QWidget):
    def __init__(self, ctx, worker, signals: EngineSignals):
        super().__init__()
        self._ctx = ctx
        self._worker = worker
        self._signals = signals
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._group = QGroupBox("参数注入")
        self._group.setCheckable(True)
        self._group.setChecked(True)
        gl = QVBoxLayout(self._group)
        gl.setContentsMargins(4, 4, 4, 4)

        # \u6ce8\u5165\u8868\u4e0b\u62c9
        gl.addWidget(QLabel("注\u5165\u8868:"))
        self._inj_combo = QComboBox()
        self._inj_index = {}  # name -> InjectionDef
        if self._ctx.command_registry:
            for inj in self._ctx.command_registry.get_injections():
                self._inj_combo.addItem(inj.name, inj.name)
                self._inj_index[inj.name] = inj
        self._inj_combo.currentTextChanged.connect(self._on_table_changed)
        gl.addWidget(self._inj_combo)

        # \u53c2\u6570\u5217\u8868
        self._param_table = QTableWidget()
        self._param_table.setColumnCount(3)
        self._param_table.setHorizontalHeaderLabels(["参数名称", "当前值", "单位"])
        self._param_table.horizontalHeader().setStretchLastSection(True)
        self._param_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._param_table.setAlternatingRowColors(True)
        self._param_table.setFont(self._param_table.font())
        self._param_table.verticalHeader().hide()
        gl.addWidget(self._param_table, stretch=1)

        # \u6309\u94ae\u884c
        btn_row = QHBoxLayout()
        self._write_btn = QPushButton("批量写入")
        self._write_btn.clicked.connect(self._on_write)
        btn_row.addWidget(self._write_btn)

        self._read_btn = QPushButton("读取全部")
        self._read_btn.clicked.connect(self._on_read)
        btn_row.addWidget(self._read_btn)

        self._reset_btn = QPushButton("重置为默认值")
        self._reset_btn.clicked.connect(self._on_reset_defaults)
        btn_row.addWidget(self._reset_btn)

        gl.addLayout(btn_row)

        # \u72b6\u6001
        self._status_label = QLabel("就绪")
        self._status_label.setStyleSheet("color: gray;")
        gl.addWidget(self._status_label)

        # \u52a0\u8f7d\u9ed8\u8ba4\u8868
        if self._inj_combo.count() > 0:
            self._on_table_changed(self._inj_combo.currentText())

    def _on_table_changed(self, name: str):
        inj = self._inj_index.get(name)
        if not inj:
            return
        self._param_table.setRowCount(len(inj.parameters))
        for row, p in enumerate(inj.parameters):
            self._param_table.setItem(row, 0, QTableWidgetItem(p.name))
            self._param_table.setItem(row, 1, QTableWidgetItem(p.default_value if p.default_value else ""))
            self._param_table.setItem(row, 2, QTableWidgetItem(p.unit))

    def _on_reset_defaults(self):
        name = self._inj_combo.currentText()
        inj = self._inj_index.get(name)
        if not inj:
            return
        for row, p in enumerate(inj.parameters):
            self._param_table.item(row, 1).setText(p.default_value if p.default_value else "")

    def _on_write(self):
        self._status_label.setText("将\u5728\u540e\u7eed\u6b65\u9aa4\u4e2d实现")

    def _on_read(self):
        pass
