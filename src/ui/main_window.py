"""PPCU TestBench — 主窗口 (Step 2: 完整骨架)"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QStatusBar,
    QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox,
)

from ..core.signals import EngineSignals
from .widgets.connection_bar import ConnectionBar
from .widgets.telemetry import TelemetryTableView
from .widgets.command_panel import CommandPanel
from .widgets.injection_panel import InjectionPanel

logger = logging.getLogger(__name__)
class MainWindow(QMainWindow):
    """PPCU TestBench 主窗口"""

    def __init__(self, ctx, signals, worker, default_cfg):
        super().__init__()
        self._ctx = ctx
        self._signals = signals
        self._worker = worker
        self.setWindowTitle(f"PPCU \u901a\u7528\u6d4b\u8bd5\u5e73\u53f0 \u2014 [{ctx.name}]")
        self.setMinimumSize(900, 600)
        self.resize(1200, 750)
        self.setup_ui(default_cfg)
        self.connect_signals()

    def setup_ui(self, default_cfg):
        self._create_menu_bar()
        self._create_toolbar(default_cfg)
        self._create_central_area()
        self._create_status_bar()

    # ==== 1. 菜单栏 ====
    def _create_menu_bar(self):
        mb = self.menuBar()

        # \u6587\u4ef6(&F)
        fm = mb.addMenu("\u6587\u4ef6(&F)")
        fm.addAction("\u9000\u51fa(&Q)", self.close, "Ctrl+Q")

        # \u6d4b\u8bd5(&T)
        tm = mb.addMenu("\u6d4b\u8bd5(&T)")
        tm.addAction("\u751f\u6210\u62a5\u544a...")

        # \u914d\u7f6e(&C)
        cm = mb.addMenu("\u914d\u7f6e(&C)")
        cm.addAction("\u5b89\u5168\u8bbe\u7f6e...")

        # \u5e2e\u52a9(&H)
        hm = mb.addMenu("\u5e2e\u52a9(&H)")
        hm.addAction("\u5173\u4e8e...", self._show_about)

    def _show_about(self):
        QMessageBox.about(self, "\u5173\u4e8e PPCU TestBench",
            "PPCU \u901a\u7528\u6d4b\u8bd5\u5e73\u53f0 v1.0\n\n"
            "\u57fa\u4e8e PySide6 + asyncio\n"
            "CCSDS Space Packet Protocol")

    # ==== 2. 工具栏 (ConnectionBar + \u9879\u76ee\u5207\u6362 + \u8f6e\u8be2\u63a7\u5236) ====
    def _create_toolbar(self, cfg):
        tb = QToolBar("\u4e3b\u5de5\u5177\u680f")
        tb.setMovable(False)
        tb.setStyleSheet("QToolBar { spacing: 4px; }")

        # --- 2a. ConnectionBar (IP/\u7aef\u53e3/\u8fde\u63a5/\u65ad\u5f00) ---
        host = cfg.get("host", "")
        port = cfg.get("port", 0)
        self._conn_bar = ConnectionBar(host, port)
        self._conn_bar.connect_requested.connect(self._on_connect)
        self._conn_bar.disconnect_requested.connect(self._on_disconnect)
        tb.addWidget(self._conn_bar)
        tb.addSeparator()

        # --- 2b. \u9879\u76ee\u5207\u6362 ---
        tb.addWidget(QLabel("\u9879\u76ee:"))
        self._project_combo = QComboBox()
        self._project_combo.setFixedWidth(180)
        self._project_combo.addItem(self._ctx.name)
        self._project_combo.currentTextChanged.connect(self._on_project_changed)
        tb.addWidget(self._project_combo)
        tb.addSeparator()

        # --- 2c. \u8f6e\u8be2\u63a7\u5236\u6309\u94ae ---
        self._poll_start_btn = QPushButton("\u25b6 \u542f\u52a8\u8f6e\u8be2")
        self._poll_start_btn.clicked.connect(self._on_poll_start_all)
        tb.addWidget(self._poll_start_btn)

        self._poll_pause_btn = QPushButton("\u23f8 \u6682\u505c")
        self._poll_pause_btn.clicked.connect(self._on_poll_pause_all)
        tb.addWidget(self._poll_pause_btn)

        self._poll_stop_btn = QPushButton("\u25a0 \u505c\u6b62")
        self._poll_stop_btn.clicked.connect(self._on_poll_stop_all)
        tb.addWidget(self._poll_stop_btn)

        self.addToolBar(tb)

    # ==== 3. \u4e2d\u592e TabWidget (3 \u4e2a\u6807\u7b7e\u9875\u5360\u4f4d) ====
    def _create_central_area(self):
        """3\u5217 QSplitter \u5e03\u5c40: \u9065\u6d4b\u6570\u636e\u8868 + \u6307\u4ee4\u53d1\u9001 + \u53c2\u6570\u6ce8\u5165"""
        splitter_h = QSplitter(Qt.Horizontal)

        # \u9762\u677f 1: \u9065\u6d4b\u6570\u636e\u8868
        self._telemetry_view = TelemetryTableView(self._ctx.telemetry_registry, self._signals)
        splitter_h.addWidget(self._telemetry_view)

        # \u9762\u677f 2: \u6307\u4ee4\u53d1\u9001
        self._command_panel = CommandPanel(self._ctx, self._worker, self._signals)
        splitter_h.addWidget(self._command_panel)

        # \u9762\u677f 3: \u53c2\u6570\u6ce8\u5165
        self._injection_panel = InjectionPanel(self._ctx, self._worker, self._signals)
        splitter_h.addWidget(self._injection_panel)

        splitter_h.setSizes([400, 400, 400])

        # \u5e95\u90e8: \u62a5\u6587\u76d1\u89c6\u5668
        bottom = QWidget(); bl = QVBoxLayout(bottom)
        bl.setContentsMargins(4, 4, 4, 4)
        bl.addWidget(QLabel("\u62a5\u6587\u76d1\u89c6\u5668 (\u5f85\u5b9e\u73b0)"))

        # \u603b\u5e03\u5c40: \u4e0a(3\u5217) + \u4e0b(\u62a5\u6587)
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(splitter_h)
        main_splitter.addWidget(bottom)
        main_splitter.setSizes([600, 200])

        self.setCentralWidget(main_splitter)
    def _create_status_bar(self):
        sb = self.statusBar()
        # \u5de6: \u8fde\u63a5\u72b6\u6001/\u63d0\u793a\u4fe1\u606f
        self._status_label = QLabel("\u5c31\u7eea")
        sb.addWidget(self._status_label, 1)
        # \u4e2d: \u9065\u6d4b\u5305\u6d3b\u8dc3\u72b6\u6001
        self._pkg_status = QLabel("\u9065\u6d4b\u5305: 0/3 \u6d3b\u8dc3")
        sb.addPermanentWidget(self._pkg_status)
        # \u53f3: \u6700\u8fd1\u63a5\u6536
        self._rx_status = QLabel("\u6700\u8fd1\u63a5\u6536: --")
        sb.addPermanentWidget(self._rx_status)

    # ==== 5. \u4fe1\u53f7\u8fde\u63a5 ====
    def connect_signals(self):
        self._signals.connection_changed.connect(self._on_connection_changed)
        self._signals.error_occurred.connect(self._on_error)
        # \u72b6\u6001\u680f\u66f4\u65b0
        self._signals.polling_mode_changed.connect(self._on_poll_mode_changed)

    # ==== 6. \u69fd\u51fd\u6570 ====

    # --- 6a. \u8fde\u63a5\u63a7\u5236 ---
    def _on_connect(self, cfg):
        self._conn_bar.set_loading(True)
        self._worker.connect(cfg)

    def _on_disconnect(self):
        self._worker.disconnect()

    @Slot(bool, str)
    def _on_connection_changed(self, connected, detail):
        self._conn_bar.set_connected(connected, detail)
        self._status_label.setText(detail)

    # --- 6b. \u9879\u76ee\u5207\u6362 ---
    def _on_project_changed(self, name: str):
        logger.info(f"Project switch requested: {name}")

    # --- 6c. \u8f6e\u8be2\u63a7\u5236 ---
    def _on_poll_start_all(self):
        if hasattr(self._worker, 'start_polling_all'):
            self._worker.start_polling_all()

    def _on_poll_pause_all(self):
        if hasattr(self._worker, 'pause_polling_all'):
            self._worker.pause_polling_all()

    def _on_poll_stop_all(self):
        if hasattr(self._worker, 'stop_polling_all'):
            self._worker.stop_polling_all()

    @Slot(str, str)
    def _on_poll_mode_changed(self, pkg_name: str, mode_str: str):
        # \u66f4\u65b0\u72b6\u6001\u680f\u4e2d\u7684\u9065\u6d4b\u5305\u8ba1\u6570
        if hasattr(self._ctx, "polling_manager") and self._ctx.polling_manager:
            total = len(self._ctx.telemetry_registry.list_packages())
            active = len(self._ctx.polling_manager.active_pollers)
            self._pkg_status.setText(f"\u9065\u6d4b\u5305: {active}/{total} \u6d3b\u8dc3")

    # --- 6d. \u9519\u8bef\u5904\u7406 ---
    @Slot(str, str)
    def _on_error(self, source, msg):
        self._status_label.setText(f"\u9519\u8bef [{source}]: {msg}")

   # ==== 7. \u5c5e\u6027 ====
    @property
    def conn_bar(self):
        return self._conn_bar
