# Martech 数据结构设计说明（Snowplow 范式）

## 1. 目标与架构对应

**业务目标**（与 GTM 架构图一致）：  
构建统一的、AI 就绪的 GTM 运营系统，通过**数据、自动化与持续学习**，把市场注意力转化为可预测、可合格的收入。

**数据建模角色**：

| 层级 | 含义 | 在架构图中的对应 |
|------|------|------------------|
| **事实（Fact）** | 发生了什么 | Integration Layer 汇入的 **Event Log**（谁在何时通过什么内容/活动做了什么） |
| **维度（Dimension）** | 参与者、内容、活动、渠道 | Marketing Data Layer 中的 **Customer (Person, Company)**、**Content+Resource Library**、**Campaign** |
| **派生（Derived Models）** | 从事件“算出”的结论 | Dashboard 的 **Lead Score**、**lead_lifecycle_state**、**Attribution analysis**、**Nurture Decision Engine** |

设计原则：**先记全事件 → 再用模型算出指标/状态 → 指标可重算、可解释、可追溯**。

### 两层建模（对外表述）

对外可以这样理解：我们做了**两层建模**。

| 层 | 名称 | 内容 | 特点 |
|----|------|------|------|
| **第一层** | **事实层**（唯一事实来源） | `event_log` + 维表（person / company / content / campaign）。只记录“谁在何时做了什么”以及参与者、资源的实体属性。 | **稳定**：不随分析需求或业务说法改变；多源异构只通过 Connector 写入这一层。 |
| **第二层** | **语义层** | 基于事实层**算出来**的派生模型（lead_score_daily、lifecycle_state、attribution_summary）以及支撑它们的规则、口径、指标定义（如 event_taxonomy 里的计分规则、MQL 定义、归因模型）。 | **可按分析需求替换**：换一套 lead scoring、换一套 MQL 定义、换一套归因模型，只改这一层逻辑或配置，事实层不变。 |

一句话总结：**事实层是唯一真相；语义层是可替换的分析口径。**  
Dashboard、Nurture 决策、归因报告等“对外输出”都建立在语义层之上，语义层可随时按业务或分析需求迭代，而不动底层事实。

### 与 Sales 的边界（Scope）

本系统**不包含严格的 Sales 逻辑**（如商机阶段、管道、成单闭环等）。与 Sales 的交互只有一条清晰路径：

- **输出**：培育效果较好的 leads（含全量信息）推送给 Sales。
- **回流**：Sales 过一段时间后返回结果（反馈）；根据该 **feedback** 长期更新培育机制、得分规则、内容策略等。

因此：事实层与语义层以**营销/培育**为主；Sales 作为**外部消费者 + 反馈来源**，不在此系统内建完整销售数据模型。若将来收到 Sales 的反馈（如“已联系/已转化/无效”），可以按需落成少量事件（如 `sales_feedback_received`）用于优化培育，但**不需要**在本系统内建模商机、阶段、管道等严格销售逻辑。

---

## 2. 设计保证：为什么不怕规则变、指标变、业务换说法

本结构针对三类现实需求做了专门设计，对应关系如下。

| 需求 | 设计如何满足 | 结果 |
|------|----------------|------|
| **行为比“状态”更重要**（营销/增长/归因都依赖行为） | 唯一事实是 **event_log**；状态（MQL/SQL、得分、阶段）全部是**从事件算出来的派生表**，不单独维护“状态真相”。归因、漏斗、得分都查事件 + 重算。 | 行为是唯一真相，状态永远可追溯到“哪几条事件导致”。 |
| **数据源多且异构**（GA / LinkedIn / HubSpot / 扫名片 等） | 所有来源通过 **Connectors + Mapping** 统一写成 **event_log** 一行行事件；用 `source`、`channel`、`properties`(jsonb)、`external_ref` 区分来源与原始 payload，维表统一 person/company/content/campaign。 | 多源异构只影响接入层映射，底层模型不变；新加一个数据源 = 新加一个 connector，不改表结构。 |
| **未来规则会变**（lead scoring / lifecycle 定义会调整） | **Lead score、lifecycle、attribution 都是派生表**，由批任务/实时 job 从 `event_log` **重算**。改规则 = 改计算逻辑或改 `event_taxonomy.yaml` 里的规则配置，**不改历史数据、不改 event 表结构**。 | 规则/指标/业务说法换一套，只需重跑派生模型，event 层“谁在何时做了什么”永久可用。 |

**总结成三句话**：

- **不怕规则变**：规则只存在于“怎么从 event 算出来”的逻辑里，event 本身不存规则。
- **不怕指标变**：新指标 = 新派生表或新视图，还是基于同一份 event_log 重算。
- **不怕业务换说法**：MQL 今天叫“营销合格线索”、明天叫“高意向线索”，只改派生逻辑和展示口径，event 里的 `content_downloaded`、`form_submitted` 等不变。

