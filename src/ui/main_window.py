"""PPCU TestBench — 主窗口"""

from __future__ import annotations

import logging

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QStatusBar,
    QWidget, QVBoxLayout, QLabel,
)

from ..core.signals import EngineSignals
from .widgets.connection_bar import ConnectionBar

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, ctx, signals, worker, default_cfg):
        super().__init__()
        self._ctx = ctx
        self._signals = signals
        self._worker = worker
        self.setWindowTitle(f"PPCU 通用测试平台 \u2014 [{ctx.name}]")
        self.setMinimumSize(800, 500)
        self.resize(1024, 680)
        self.setup_ui(default_cfg)
        self.connect_signals()

    def setup_ui(self, default_cfg):
        self._create_menu_bar()
        self._create_toolbar(default_cfg)
        self._create_status_bar()

    def _create_menu_bar(self):
        mb = self.menuBar()
        mb.addMenu("文件(&F)").addAction("退出(&Q)", self.close, "Ctrl+Q")

    def _create_toolbar(self, cfg):
        tb = QToolBar("通讯工具栏")
        tb.setMovable(False)
        host = cfg.get("host", "")
        port = cfg.get("port", 0)
        self._conn_bar = ConnectionBar(host, port)
        tb.addWidget(self._conn_bar)
        self.addToolBar(tb)

    def _create_status_bar(self):
        self._status_label = QLabel("就绪")
        self.statusBar().addWidget(self._status_label, 1)

    def connect_signals(self):
        self._signals.connection_changed.connect(self._on_connection_changed)
        self._conn_bar.connect_requested.connect(self._on_connect)
        self._conn_bar.disconnect_requested.connect(self._on_disconnect)

    def _on_connect(self, cfg):
        self._conn_bar.set_loading(True)
        self._worker.connect(cfg)

    def _on_disconnect(self):
        self._worker.disconnect()

    @Slot(bool, str)
    def _on_connection_changed(self, connected, detail):
        self._conn_bar.set_connected(connected, detail)
        self._status_label.setText(detail)

    @property
    def conn_bar(self):
        return self._conn_bar
