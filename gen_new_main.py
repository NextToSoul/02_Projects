import tempfile, os
src = r'E:\Codex Workspace\02_Projects\PPCU_TestBench\src\ui\main_window.py'
with open(src, 'r', encoding='utf-8') as f:
    lines = f.readlines()
new_lines = []
i = 0
while i < len(lines):
    if 'def _create_central_area(self):' in lines[i]:
        new_lines.append(lines[i]); i += 1
        while i < len(lines) and '_create_status_bar' not in lines[i]:
            i += 1
        new_lines.append('        """2\u5217 QSplitter \u5e03\u5c40: \u9065\u6d4b(\u5de6) \u6307\u4ee4+\u6ce8\u5165(\u53f3)"""\n')
        new_lines.append('        right_splitter = QSplitter(Qt.Vertical)\n')
        new_lines.append('        self._command_panel = CommandPanel(self._ctx, self._worker, self._signals)\n')
        new_lines.append('        right_splitter.addWidget(self._command_panel)\n')
        new_lines.append('        self._injection_panel = InjectionPanel(self._ctx, self._worker, self._signals)\n')
        new_lines.append('        right_splitter.addWidget(self._injection_panel)\n')
        new_lines.append('        right_splitter.setSizes([300, 300])\n')
        new_lines.append('        splitter_h = QSplitter(Qt.Horizontal)\n')
        new_lines.append('        self._telemetry_view = TelemetryTableView(self._ctx.telemetry_registry, self._signals)\n')
        new_lines.append('        splitter_h.addWidget(self._telemetry_view)\n')
        new_lines.append('        splitter_h.addWidget(right_splitter)\n')
        new_lines.append('        splitter_h.setSizes([600, 400])\n')
        new_lines.append('        bottom = QWidget(); bl = QVBoxLayout(bottom)\n')
        new_lines.append('        bl.setContentsMargins(4, 4, 4, 4)\n')
        new_lines.append('        bl.addWidget(QLabel("\u62a5\u6587\u76d1\u89c6\u5668 (\u5f85\u5b9e\u73b0)"))\n')
        new_lines.append('        main_splitter = QSplitter(Qt.Vertical)\n')
        new_lines.append('        main_splitter.addWidget(splitter_h)\n')
        new_lines.append('        main_splitter.addWidget(bottom)\n')
        new_lines.append('        main_splitter.setSizes([600, 200])\n')
        new_lines.append('        self.setCentralWidget(main_splitter)\n')
        continue
    new_lines.append(lines[i]); i += 1
fd, tmp = tempfile.mkstemp(suffix='.py', prefix='ppcu_main_')
os.close(fd)
with open(tmp, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print(f'TEMP: {tmp}')
print(f'LINES: old={len(lines)} new={len(new_lines)}')