### 数据统一性如何保证

多源（GA、HubSpot、LinkedIn、手动）且部分事件无 person，仍可保证**结构、语义与可关联**上的统一：

| 维度 | 做法 | 保证什么 |
|------|------|----------|
| **结构统一** | 所有来源只写**同一张 event_log**，同一套字段（event_type、actor_type、source、channel、properties、person_id 等）；Connector 按 [fact_layer_source_mapping](fact_layer_source_mapping.md) / [source_event_mapping.yaml](source_event_mapping.yaml) 映射，不各写各表。 | 下游只查一张表、同一套列，无“多套事实” |
| **语义统一** | **event_type** 用统一枚举（见 [event_taxonomy.yaml](event_taxonomy.yaml)）；**source** / **channel** 建议用枚举或 **touchpoint_source** 维表做规范化，避免同一渠道多种写法（如 "Website" vs "website"）。 | 计分、归因、漏斗用同一套 event_type/channel 规则 |
| **身份统一** | **person** 以 email 为业务唯一键；**company** 以 company_name/domain 为匹配键。同一人/公司多源写入时，先解析到同一 person_id/company_id 再写 event。匿名事件（GA）写 actor_type=anonymous、person_id=null，匿名 ID 放 properties。 | 有身份的事件指向同一批维表；匿名事件格式一致，便于后续身份解析 |
| **防重与可追溯** | **external_ref** 存源系统事件唯一键，并做 unique 约束；同一 GA/HubSpot 事件只落一条。**source** 标识来源，**properties** 保留原始 payload。 | 不重复、可对源排查 |
| **引用一致** | person_id / company_id / content_id / campaign_id 为外键；有则必指向维表已有行（或先写维表再写 event）。 | 有 ID 时维度一致、可 JOIN |

**身份解析（可选）**：同一 session 内先有 GA 匿名行为、后有 form_submitted 留资时，可用 properties 里的 client_id/session 与后续 person 关联，把该 session 下历史匿名事件在语义层“挂”到同一 person（如归因、得分时按 session 聚合再与 person 绑定）。事件表不必回写 person_id，语义层重算时处理即可。

---

## 3. Snowplow 风格三条铁律

### 铁律 A：Event Log 是唯一事实来源

- 所有行为都变成**事件**，不直接维护“统计表”。
- 统计、漏斗、得分、生命周期阶段等，都从 `event_log` **算出来**。
- 对应架构图：HubSpot Workflow、GA、LinkedIn Analytics、Business Card App 等汇入的都是“事件/行为”，最终落在一个统一的 Event Log 上。

### 铁律 B：事件里只放“坐标”，细节放维表

- `event_log` 只存：`person_id`、`company_id`、`content_id`、`campaign_id`、`source`、`channel` 等 ID 与少量关键字段。
- 人、公司、内容、活动的**详情**放在 `person`、`company`、`content`、`campaign` 等维表。
- 对应架构图：Event Log 与 Customer / Content+Resource Library / Campaign 分离，Event Log 即“超立方体坐标系”。

**并非每个 event 都有 person**：很多事件来源（如 **Google Analytics**）没有“人”这个维度——未登录、未留资，GA 里也没有 person/contact 标识。这类事件应照常入库：`actor_type` = **anonymous**，`person_id`、`company_id` 为 **null**；若源里有匿名标识（如 GA 的 client_id、session_id），可放进 `properties`，便于后续做身份解析（如同一 session 内 later 有 form_submitted 再反填 person_id）。HubSpot/表单类事件才有 person_id。

### 铁律 C：Lifecycle / Attribution 都是“算出来的切片”

- 不把 lifecycle 当“手改状态表”（除非是 CRM 官方状态同步）。
- 能从 event 重算 lifecycle，并能解释“为什么变成 MQL”（reason / 导致变化的事件引用）。
- 对应架构图：Dashboard 的 “Query over Event Log + Customer/Content/Campaign”、Attribution analysis、Nurture Decision Engine 都是基于 Event Log + 维表的**派生视图**。

---

## 4. 事件语言（Event Taxonomy）

事件按**来源**分为 4 类，v0 先覆盖 **Week 2 最小闭环**：`download → event → score → stage → dashboard`。

### A. Content 行为（核心）

| event_type | 说明 |
|------------|------|
| `content_viewed` | 看了内容（页/资源） |
| `content_downloaded` | 下载（白皮书/资料） |
| `content_shared` | 分享 |
| `asset_clicked` | 点击 CTA/按钮 |

### B. HubSpot 行为（营销自动化）

| event_type | 说明 |
|------------|------|
| `form_submitted` | 表单提交 |
| `email_opened` | 邮件打开 |
| `email_clicked` | 邮件点击 |
| `webinar_registered` | Webinar 注册 |
| `webinar_attended` | Webinar 参会 |

### C. Sales 反馈（可选；非严格销售逻辑）

