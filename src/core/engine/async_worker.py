"""
PPCU TestBench — 异步工作线程
后台线程持有独立的 asyncio 事件循环，通过 Qt 信号回传结果到 UI 线程。
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class AsyncWorker(QThread):
    """后台工作线程 - 持有一个独立的 asyncio 事件循环"""

    connection_changed = Signal(bool, str)
    raw_frame_sent = Signal(str, str)
    raw_frame_received = Signal(str, str, bool)
    error_occurred = Signal(str, str)

    def __init__(self, ctx, transport, protocol, seq_mgr):
        super().__init__()
        self._ctx = ctx
        self._transport = transport
        self._protocol = protocol
        self._seq = seq_mgr
        self._loop = None
        self._loop_ready = True
        self._polling_mgr = None

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        logger.info("AsyncWorker: asyncio loop started")
        try:
            self._loop.run_forever()
        finally:
            self._loop.close()
            logger.info("AsyncWorker: asyncio loop stopped")

    def connect(self, cfg: dict):
        if self._loop: asyncio.run_coroutine_threadsafe(self._do_connect(cfg), self._loop)

    def disconnect(self):
        if self._loop: asyncio.run_coroutine_threadsafe(self._do_disconnect(), self._loop)

    def stop(self):
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        self.wait(3000)

    async def _do_connect(self, cfg: dict):
        result = await self._transport.connect(cfg)
        if result:
            detail = f"{cfg.get('host')}:{cfg.get('port')}"
            self.connection_changed.emit(True, detail)
            # \u8fde\u63a5\u6210\u529f\uff0c\u4e0d\u81ea\u52a8\u8f6e\u8be2
        else:
            self.connection_changed.emit(False, "连接失败")

    async def _do_disconnect(self):
        if self._polling_mgr:
            self._polling_mgr.stop_all()
        await self._transport.disconnect()
        self.connection_changed.emit(False, "已断开")

    @property
    def polling_manager(self):
        return self._polling_mgr

    @polling_manager.setter
    def polling_manager(self, mgr):
        self._polling_mgr = mgr
