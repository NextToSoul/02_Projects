> **已迁移**: 本文件内容已全部整理归档到 .learnings/LEARNINGS.md，后续学习记录请统一写入 .learnings/ 目录。
> 
> 迁移日期: 2026-06-11
>
# PPCU TestBench 开发经验记录
日期: 2026-06-11 17:17

## 1. 架构 - Qt + asyncio 事件循环冲突
- 现象: asyncio.create_task() 在 Qt 按钮回调中无法运行
- 原因: Qt 事件循环 != asyncio 事件循环, 点击按钮时 asyncio 循环未运行
- 尝试1: threading.Thread + asyncio.run() - 信号跨线程脆弱, 不可靠
- 尝试2: qasync 统一事件循环 - 方案正确但代码被回退
- 结论: 采用 QThread Worker 模式, 工作线程持 asyncio 循环, 信号回传 UI

## 2. 工具链 - PowerShell 转义问题
- 现象: Python -c 参数中的中文和 \u 转义被 PowerShell 拦截
- 原因: PowerShell 处理引号和反斜杠的规则与 Python 冲突
- 方案1: @单引号 heredoc  (PowerShell @\'...\'@)
- 方案2: apply_patch 写入文件 (处理 Unicode 正确)
- 方案3: 直接写 .py 文件再执行

## 3. 工具链 - apply_patch 前置空格
- 现象: 文件每行多了一个前置空格
- 原因: +text 格式中 + 后面紧跟的内容即为捕获内容
- 正确: +def main(): -> 捕获 def main():
- 错误: + def main(): -> 捕获 ' def main():' (多一个空格)

## 4. 工具链 - UTF-8 BOM
- 现象: Python 报 SyntaxError: invalid non-printable character U+FEFF
- 原因: PowerShell Out-File -Encoding utf8 写入 UTF-8 with BOM
- 修复: utf-8-sig 读取后以 utf-8 重新写入

## 5. 数据 - 枚举值类型不兼容
- 现象: 遥测枚举键为整数(0:待机), 指令枚举键为十六进制(AA AA:开)
- 原设计: dict[int, str] 无法支持指令枚举
- 修复: 统一为 dict[str, str], 查询时 str(int_value)

## 6. 数据 - 导入路径错误
- 现象: ImportError: cannot import name TelemetryRegistry from core.models
- 原因: TelemetryRegistry 定义在 core.telemetry.registry 而非 core.models
- 类似: CommandRegistry, PollingManager 等均有特定导入路径

## 7. 版本 - pycache 被跟踪
- 现象: git status 显示大量 .pyc 文件的变更
- 修复: .gitignore 添加 __pycache__/, git rm --cached 移除跟踪


## Qt6 API 兼容性
### QTabWidget.setDocumentMode / setElideMode
- 问题: PySide6 6.11.1 中 QTabWidget.setDocumentMode/ElideMode 不存在
- 第一次修复: 改用 tabBar().setElideMode() - 但部分环境仍报错
- 最终修复: 直接移除这两个非关键方法
- 结论: 对于仅做界面微调的非关键 API，直接移除比绕行更安全

