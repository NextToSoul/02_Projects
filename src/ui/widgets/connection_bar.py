"""PPCU TestBench — 通讯连接控制栏"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton


class ConnectionBar(QWidget):
    """IP/端口输入 + 连接/断开按钮"""

    connect_requested = Signal(dict)
    disconnect_requested = Signal()

    def __init__(self, default_host="", default_port=0, parent=None):
        super().__init__(parent)
        self._connected = False
        self._loading = False
        self.setup_ui(default_host, default_port)

    def setup_ui(self, host, port):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        layout.addWidget(QLabel("IP:"))
        self._ip_input = QLineEdit(host)
        self._ip_input.setFixedWidth(150)
        self._ip_input.setPlaceholderText("192.168.1.100")
        layout.addWidget(self._ip_input)

        layout.addWidget(QLabel("Port:"))
        self._port_input = QLineEdit(str(port) if port else "")
        self._port_input.setFixedWidth(80)
        self._port_input.setPlaceholderText("2000")
        layout.addWidget(self._port_input)

        self._conn_btn = QPushButton("连接")
        self._conn_btn.setFixedWidth(100)
        self._conn_btn.clicked.connect(self._toggle)
        self._conn_btn.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self._conn_btn)

    def _toggle(self):
        if self._loading or not self._ip_input.text().strip():
            return
        if self._connected:
            self.disconnect_requested.emit()
        else:
            try:
                cfg = {
                    "host": self._ip_input.text().strip(),
                    "port": int(self._port_input.text().strip()) if self._port_input.text().strip() else 0,
                    "reconnect_max_retries": 1,
                    "reconnect_interval_s": 1,
                    "timeout_s": 3.0,
                }
                self.connect_requested.emit(cfg)
            except ValueError:
                pass

    def set_connected(self, connected: bool, detail: str = ""):
        self._connected = connected
        self._loading = False
        if connected:
            self._conn_btn.setText("断开")
            self._conn_btn.setStyleSheet("color: red; font-weight: bold;")
            self._ip_input.setEnabled(False)
            self._port_input.setEnabled(False)
        else:
            self._conn_btn.setText("连接")
            self._conn_btn.setStyleSheet("color: green; font-weight: bold;")
            self._ip_input.setEnabled(True)
            self._port_input.setEnabled(True)

    def set_loading(self, loading: bool):
        self._loading = loading
        self._conn_btn.setText("连接中...")

    @property
    def host(self) -> str:
        return self._ip_input.text().strip()

    @property
    def port(self) -> int:
        try:
            return int(self._port_input.text().strip()) if self._port_input.text().strip() else 0
        except ValueError:
            return 0
