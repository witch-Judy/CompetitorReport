# Marketing Automation 全套需求（2026 MarTech & Event Strategy）

本文档整合 **2026 全球展会与 campaign** 下的 MarTech / 营销自动化需求，供选型、实施与对外沟通使用。需求与现有 **GTM 数据架构**（[design.md](design.md)、[assets/GTM_architecture.png](assets/GTM_architecture.png)）及 **Supabase + HubSpot + Teams** 技术栈对齐，便于落地时与事件模型、维表、Connector 一致。

**参考来源**：2026 MarTech & Event Strategy Requirements（内部需求摘要）；**架构参考**：本目录 GTM 架构图与 Snowplow 范式数据结构。

### 已有 / 已确定技术栈（Current stack）

| 层级/角色 | 技术栈 | 说明 |
|-----------|--------|------|
| **数据库** | **Supabase**（Postgres，等待建成） | 唯一落库：event_log + 维表（person、company、content、campaign、touchpoint_source）及派生表（lead_score_daily、lifecycle_state、attribution_summary）。见 [schema_v0.sql](schema_v0.sql)、[schema_v0.md](schema_v0.md)。 |
| **CRM 与营销自动化** | **HubSpot**（Enterprise 优先） | 主 CRM/MA；事件与线索经 Connector 写入 Supabase 或与 HubSpot 同步。工作流、表单、邮件、Breeze AI（或同等）得分。 |
| **内容文件存储** | **Microsoft Teams**（OneDrive / SharePoint） | 文件本体在 Teams；Supabase **content** 表只存元数据与 **file_url**（Teams 分享链接）。Supabase 与 Teams 对接已就绪。见 [content_library_design.md](content_library_design.md)。 |
| **事件/行为来源** | **GA4**（BigQuery 或 Reporting API）、**HubSpot**（API/Webhook）、**LinkedIn**（API/Insight Tag）、**展会线索工具**（如 Zuant、Cvent）、**网站表单**、**CSV/手动上传** | 经 Connector 统一映射进 **event_log**；见 [fact_layer_source_mapping.md](fact_layer_source_mapping.md)、[supabase_integration_guide.md](supabase_integration_guide.md)。 |

新增能力（如 Chatbot、内容编辑用 CMS）需与上述技术栈集成；§2.5 营销自动化具体能力需与 HubSpot 及本数据模型对齐。

---

## 1. 核心目标（Core Objective）

| 需求 | 说明 | 与现有架构的对应 |
|------|------|------------------|
| **统一 CRM + 营销自动化** | 以统一平台支撑 2026 全球展会与 campaign，**HubSpot Enterprise 优先**。 | 事件与线索以 **event_log** + **person** / **company** 为统一事实与维度；HubSpot 作为主要 MA 源之一，通过 Connector 写入 Supabase 或与 HubSpot 原生对象同步。 |
| **拦截竞品线索** | 从 legacy 竞品（ABB、Honeywell、Emerson 等）手中拦截 leads，并支撑**置换（displacement）** 内容与转化路径。 | **Competitor Intelligence** 需在 person/company 或 Custom Object 中体现“当前在用竞品系统”（见 §2.1）；触发自动化置换内容与培育流程。 |
| **闭环 ROI 报告** | 对 Hannover Messe、GasTech、ADIPEC 等**重点展会**实现从获客到成单的闭环 ROI 可衡量。 | **多触点归因**（first touch → closed-won）与 **event_log + 派生表**（attribution_summary、lifecycle_state）支撑；见 §4。 |

---

## 2. 技术与数据需求（Technical & Data Requirements）

### 2.1 竞品情报映射（Competitor Intelligence Mapping）

| 需求 | 说明 | 落地建议 |
|------|------|----------|
| **Current Installed Base** | 能记录线索/客户**当前使用的竞品系统**（如 ABB、Honeywell、Emerson 等），并据此触发**自动化置换内容**。 | 在 **company** 或 **person** 维表增加字段（如 `current_competitor`、`installed_base`）或 HubSpot Custom Object；工作流/培育规则根据该字段推送置换类 content（content 维表 + event_log 的 content_id）。 |
| **置换内容自动化** | 根据竞品标签自动匹配并推送 displacement 白皮书、案例、对比材料。 | Content Library（content 表）中内容打 tag 或 campaign 与“竞品置换”关联；MA 工作流根据 person/company 的竞品字段 + event 行为触发对应 content 与 campaign。 |

### 2.2 区域架构（Regional Architecture）

