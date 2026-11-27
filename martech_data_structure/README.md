# Martech 数据结构设计

本目录采用 **Snowplow 风格的 event-based / 元数据建模范式**，用于设计 GTM 运营系统所需的数据结构：**事实（Event Log）→ 维度（Person/Company/Content/Campaign）→ 派生（Score/Lifecycle/Attribution）**。  
对外可表述为**两层建模**：**第一层 = 唯一事实来源（event_log + 维表）**；**第二层 = 可按分析需求替换的语义层（派生模型 + 规则/口径）**。详见 [design.md §1 两层建模](design.md#两层建模对外表述)。

## 设计原则（三条铁律）

1. **Event Log 是唯一事实来源**：所有行为进事件表，统计/漏斗/得分均从事件重算。
2. **事件里只放“坐标”**：事件存 ID 与关键字段，详情在维表。
3. **Lifecycle/Attribution 是算出来的切片**：可重算、可解释、可追溯。

**设计保证**（详见 [design.md §2](design.md#2-设计保证为什么不怕规则变、指标变、业务换说法)）：行为比状态更重要；多源异构只做 Connector 映射；规则/指标/业务说法变更时只改派生逻辑，不改 event 层——**不怕规则变、不怕指标变、不怕业务换说法**。

## 文件索引

| 文件 | 说明 |
|------|------|
| [marketing_automation_requirements.md](marketing_automation_requirements.md) | **Marketing Automation 全套需求**（2026 MarTech & Event Strategy）：核心目标、技术/数据、Campaign/Sales、报表、实施与 Sprint 0，与架构图及本目录数据模型对齐 |
| [design.md](design.md) | 设计说明：与 GTM 架构图对应、两条建模、三条铁律、事件分类、表职责、派生模型逻辑 |
| [event_taxonomy.yaml](event_taxonomy.yaml) | 事件语言（4 类来源）+ v0 最小闭环 + 计分规则示例 |
| [schema_v0.yaml](schema_v0.yaml) | 表结构定义（1 事实表 + 5 维表 + 3 派生表），可读版 |
| [schema_v0.md](schema_v0.md) | 表结构说明 **Markdown 版**（Customer/Content/Campaign 等维表与事实表、派生表字段一览） |
| [schema_v0.sql](schema_v0.sql) | Postgres/Supabase 建表 DDL，可直接执行 |
| [customer_dimension_guide.md](customer_dimension_guide.md) | **Customer 维表维护**：表单字段映射、source 区分来源、手动上传历史库去重与维护要点 |
| [content_library_design.md](content_library_design.md) | **Content Library 设计**：为何用维表、字段与扩展建议、与 event_log 的配合 |
| [supabase_integration_guide.md](supabase_integration_guide.md) | **通过 Supabase 连接所有数据**：各源如何写入 Supabase、Connector 实现方式、实施顺序 |
| [fact_layer_source_mapping.md](fact_layer_source_mapping.md) | **事实层与多数据源映射**：GA4、LinkedIn、HubSpot 等事件 → event_log 的 event_type / source / channel / properties |
| [source_event_mapping.yaml](source_event_mapping.yaml) | 各源事件 → event_log 的机器可读映射（供 Connector/配置使用） |
| [assets/GTM_architecture.png](assets/GTM_architecture.png) | GTM 架构图：Integration Layer → Marketing Data Layer → Dashboard |

## 表结构总览

- **事实表**：`event_log`（谁在何时通过什么内容/活动做了什么）
- **维表**：`person`、`company`、`content`、`campaign`、`touchpoint_source`（可选）
- **派生表**：`lead_score_daily`、`lifecycle_state`、`attribution_summary`（可选 v0）

## 与项目其他目录的关系

- `raw_data/`、`channel_data/`：原始技术栈/渠道数据，可作为 Connectors 的输入
- `output_data/`、`Information/structured_data/`：结构化输出，可与本 schema 做映射
- `companyAnalysis/`：Martech 分析结论，用于校验事件类型与维表口径

## 使用方式

1. 阅读 [design.md](design.md) 和 [event_taxonomy.yaml](event_taxonomy.yaml) 理解事件语言与表职责。
2. 在 Supabase/Postgres 中执行 [schema_v0.sql](schema_v0.sql) 建表。
3. Connectors 只写 `event_log` 与维表；Dashboard 查询 Event Log + 维表，或使用派生表（由 job/ dbt 等从 event 重算）。
