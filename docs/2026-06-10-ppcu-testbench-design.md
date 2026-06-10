 # PPCU 通用测试平台 — 设计方案
 
 > 版本: v1.0  
 > 日期: 2026-06-10  
 
 ---
 
 ## 一、项目概述
 
 ### 1.1 背景
 
 为航天用 PPCU（Power Processing and Control Unit）研发自动化测试软件。PPCU 通过 RS422 接口与测试计算机通讯，通讯链路为：
 
 **测试电脑 → 网线 → 网络通讯盒（串口转以太网）→ RS422 → PPCU**
 
 通讯协议基于 **CCSDS Space Packet Protocol** 标准（Big-Endian），通讯周期 1s。
 
 ### 1.2 核心需求
 
 - 发送/修改指令 → 查询遥测 → 监测流程阶段时间 → 反馈测试结果（成功/失败），报告原因
 - 实时/按需显示收发报文、测试进度
 - 可灵活配置输入条件与通过条件
 - 自动生成 CSV、HTML、Word 三种格式测试报告
 - **全局动态编码，避免硬编码**
 - 支持跨项目扩展（同架构下替换通讯方式即可适配其他设备）
 
 ### 1.3 设计原则
 
 | 原则 | 说明 |
 |------|------|
 | **数据驱动** | 所有协议定义（指令格式、遥测参数映射）来自 Excel 配置，不写死在代码中 |
 | **硬件抽象** | Transport / ProtocolCodec 双层接口，当前实现 TCP+CCSDS，可扩展 CAN/串口等 |
 | **解耦架构** | Polling Loop 独立于用例执行，通过遥测缓存与事件总线同步 |
 | **安全优先** | 指令级别拦截、高危确认、参数值范围校验三层保护 |
 | **模块组合** | 测试用例由步骤模块组合（表单界面 + YAML 双向同步） |
 
 ---
 
 ## 二、技术选型
 
 | 方向 | 选型 | 理由 |
 |------|------|------|
 | 语言 | Python 3.10+ | 生态丰富、动态类型天然避免硬编码 |
 | GUI 框架 | **PySide6** (LGPL v3) | 原生桌面体验、免费商用、可打包 exe |
 | 通讯 | asyncio (asyncio.open_connection) | 非阻塞 TCP，1s 周期天然适合异步 |
 | 测试引擎 | 自定义混合引擎 | 支持线性步 + 状态机感知 + 时序验证 |
 | 数据序列化 | YAML | 可读性好、支持注释，比 JSON 更适合配置 |
 | 协议定义 | Excel + YAML 补丁 | Excel 是上游数据源，UI 修改保存为 YAML 补丁 |
 | 数据库 | SQLite | 零配置、单文件、适合作结果库 |
 | 报告 | openpyxl + Jinja2 + python-docx | 分别对应 CSV/HTML/Word |
 | 打包 | PyInstaller | 导出单 exe，无 Python 依赖 |
 
 ---
 
 ## 三、整体架构
 
 ### 3.1 架构分层
 
 ```
 ┌──────────────────────────────────────────────────────────────┐
 │  UI 层 (PySide6)                                              │
 │  主窗口 | 遥测面板 | 报文监视器 | 用例编辑器 | 项目切换 | 报告   │
 ├──────────────────────────────────────────────────────────────┤
 │  启动层                                                        │
 │  欢迎页 | 新建项目向导 | 项目管理器                              │
 ├──────────────────────────────────────────────────────────────┤
 │  项目管理层                                                     │
 │  ProjectRegistry | SessionManager | ProfileLoader             │
 ├──────────────────────────────────────────────────────────────┤
 │  引擎层 (asyncio)                                              │
 │  SuiteRunner → CaseRunner → StepExecutor                     │
 │  PollingManager | TelemetryRegistry | SafetyGuard            │
 ├──────────────────────────────────────────────────────────────┤
 │  硬件抽象层                                                     │
 │  Transport 接口 | ProtocolCodec 接口                           │
 │  TCPTransport(CURRENT) | CCSDSCodec(CURRENT)                 │
 │  CANTransport(EXT) | CANProtocol(EXT)                        │
 ├──────────────────────────────────────────────────────────────┤
 │  数据层                                                        │
 │  Excel 协议表 | YAML 测试用例 | YAML 用户补丁 | SQLite 结果库   │
 └──────────────────────────────────────────────────────────────┘
 ```
 
 ### 3.2 模块间通信
 
 引擎层和 UI 层通过 **事件总线（EngineSignals）** 解耦通信，核心是 Qt Signal/Slot 机制：
 
 - Polling Loop 收到遥测 → 发射 telemetry_updated 信号 → UI 面板自行消费
 - 用例执行状态变更 → 发射 step_status / case_completed 信号 → 用例树更新着色
 - 安全拦截 → 发射 safety_alert 信号 → 状态栏 / 安全面板显示
 
 引擎不直接操作任何 UI 控件。
 
 ---
 
 ## 四、硬件抽象层
 
 ### 4.1 Transport 接口
 
 ```
 class Transport(ABC):
     """硬件传输抽象——TCP、CAN、串口统一接口"""
     async def connect(self, config: dict) -> bool
     async def disconnect(self)
     async def send(self, data: bytes) -> int
     async def recv(self, timeout_s: float = None) -> bytes | None
     def is_connected(self) -> bool
     transport_type: str  # 'tcp' / 'can' / 'serial'
 ```
 
 当前实现: TCPTransport — asyncio socket 连接串口转以太网通讯盒。
 
 ### 4.2 ProtocolCodec 接口
 
 ```
 class ProtocolCodec(ABC):
     """协议编解码——CCSDS、CAN 帧、Modbus 统一接口"""
     def encode_command(self, cmd_def, seq, params) -> bytes
     def decode_telemetry(self, raw: bytes) -> TelemetryFrame | None
     def get_frame_info(self, raw: bytes) -> FrameInfo
     def calculate_checksum(self, frame: bytes) -> bytes
 ```
 
 当前实现: CCSDSCodec — 支持 CCSDS Space Packet 帧格式：
 - 帧头标识符 EB 90 (2B)
 - 版本号(3bit) + 类型(1bit) + 副导头标识(1bit) + APID(11bit) = 2B
 - 分组标志(2bit) + 源包序列号(14bit) = 2B
 - 数据域长度(2B, 实际长度-1)
 - 指令码(2B) + 可选参数
 - 校验和(2B, 字节 3~10 单字节求和取反)
 
 ### 4.3 CCSDS 帧格式参考
 
 | 字节序号 | 字段 | 值 | 说明 |
 |---------|------|----|------|
 | 0-1 | 标识符 | 0xEB90 | 固定值 |
 | 2 | Version(3) + Type(1) + SubHdr(1) + APID_high(3) | 0x05 | |
 | 3 | APID_low(8) | 0x20 | APID=0x520 |
 | 4 | GroupFlag(2) + SeqCount_high(6) | | 0b11 表示未分段 |
 | 5 | SeqCount_low(8) | 0x00~0xFF | 14-bit 循环累加 |
 | 6-7 | 数据域长度 | | 实际数据长度 - 1 |
 | 8-9 | 指令码(2B) | 如 0x005A | 不同指令不同值 |
 | 10~N | 可选参数 | | 长度由数据域长度决定 |
 | N+1~N+2 | 校验和 | | 3~N 字节和取反 |
 
 ### 4.4 跨项目扩展
 
 换项目时，只需：
 1. 新的 Transport 实现类（如 CANTransport）
 2. 新的 ProtocolCodec 实现类
 3. 新的 Profile 目录（Excel 协议表 + YAML 配置）
 4. 零改动引擎和 UI 代码
 
 ---
 
 ## 五、测试引擎
 
 ### 5.1 运行时并发模型
 
 asyncio 事件循环中运行三个独立协程：
 
 **Task 1: Polling Loop**（常驻）
 - 每包独立状态机：DISABLED / SINGLE / ACTIVE / PAUSED
 - 收到应答 → 位域解析 → 更新 TelemetryCache → 发射信号
 - 支持按包动态切换轮询模式（不轮询/单次查询/持续轮询/暂停）
 
 **Task 2: Test Execution**（按需启动）
 - SuiteRunner 遍历用例集
 - CaseRunner 执行单用例各步骤
 - StepExecutor 根据步骤类型走不同执行路径
 
 **Task 3: Soak Monitor**（浸透模式时启动）
 - 监听遥测更新，设监测阈值，超限发告警
 
 ### 5.2 步骤类型体系
 
 | 步骤类型 | 说明 | 核心配置字段 |
 |---------|------|------------|
 | 发送指令 send_command | 编码并发送一条遥控指令 | 指令选择、参数值、超时、失败动作 |
 | 验证遥测 verify_telemetry | 读取遥测并判断是否符合预期 | 遥测包、参数列表、运算符、预期值、容差 |
 | 等待条件 wait_for_condition | 轮询遥测直到条件满足或超时 | 条件列表、轮询间隔、超时 |
 | 时序验证 timing_verification | 发送指令后在多个时间点验证遥测 | 触发指令、时间点列表(偏移+参数+预期) |
 | 延时等待 delay | 固定时间等待 | 时长 |
 | 脚本步骤 script | 逃生舱，嵌入 Python 脚本 | 脚本内容 |
 | 错误注入 error_inject | 构造异常帧测试 PPCU 边界 | 错误类型 |
 
 ### 5.3 时序验证步骤执行流程
 
 触发指令发出 → 记录 T₀
 监听遥测缓存更新流
 T₀+0s  → 检查 TM1005=推进模式  → ✅ / ❌
 T₀+10s → 检查 TM1006=放气      → ✅ / ❌
 T₀+50s → 检查 TM1022=开        → ✅ / ❌
 所有时间点完成 或 超时 → 汇总结果
 
 ### 5.4 安全保护
 
 - 指令级别拦截：将指令分类（模式切换、参数注入、阀门控制等），可为每类配置禁止发送
 - 高危确认：高危指令（复位、维护模式）每次发送前弹出确认对话框
 - 参数范围校验：参数注入时校验值是否超出有效范围
 - 执行拦截记录：被拦截的指令记入日志和报告中
 
 ### 5.5 序列号管理
 
 SRM 自动维护 CCSDS 14-bit 源包序列号（0x0000~0x3FFF 循环累加），指令发出时自动填入，不要求用户手动维护。
 
 ---
 
 ## 六、遥测系统
 
 ### 6.1 PollingManager 状态机
 
 每个遥测包独立运行一个状态机实例。UI 提供每包的操作按钮：[▶一次] [●持续轮询] [⏸暂停]。
 
 状态转换：DISABLED → SINGLE → DISABLED ; DISABLED → ACTIVE → PAUSED → ACTIVE ; ACTIVE → PAUSED → ACTIVE
 
 ### 6.2 TelemetryRegistry（运行时可动态增删）
 
 启动时从 Excel 加载协议表，UI 层"遥测包管理器"支持：
 - 新增遥测包（手动定义或导入 Excel）
 - 删除已废弃的包
 - 修改现有包的参数（增删字段）
 - 所有修改导出为 YAML 补丁文件，不修改 Excel 源文件
 
 ### 6.3 混合轮询策略
 
 | 帧类型 | 描述 | 默认策略 | 用例执行时 |
 |--------|------|---------|-----------|
 | 快帧（常规包1/2） | PPCU 周期上报 | 开启 1s 轮询 | 直接读缓存 |
 | 慢帧（查询包1/2） | 需主动查询 | 关闭 | 按需发单次查询 |
 
 ---
 
 ## 七、项目管理系统
 
 ### 7.1 Device Profile 结构
 
 profiles/<project_name>/
 ├── profile.yaml           # 项目元信息 + 通讯/协议配置
 ├── safety.yaml            # 安全策略
 ├── telemetry/             # 遥测包定义 (Excel + YAML 补丁)
 ├── commands/              # 指令定义 (Excel)
 ├── injections/            # 参数注入定义 (Excel)
 └── cases/                 # 测试用例 (YAML)
 
 ### 7.2 切换体验
 
 - 欢迎页：启动时展示项目列表（卡片式），显示基本信息
 - 运行时下拉切换：主窗口标题栏常驻项目下拉框，切换时热加载配置 + 自动重连
 - 新建向导：4 步（基本信息 → 通讯方式 → 协议 → 数据导入）
 - 项目管理器：项目列表、增删改查、导出导入
 
 ### 7.3 跨项目扩展步骤
 
 | 步骤 | 操作 | 代码工作量 |
 |------|------|-----------|
 | 标准通讯方式切换 | 在向导中选择 TCP/CAN/串口 | 零代码 |
 | 自定义通讯方式 | 编写 Transport + ProtocolCodec 实现 | ~500 行 |
 | 新设备协议表 | 按模板填写 Excel 表 | 纯数据工作 |
 | 引擎和 UI | 完全复用 | 零代码 |
 
 ---
 
 ## 八、UI 界面设计
 
 ### 8.1 主窗口布局
 
 标题栏(项目切换下拉 + 连接状态)
 菜单栏
 工具栏(运行/停止/报告/安全)
 左侧: 用例树 | 中央: 遥测面板(数据表/趋势图) + 轮询控制 | 右侧: 报文监视器
 底部: 用例编辑器 / 执行详情（可折叠）
 状态栏
 
 ### 8.2 核心交互
 
 - 遥测面板：双列显示（原始值 hex + 物理值工程单位）、按包分组/过滤/搜索、趋势图实时曲线
 - 报文监视器：逐行着色显示（蓝色=发送、绿色=接收通过、红色=接收失败）、结构化表格、导出 pcap
 - 用例编辑器：双模式（表单模式 + YAML 源码模式），双向实时同步
 - 进度面板：用例树节点状态着色（✅/❌/⏳/⏸/➖/🔒），正在执行的步骤高亮
 - 安全面板：指令分类拦截开关、高危确认配置、拦截日志
 
 ### 8.3 事件总线信号列表
 
 connection_changed(bool, str)
 telemetry_updated(str, list)           # (包名, 参数更新列表)
 polling_mode_changed(str, str)         # (包名, 新模式)
 raw_frame_sent(str, str)               # (时间戳, hex)
 raw_frame_received(str, str, bool)     # (时间戳, hex, 校验结果)
 suite_started(str)
 case_started(str, int, int)            # (用例名, 索引, 总数)
 step_status(str, str, str, str)        # (用例名, 步骤ID, 步骤名, 状态)
 case_completed(str, float, str)        # (用例名, 耗时, 结果)
 suite_completed(str, int, int, int)    # (套件名, 通过, 失败, 跳过)
 safety_alert(str, str)                 # (级别, 消息)
 command_blocked(str, str)              # (指令名, 原因)
 project_changed(str)                   # 新项目名
 error_occurred(str, str)               # (来源, 消息)
 
 ---
 
 ## 九、测试用例系统
 
 ### 9.1 YAML 用例格式
 
 ```yaml
 name: 待机→正常点火模式切换
 description: 从待机模式切到正常点火，验证模式字与阶段时间
 tags: [mode, functional]
 
 setup:
   - action: connect
     profile: default
 
 steps:
   - id: S01
     name: 发送模式切换指令
     action: send_command
     command: TCHEDTTA003_2
     timeout_s: 3
   
   - id: S02
     name: 验证模式切换
     action: verify_telemetry
     package: 常规包1
     checks:
       - parameter: TM1005
         operator: equals
         expected: 推进模式
 
   - id: S03
     name: 时序验证
     action: timing_verification
     trigger_command: TCHEDTTA003_2
     timeout_s: 60
     timepoints:
       - offset: +0s
         package: 快帧
         checks:
           - parameter: TM1005
             operator: equals
             expected: 推进模式(0x01)
       - offset: +10s
         package: 快帧
         checks:
           - parameter: TM1006
             operator: equals
             expected: 下游供气管路放气
 ```
 
 ### 9.2 编辑器界面
 
 表单模式：左侧步骤列表（可拖拽排序），右侧动态步骤配置表单（按步骤类型切换），条件通过"添加条件行"方式配置，每个条件 = 参数 + 运算符 + 预期值 + 容差。
 
 YAML 源码模式：语法高亮文本编辑器，与表单模式双向同步。
 
 ### 9.3 参数化测试
 
 在 YAML 中用 params 声明输入参数（类型、范围、默认值），UI 自动渲染对应输入控件。
 
 ---
 
 ## 十、报告系统
 
 ### 10.1 三件套报告
 
 | 格式 | 定位 | 核心内容 |
 |------|------|---------|
 | CSV | 数据层面/Excel 分析 | 每条原子校验一行（配置→预期→实际→结果） |
 | HTML | 交互查看/分享 | 可折叠卡片、搜索过滤、失败高亮、问题记录 |
 | Word | 正式归档/签字 | 完整测试记录单、环境信息、问题描述、签字栏 |
 
 ### 10.2 每条记录的完整链路
 
 每条步骤报告包含：
 1. 配置快照（UI 上配置的条件完整序列化）
 2. 实际结果（运行中采集的实际值、时间戳）
 3. 结论（通过/失败/跳过）
 4. 失败详情（预期 vs 实际 vs 偏差 + 问题描述）
 
 ### 10.3 问题记录区
 
 每个失败用例自动生成问题描述块，包含：
 - 问题编号（ISSUE-YYYYMMDD-NNN）
 - 严重程度、问题现象、复现步骤、原因分析、处置建议
 
 ### 10.4 SQLite 结果库
 
 test_runs 表和 case_results 表，支持历史趋势查询和版本追溯。
 
 ---
 
 ## 十一、数据配置系统
 
 ### 11.1 四层配置
 
 | 层级 | 位置 | 格式 | 说明 |
 |------|------|------|------|
 | 0: 内置默认值 | src/config/defaults/ | Python dataclass | 基础回退值 |
 | 1: Profile YAML | profiles/<project>/*.yaml | YAML | 项目级配置 |
 | 2: Excel 协议表 | profiles/<project>/telemetry/*.xlsx | Excel | 协议级数据 |
 | 3: 用户运行时补丁 | user_overrides.yaml | YAML | UI 增删改生成，不修改 Excel |
 
 ### 11.2 加载流程
 
 Excel 加载 → 校验合法性 → 合并 YAML 补丁 → 构建运行时注册表
 
 ---
 
 ## 十二、安全保护
 
 | 保护层 | 机制 | 适用范围 |
 |--------|------|---------|
 | 指令分类拦截 | 按类别禁止发送特定指令 | 全局 |
 | 高危确认 | 每次发送前弹出确认对话框 | 高危指令 |
 | 参数范围校验 | 注入参数超限则拦截 | 参数注入步骤 |
 | 执行中保护 | 用例执行时自动启用 | 所有用例 |
 | 拦截日志 | 被拦截指令记录到日志和报告 | 全局 |
 
 保护策略通过每个项目的 safety.yaml 单独配置，项目切换时自动切换。
 
 ---
 
 ## 十三、实现路线图
 
 ### Phase 0: 项目脚手架 (~2天)
 目录结构、数据模型 dataclass、类型枚举、requirements.txt、PyInstaller 配置、git 初始化
 
 ### Phase 1: 核心引擎 (~7天) 核心里程碑
 ExcelLoader / ProfileLoader / SchemaValidator
 Transport + ProtocolCodec 抽象 + TCPTransport + CCSDSCodec
 BitFieldParser / TelemetryRegistry / PollingManager / TelemetryCache
 SafetyGuard / SeqManager / StepExecutor / CaseRunner / SuiteRunner
 CLI 验证脚本 — 不依赖 UI 跑通完整测试循环
 
 ### Phase 2: 基础 UI (~7天)
 MainWindow / EngineSignals 事件总线 / App 组装
 TelemetryTableView / PollingControlBar / MessageMonitor
 SafetyPanel / 连接状态栏 / QSS 样式
 
 ### Phase 3: 用例系统 (~5天)
 TestSuiteTree / TestCaseEditor / 各步骤编辑器 Widget
 TimingVerificationEditor / YAML 双向编辑
 ExecutionProgressPanel
 WelcomePage / ProjectManagerDialog / NewProjectWizard
 SessionManager / 运行时项目切换
 
 ### Phase 4: 报告系统 (~4天)
 CSVReporter / HTMLReporter(Jinja2) / WordReporter
 ReportManager / ResultDatabase(SQLite)
 报告 UI 入口 / 历史结果视图
 
 ### Phase 5: 增强 + 打包 (~5天)
 趋势图(QChart) / 浸透模式 / 报文录制(pcap)
 错误注入 / 脚本步骤 / 远程轻量监视
 PyInstaller 打包 exe / 用户手册
 
 ---
 
 ## 十四、关键技术决策记录
 
 | 决策 | 结果 | 理由 |
 |------|------|------|
 | GUI 框架 | PySide6 (非 PyQt6) | LGPL 免费商用，适合 PyInstaller 打包 |
 | 测试用例格式 | YAML (非 JSON) | 可读性好、支持注释 |
 | 协议数据源 | Excel + YAML 补丁 | Excel 是用户现有数据源，YAML 补丁不破坏源文件 |
 | 遥测轮询 | 可控模式（每包独立状态机） | 避免非必要轮询导致通讯堵塞 |
 | 遥测注册表 | 运行时可动态增删 | 固件升级可能增加新包 |
 | 跨项目支持 | Device Profile 机制 | 更换通讯方式只需新 Transport + Profile |
 | 事件通信 | Qt Signal (非自定义事件循环) | 与 Qt 深度集成，减少耦合 |
 | 报告格式 | CSV + HTML + Word | 分别满足数据/交互/归档三个场景 |
 
 ---
 
 ## 十五、文件清单
 
 ### 源文件目录
 
 src/ — 应用源码
 src/core/ — 核心引擎和硬件抽象
 src/config/ — 配置加载器
 src/ui/ — PySide6 界面
 src/reporters/ — 报告生成
 src/utils/ — 工具函数
 
 ### 配置目录
 
 profiles/ppcu_rs422/ — PPCU RS422 项目配置
 profiles/generic_template/ — 新项目模板
 
 ### 其他
 
 data/ — 运行时数据
 reports/ — 报告输出
 tests/ — 单元测试
 scripts/ — 脚本工具
 docs/ — 文档