| 需求 | 说明 | 落地建议 |
|------|------|----------|
| **独立 BU** | 支持 **SEA、Europe、NA、Middle East** 等独立业务单元，各自**线索路由、语言分区、数据合规**。 | **person** / **company** 维表需有 **region** / **business_unit**（及 country、language）；路由与权限规则按 region 分区；event_log 的 **properties** 或维表存 language/region，便于分区报表与合规。 |
| **本地化线索路由** | 各区域 leads 自动路由至对应区域销售/市场。 | 基于 person/company 的 region/country 配置工作流与分配规则；Hot leads 推送 Sales 时带 region 信息（与 §3.1 SLA 结合）。 |
| **区域数据隐私** | 满足各区域数据驻留与隐私要求。 | 数据存储与访问策略按 region 设计；Supabase 与 HubSpot 配置需支持区域策略；event 与 person 数据分区可查、可审计。 |

### 2.3 高速线索接入（High-Speed Lead Integration）

| 需求 | 说明 | 落地建议 |
|------|------|----------|
| **展会线索工具对接** | 与 **Zuant、Cvent** 等展会 lead-capture 工具**无缝 API 对接**，实现 **Speed-to-Lead &lt; 4 小时**（从展台扫码到销售触达）。 | 展会工具 → API/Webhook → **Connector** → 写入 **person** / **company** + **event_log**（如 event_type=form_submitted 或 event_type=event_lead_captured）；写入格式见 [supabase_integration_guide.md §3](supabase_integration_guide.md#3-各来源数据以什么格式连进来)。 |
| **统一落库** | 展会线索与线上表单、HubSpot、GA 等统一进入同一套 **event_log + 维表**，便于归因与得分。 | 所有来源经映射后写 Supabase（或 HubSpot 为主时同步到 Supabase）；external_ref 防重；见 [fact_layer_source_mapping.md](fact_layer_source_mapping.md)。 |

### 2.4 线索得分与 AI（Lead Scoring & AI）

| 需求 | 说明 | 落地建议 |
|------|------|----------|
| **预测性线索得分** | 使用 **HubSpot Breeze AI**（或同等能力）基于**展会参与度与意图信号**对线索排序与优先级划分。 | 意图与参与度来自 **event_log**（展会签到、下载、表单、邮件点击等）；得分结果可落 **lead_score_daily** 或 HubSpot 原生得分；语义层可重算、可解释（见 [design.md](design.md)）。 |
| **事件驱动得分** | 得分规则基于行为事件，可配置、可迭代。 | event_taxonomy 与计分规则（如 [event_taxonomy.yaml](event_taxonomy.yaml) 的 scoring_rules_v0）由 MA 或批任务从 event_log 重算；Breeze AI 可与 event 特征结合。 |

### 2.5 营销自动化具体能力（更细需求）

在“统一 CRM + MA”之下，供应商/实施方需具备以下**具体能力**，并与 event_log、维表及工作流对齐：

| 能力 | 需求要点 | 与数据架构的对应 |
|------|----------|------------------|
| **Email Marketing** | 邮件触达、模板、A/B 测试、打开/点击追踪、退订与合规（如区域 consent）；支持按 segment（区域、竞品、得分）发信。 | 邮件行为（打开、点击、退订）作为事件写入 **event_log**（event_type 如 email_opened、email_clicked），source=hubspot；**person** 维表支撑分群与去重；见 [fact_layer_source_mapping.md](fact_layer_source_mapping.md)。 |
| **Lead Nurturing** | 基于行为与属性的自动化培育流程（如下载白皮书 → 系列邮件；展会留资 → 欢迎序列 + 置换内容）；支持按生命周期阶段与得分分支、节奏控制。 | 培育触发的行为来自 **event_log**（form_submitted、content_downloaded、email_clicked 等）；**lifecycle_state**、**lead_score_daily** 支撑分支与节奏；内容来自 **content** 维表；工作流为“语义层”的执行层（HubSpot Workflow 或等价）。 |
| **Campaign Management** | 跨渠道 campaign 的创建、排期、受众与预算；与展会、线上、ABM 等统一命名与归因；支持按 campaign 维度报表。 | **campaign** 维表存 campaign 元数据（name、时间、objective、channel_mix）；**event_log.campaign_id** 关联行为与 campaign；归因与报表按 campaign 聚合，见 **attribution_summary** 与 §4。 |
| **Chatbot / 对话式营销** | 网站或产品内**聊天机器人**：预约会议、自动甄别线索；对话结束后自动触发邮件序列；用 CRM 数据个性化话术；可配置对话流程、无需代码；界面可随网站/产品主题定制。 | 对话行为（如会话开始/结束、预约成功）可落 **event_log**（如 chat_started、chat_ended、meeting_booked）；触发邮件序列与 **Lead Nurturing**、**Email Marketing** 一致；person 维表支撑个性化与线索识别。 |

以上四项为**更具体的需求**，选型与 Sprint 0 时需明确平台是否覆盖，并与本目录事件模型、维表及派生表一致。

---

## 3. Campaign 与 Sales 协同（Campaign & Sales Alignment）

### 3.1 自动化 SLA 与升级（Automated SLAs）

| 需求 | 说明 | 落地建议 |
|------|------|----------|
| **跟进时效** | 工作流自动跟踪并**强制销售跟进时效**；若 **Hot** 展会线索在约定时间内未被联系，触发**升级告警**。 | 从 **lifecycle_state** 或 HubSpot 状态 + **event_log**（如 event_lead_captured、form_submitted）计算“分配时间”；超时未联系则触发通知/升级；Hot 定义可与 lead_score_daily 或 Breeze AI 得分一致。 |
| **可追溯** | 升级与 SLA 违反可追溯到具体线索与事件。 | 派生表 **lifecycle_state.reason** 存导致状态变化的事件引用；SLA 逻辑可基于 event 时间戳与分配时间差。 |

### 3.2 全渠道拦截与 ABM（Omnichannel Intercepts）

| 需求 | 说明 | 落地建议 |
|------|------|----------|
| **地理围栏与 ABM** | 能执行**地理围栏数字广告**与 **ABM**，针对参加特定 2026 全球展会的**大客户**进行定向触达。 | **campaign** 维表与 event_log 的 campaign_id、channel 支持“展会 + 区域 + ABM 名单”；person/company 与 region、account 标签配合投放与归因；多源事件（GA、LinkedIn、HubSpot）统一进 event_log 做归因。 |
| **展会场景** | 与 Hannover Messe、GasTech、ADIPEC 等场馆/时间结合。 | campaign 或 content 与“展会/场馆”关联；event 的 properties 或维表存 event_venue、event_date，便于报表与归因。 |

### 3.3 销售赋能（Sales Enablement）

| 需求 | 说明 | 落地建议 |
|------|------|----------|
| **移动优先 CRM** | 为一线团队提供**移动优先**的 CRM 界面，在**展会现场**管理线索、查看**竞品 Battlecards**。 | CRM 侧（HubSpot 或与 Supabase 同步的界面）提供移动端；Battlecards 与 **current_competitor** / installed_base 关联，按竞品类型展示；内容可来自 Content Library（content 表）或 Teams。 |
| **现场线索与 Battlecards** | 展台扫码/留资后，销售可即时看到线索摘要与应对话术。 | 展会 Connector 写入 person/company + event_log 后，CRM/移动端实时或近实时展示；竞品字段驱动 Battlecard 推荐。 |

---

## 4. 报表与分析需求（Reporting & Analytics Requirements）

供应商需能搭建 **2026 Command Center Dashboard**，并支持以下能力：

| 需求 | 说明 | 与现有架构的对应 |
|------|------|------------------|
| **多触点归因（W 型）** | 从 **first touch** 到 **closed-won** 的营收归因，支持 W 型权重。 | **event_log** 为事实来源；**attribution_summary**（或等价派生表）存 first_touch_channel、last_touch_channel、influencing_events；Dashboard 查询 event_log + 维表，归因模型（含 W 型）在语义层重算，见 [design.md](design.md)、[schema_v0.md](schema_v0.md)。 |
| **竞品置换胜率** | 分析**从哪些竞品 installed base 成功转化**，展示 Competitor Displacement Win-Rate。 | 维表 **company** / **person** 的 current_competitor / installed_base + **lifecycle_state** 或成单结果；报表按竞品维度聚合转化率与营收。 |
| **区域管道速度** | **Regional Pipeline Velocity**：各区域/国家线索**流转速度**的对比分析。 | **event_log** 的 occurred_at + **lifecycle_state** 的 stage_updated_at，按 person/company 的 region 聚合“从留资到 MQL/SQL/成单”的时长分布；Dashboard 按 region/BU 对比。 |
| **Command Center** | 单一指挥中心视图：展会、campaign、线索质量、跟进 SLA、归因与 pipeline。 | Dashboard 数据源 = **event_log** + **person** / **company** / **content** / **campaign** + **lead_score_daily** / **lifecycle_state** / **attribution_summary**；可接 Supabase 或经 HubSpot 报表扩展实现。 |

---

## 5. 实施与 Sprint 0（Implementation & Sprint 0 Expectations）

| 需求 | 说明 | 落地建议 |
|------|------|----------|
| **Sprint 0 Discovery** | 专项阶段：将 **2026 展会日历** 与 **CRM 数据模型** 对齐，明确事件类型、属性与报表口径。 | 用本目录 **event_taxonomy.yaml**、**schema_v0** 与 [fact_layer_source_mapping.md](fact_layer_source_mapping.md) 作为数据模型基线；将 2026 各展会、campaign 映射到 campaign 维表与 event_type；确定 Zuant/Cvent 等输入格式与 Connector 规范。 |
| **数据迁移** | 历史线索数据的**清洗与导入**策略。 | 参考 [customer_dimension_guide.md](customer_dimension_guide.md)：person/company 的 source、去重规则（email、company_name）、批量导入的 source 标识（如 import_202601）；历史行为若可还原可落 event_log，否则仅做维表补齐。 |
| **培训** | 面向区域市场与销售负责人的 **Train-the-Trainer** 全球培训。 | 覆盖：统一数据模型（事件 + 维表）、HubSpot 与 Supabase 使用、展会线索接入流程、SLA 与 Battlecards、Command Center 与归因解读；可引用本目录文档为技术参考。 |

---

## 6. 与现有数据架构的对应关系

- **事实与维度**：本需求中的“线索、行为、竞品、区域、展会、campaign”均对应 [design.md](design.md) 中的 **event_log** 与 **person** / **company** / **content** / **campaign** 维表；Custom Object（如竞品）可扩展维表或 HubSpot 对象后与 event 关联。
- **数据落点**：所有 Connector 写入 **Supabase**（或 HubSpot 与 Supabase 同步），文件存 **Teams**，见 [supabase_integration_guide.md](supabase_integration_guide.md)、[content_library_design.md](content_library_design.md)。
- **得分、生命周期、归因**：均为由 **event_log** 重算的**派生层**，规则可配置、可替换，见 [design.md §2 设计保证](design.md#2-设计保证为什么不怕规则变、指标变、业务换说法)。
- **与 Sales 的边界**：系统负责培育与推送 Hot leads；Sales 跟进、SLA、Battlecards 为协同能力，闭环成单数据通过反馈回写或 CRM 同步支撑归因与竞品胜率报表，见 [design.md §1 与 Sales 的边界](design.md#与-sales-的边界scope)。

---

## 7. 现有/已建数据库与规模（Database & Size）

本需求所依托的**已有数据架构**即本目录定义的 schema（[schema_v0.sql](schema_v0.sql)、[schema_v0.md](schema_v0.md)）：事实表 **event_log**、维表 **person / company / content / campaign / touchpoint_source**、派生表 **lead_score_daily / lifecycle_state / attribution_summary**，落库在 **Supabase**（Postgres）。

**建议在需求与选型中明确现有数据库的规模（Size）**，便于供应商与实施方评估容量、性能与迁移范围：

| 维度 | 说明 | 示例/待补充 |
|------|------|-------------|
| **库类型** | 当前生产/预发库 | 如 Supabase (Postgres 15) |
| **表数量** | 事实表 + 维表 + 派生表 | 1 事实 + 5 维 + 3 派生（见 schema_v0） |
| **event_log 行数** | 事件总量（当前或年预期） | 如 10^6 / 年、10^7 累计 |
| **person / company 行数** | 联系人/公司主数据量 | 如 10^5 person、10^4 company |
| **content 行数** | 内容资产条数 | 如 10^3 级 |
| **存储占用** | 库总大小或按表统计 | 如 xx GB（可填实际 Supabase 统计） |
| **保留策略** | event_log 保留时长、是否分区/归档 | 如 2 年热数据 + 归档 |

上表示例可替换为**实际环境的数据**；若尚未上线，可填“预期规模”并标注。将上述数据库与规模写进需求文档，有利于 Sprint 0 数据迁移、Command Center 与 Connector 的容量规划。

---

## 8. 文档索引（本目录）

| 文档 | 用途 |
|------|------|
| [design.md](design.md) | 数据架构与两条建模、三条铁律、事件分类 |
| [schema_v0.md](schema_v0.md) / [schema_v0.sql](schema_v0.sql) | 表结构及建表 DDL |
| [event_taxonomy.yaml](event_taxonomy.yaml) | 事件类型与计分规则示例 |
| [customer_dimension_guide.md](customer_dimension_guide.md) | 客户维表与导入规范 |
| [content_library_design.md](content_library_design.md) | Content Library 与 Teams 角色 |
| [fact_layer_source_mapping.md](fact_layer_source_mapping.md) | 多源事件 → event_log 映射 |
| [supabase_integration_guide.md](supabase_integration_guide.md) | 通过 Supabase 连接各源与输入格式 |
| [assets/GTM_architecture.png](assets/GTM_architecture.png) | GTM 架构图 |

本文档为 **Marketing Automation 全套需求** 的汇总，可与上述技术文档配合用于选型、Sprint 0 与实施落地。**§7 现有/已建数据库与规模** 请按实际或预期数据补充后提供给供应商或实施团队。