本系统不建模完整 Sales 管道。若将来从 Sales 侧拿到反馈并回写，可落为少量事件用于培育优化，例如：

| event_type | 说明 |
|------------|------|
| `lead_status_changed` | 线索状态变更（如由 Sales 反馈回写） |
| `lifecycle_stage_changed` | 生命周期阶段变更（由培育逻辑或反馈推导） |
| `sales_feedback_received` | Sales 返回的结果（可选：已联系/有效/无效等），用于长期优化培育规则 |

v0 不依赖上述事件；**lead_score_daily / lifecycle_state 仅由营销行为事件（A/B/D 类）重算**。`opportunity_created`、`meeting_booked` 等若由外部系统提供可接入，但非本系统必建能力。

### D. 数据/内容操作行为（内部运营）

| event_type | 说明 |
|------------|------|
| `content_created` | 内容创建 |
| `content_updated` | 内容更新 |
| `tag_added` | 打标签 |
| `campaign_launched` | 活动上线 |

**v0 最小闭环**优先保证：`content_downloaded`、`form_submitted`、以及 HubSpot 同步的 `email_*` / `webinar_*`，用于算 **lead_score_daily** 和 **lifecycle_state**。

---

## 5. 核心表结构总览

### 5.1 事实表（1 张）

- **event_log**：谁在什么时候做了什么；`event_type`、`actor_type`、`person_id`、`company_id`、`content_id`、`campaign_id`、`source`、`channel`、`properties`（jsonb）、`external_ref`。

### 5.2 维表（5 张，v0）

- **person**：联系人/Lead（email、姓名、职位、hubspot_contact_id）。
- **company**：公司（B2B 必备）（公司名、domain、industry、country、hubspot_company_id）。
- **content**：内容资产库（title、content_type、tags、file_url、published_at、source_system）。
- **campaign**：活动（name、start_date、end_date、objective、channel_mix）。
- **touchpoint_source**（可选 v0）：source / channel 枚举与规范化，便于归因。

### 5.3 派生表（Derived Models，从 event 算出来）

- **lead_score_daily**：每人每日得分 + score_breakdown（哪些事件贡献分数）。
- **lifecycle_state**：每人当前阶段 + stage_updated_at + **reason**（导致变化的事件引用，可解释、可追溯）。
- **attribution_summary**（可选 v0）：每人转化事件的首触/末触渠道 + influencing_events。

---

## 6. 与架构图的数据流对应

| 架构图组件 | 对应表/逻辑 |
|------------|--------------|
| Connectors + Mapping + Scheduler → customer+Event / Behavior Data / Clean Customer Data | 写入 **event_log**，维表 **person** / **company** 由 Clean Customer Data / API 维护 |
| HubSpot Workflow → customer+Event Log / Lead Score | **event_log** 收事件；**lead_score_daily** 由事件重算 |
| Marketing Data Layer：Event Log + Customer + Content + Campaign | **event_log** + **person** + **company** + **content** + **campaign** |
| lead_lifecycle_state | **lifecycle_state** 表，由事件重算，reason 存事件引用 |
| Dashboard：Data analysis / Attribution / Nurture Decision Engine | 查询 **event_log** + 维表；Attribution 用 **attribution_summary**；Nurture 用 **lead_score_daily** + **lifecycle_state** |
| 推送给 Sales 的 leads + 反馈回流 | 培育效果好的 leads 全量推给 Sales；Sales 过段时间返回 feedback，用于**长期**更新培育机制；本系统**不包含**严格 Sales 逻辑（管道/商机阶段等） |

---

## 7. 文件索引

- **事件分类与 v0 闭环**：`event_taxonomy.yaml`
- **表结构定义（可读）**：`schema_v0.yaml`
- **表结构说明（Markdown 版）**：`schema_v0.md`（Customer/Content/Campaign 维表及事实表、派生表字段一览）
- **Postgres/Supabase 建表**：`schema_v0.sql`
- **通过 Supabase 连接所有数据**：`supabase_integration_guide.md`（各源写入 Supabase 的方式与 Connector 实现）
- **架构图**：`assets/` 或项目根目录下提供的 GTM 架构图（Event Log + 维表 + Dashboard 查询关系）

---

## 8. 可质疑与演进点

- **external_ref**：若多系统写入，需防重（同一 HubSpot event 只落一条）。
- **actor_type**：person/company/anonymous 是否再细分为 bot/system，可按需要扩展。
- **lifecycle_state.reason**：用 jsonb 存 `event_id` 或 `event_type + occurred_at`，便于“为什么变成 MQL”的可解释性。
- **attribution_summary**：v0 可只做 first_touch / last_touch，后续再加权重模型。
- **touchpoint_source**：若渠道不多，v0 可用枚举或配置表，不单独建表也可。

以上设计可直接用于在 Supabase/Postgres 建表，并与“Connectors + Event Log + 维表 + Dashboard”的架构图一一对应。
