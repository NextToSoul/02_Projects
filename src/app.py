"""PPCU TestBench — 应用程序入口"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .config.loader import ProfileLoader
from .core.hardware.sequencer import SequenceManager
from .core.signals import EngineSignals
from .core.telemetry.cache import TelemetryCache
from .core.telemetry.poller import PollingManager
from .core.engine.async_worker import AsyncWorker
from .ui.main_window import MainWindow

logger = logging.getLogger(__name__)


class PpuTestBenchApp:
    def __init__(self):
        self.signals = EngineSignals()
        self.telemetry_cache = TelemetryCache()
        self.seq_mgr = SequenceManager()
        self.worker = None
        self.window = None
        self._ctx = None

    async def initialize(self, profile_path):
        loader = ProfileLoader()
        ctx = await loader.load(Path(profile_path))
        self._ctx = ctx

        self.worker = AsyncWorker(ctx, ctx.transport, ctx.protocol, self.seq_mgr)
        self.worker.start()

        pm = PollingManager(ctx.transport, ctx.protocol, self.seq_mgr, self.telemetry_cache)
        pm.set_registries(ctx.telemetry_registry, ctx.command_registry)
        for pkg in ctx.telemetry_registry.list_packages():
            pm.register_package(pkg)
        self.worker.connection_changed.connect(self.signals.connection_changed.emit)
        self.worker.error_occurred.connect(self.signals.error_occurred.emit)
        self.worker.polling_manager = pm

        default_cfg = ctx.profile.transport_config if ctx.profile else {}
        self.window = MainWindow(ctx, self.signals, self.worker, default_cfg)
        self.window.show()
        logger.info(f"Application started: {ctx.name}")

    def shutdown(self):
        if self.worker:
            self.worker.stop()


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="PPCU TestBench")
    parser.add_argument("--profile", default="profiles/ppcu_rs422")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    app = QApplication(sys.argv)
    app.setApplicationName("PPCU TestBench")

    tui = PpuTestBenchApp()
    await tui.initialize(Path(args.profile))

    exit_code = app.exec()
    tui.shutdown()
    sys.exit(exit_code)
