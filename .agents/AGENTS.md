 # PPCU 通用测试平台
 
 航天用 PPCU（Power Processing and Control Unit）自动化测试软件。
 基于 PySide6 + asyncio，支持 TCP→RS422 通讯，CCSDS 协议。
 通过 Device Profile 机制支持跨项目扩展。
 
 ## 项目结构
 
 - src/  — 应用源码（核心引擎 + UI + 报告 + 配置）
 - profiles/ — 设备配置包（每个子目录是一个测试项目）
 - docs/ — 设计文档
 - reports/ — 测试报告输出（gitignore）
 - tests/ — 单元测试
 - scripts/ — CLI 验证脚本
 
 ## 核心技术栈
 
 - Python 3.10+
 - PySide6 (LGPL v3, 免费商用)
 - asyncio (TCP 通讯)
 - YAML (测试用例/配置)
 - openpyxl + Jinja2 + python-docx (报告)
 - SQLite (结果库)
 - PyInstaller (打包 exe)
 
 ## 设计原则
 
 - 数据驱动：协议定义来自 Excel，不硬编码
 - 硬件抽象：Transport/ProtocolCodec 接口，支持 TCP/CAN/串口
 - 解耦架构：引擎通过事件总线与 UI 通信
 - 安全优先：指令拦截 + 高危确认 + 参数校验
 - 跨项目扩展：换项目 = 换一套配置 + 新 Transport 实现
