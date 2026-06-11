# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260611-001] best_practice

**Logged**: 2026-06-11T17:17:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
Qt + asyncio 事件循环冲突应使用 QThread Worker 模式，而非 threading.Thread + asyncio.run()

### Details
PySide6 的事件循环与 asyncio 的事件循环不兼容。在 Qt 按钮回调中直接调用 asyncio.create_task() 无法运行。
- 尝试1: threading.Thread + asyncio.run() — 信号跨线程脆弱，不可靠
- 尝试2: qasync 统一事件循环 — 方案正确但代码被回退
- 最终: 采用 QThread Worker 模式，工作线程持 asyncio 循环，信号回传 UI

### Metadata
- Source: user_feedback
- Related Files: PPCU_TestBench/src/core/hardware/transport.py
- Tags: qt, asyncio, threading, architecture
- Pattern-Key: arch.event_loop_conflict

---

## [LRN-20260611-002] knowledge_gap

**Logged**: 2026-06-11T17:17:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
PowerShell 会拦截 Python -c 参数中的中文和 \u 转义

### Details
PowerShell 处理引号和反斜杠的规则与 Python 冲突，导致解释器无法正确解析内联脚本。
- 方案1: 使用 PowerShell @'...'@ heredoc 语法
- 方案2: 使用 apply_patch 工具写入文件（处理 Unicode 正确）
- 方案3: 直接写入 .py 文件再执行

### Metadata
- Source: error
- Tags: powershell, python, encoding, toolchain
- Pattern-Key: toolchain.powershell_quoting

---

## [LRN-20260611-003] correction

**Logged**: 2026-06-11T17:17:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
apply_patch 的 + 号后紧跟内容，不能有多余空格

### Details
apply_patch 工具语法中 +text 的 + 号后紧跟字符即为捕获内容。
- 正确: +def main(): → 捕获 def main():
- 错误: + def main(): → 捕获 ' def main():'（多一个前置空格）

### Metadata
- Source: error
- Tags: apply_patch, tooling, formatting
- Pattern-Key: toolchain.apply_patch_spacing

---

## [LRN-20260611-004] knowledge_gap

**Logged**: 2026-06-11T17:17:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
PowerShell Out-File -Encoding utf8 写入 UTF-8 with BOM，Python 无法直接读取

### Details
Python 解析含 BOM 的文件时报 SyntaxError: invalid non-printable character U+FEFF。
- 修复: 用 utf-8-sig 编码读取后，以 utf-8 重新写入即可

### Metadata
- Source: error
- Tags: encoding, utf8, bom, powershell
- Pattern-Key: toolchain.utf8_bom

---

## [LRN-20260611-005] correction

**Logged**: 2026-06-11T17:17:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
遥测和指令的枚举类型应统一使用 dict[str, str] 而非 dict[int, str]

### Details
原设计使用 dict[int, str] 存储枚举值。但指令枚举键为十六进制（如 AA AA:开），与遥测枚举的整数键（如 0:待机）不兼容。
- 修复: 统一为 dict[str, str]，查询时用 str(int_value)

### Metadata
- Source: error
- Related Files: PPCU_TestBench/src/core/models.py, PPCU_TestBench/src/core/definitions.py
- Tags: data, enum, type, consistency
- Pattern-Key: data.enum_type_unification

---

## [LRN-20260611-006] knowledge_gap

**Logged**: 2026-06-11T17:17:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
各个 Registry/Manager 类有各自的导入路径，不在 core.models 中

### Details
导入路径错误导致 ImportError: cannot import name TelemetryRegistry from core.models。
- TelemetryRegistry → core.telemetry.registry
- CommandRegistry → core.telemetry.registry
- PollingManager → core.telemetry.poller
- 其他类似类均有各自的特定导入路径

### Metadata
- Source: error
- Related Files: PPCU_TestBench/src/core/telemetry/registry.py, PPCU_TestBench/src/core/telemetry/poller.py
- Tags: import, structure, project_layout
- Pattern-Key: backend.import_paths

---

## [LRN-20260611-007] best_practice

**Logged**: 2026-06-11T17:17:00+08:00
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
.gitignore 需添加 __pycache__/，并移除已被 Git 跟踪的 .pyc 文件

### Details
git status 显示大量 .pyc 文件的变更，说明 __pycache__ 目录未被正确忽略。
- 修复: .gitignore 添加 __pycache__/
- 清理: git rm --cached 移除已跟踪的 .pyc 文件

### Metadata
- Source: error
- Related Files: PPCU_TestBench/.gitignore
- Tags: git, pycache, cleanup
- Pattern-Key: infra.pycache_gitignore

---

## [LRN-20260611-008] best_practice

**Logged**: 2026-06-11T17:17:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: frontend

### Summary
PySide6 6.11.1 中移除的 QTabWidget API（setDocumentMode、setElideMode）直接移除即可

### Details
PySide6 6.11.1 中 QTabWidget.setDocumentMode 和 setElideMode 不存在。
- 第一次修复: 改用 tabBar().setElideMode() — 但部分环境仍报错
- 最终修复: 直接移除这两个非关键方法
- 结论: 对于仅做界面微调的非关键 API，直接移除比绕行更安全

### Metadata
- Source: error
- Related Files: PPCU_TestBench/src/core/ui/tabs.py
- Tags: qt6, pyside6, api, compatibility
- Pattern-Key: frontend.qt6_api_compat

---
