# Martech Schema v0 表结构说明（Markdown 版）

与 `schema_v0.yaml`（可读配置）、`schema_v0.sql`（Postgres 建表）一致，本文件为**文档版**，便于在 Markdown 中查阅全量表结构。  
架构图对应：**Customer** = person + company，**Content** = content，**Campaign** = campaign。

---

## 1. 事实表（1 张）

### event_log

唯一事实来源；记录「谁在什么时候做了什么」（超立方体坐标系）。  
Snowplow 对应：`event_type` = event_name，`properties` = unstructured/context。

**并非每个 event 都有 person**：如 Google Analytics 的 page_view、click 等通常没有“人”标识，应存为 `actor_type`=anonymous、`person_id`/`company_id`=null；匿名 ID（如 GA client_id）可放 `properties`，供后续身份解析。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| event_id | uuid | ✓ | PK |
| occurred_at | timestamptz | ✓ | 行为发生时间 |
| event_type | text | ✓ | content_downloaded / form_submitted / ... |
| actor_type | text | ✓ | person / company / **anonymous**（无 person 时） |
| person_id | uuid | | 可选；无身份时为空（如 GA 多数事件）→ person.person_id |
| company_id | uuid | | 可选；无身份时为空 → company.company_id |
| content_id | uuid | | → content.content_id |
| campaign_id | uuid | | → campaign.campaign_id |
| source | text | | hubspot / web / manual / teams |
| channel | text | | email / linkedin / website / ... |
| properties | jsonb | | utm、page_url、device 等不稳定字段 |
| external_ref | text | | 源系统事件 id，防重复 |
| created_at | timestamptz | ✓ | 入库时间 |

**索引建议**：occurred_at；(person_id, occurred_at)；(event_type, occurred_at)；external_ref（unique）。

---

## 2. 维表（5 张）

### 2.1 person（Customer - 联系人/Lead）

支持**表单收集**与**手动上传历史客户库**；用 `source` 区分来源，便于维护与去重。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| person_id | uuid | ✓ | PK |
| email | text | ✓ | 唯一（表单 Email*） |
| full_name | text | | 表单 Name*；可与 first_name/last_name 二选一或同时维护 |
| first_name | text | | |
| last_name | text | | |
| job_title | text | | 表单 Position |
| mobile_number | text | | 表单 Mobile Number |
| interested_products_solutions | text | | 表单 Interested products/solutions（如 Hardware / Software） |
| notes | text | | 表单 Notes |
| source | text | | form / manual_upload / hubspot / import_YYYYMM 等 |
| hubspot_contact_id | text | | |
| created_at | timestamptz | ✓ | |
| updated_at | timestamptz | | 最近一次更新（含手动上传覆盖时更新） |

### 2.2 company（Customer - 公司，B2B 必备）

支持**表单收集**与**手动上传历史客户库**；用 `source` 区分来源。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| company_id | uuid | ✓ | PK |
| company_name | text | | 表单 Company* |
| domain | text | | 可从 Website 解析或单独填写 |
| website | text | | 表单 Website（完整 URL） |
| industry | text | | 表单 Industry* |
| country | text | | 表单 Country* |
| source | text | | form / manual_upload / hubspot / import_YYYYMM 等 |
| hubspot_company_id | text | | |
| created_at | timestamptz | ✓ | |
| updated_at | timestamptz | | 最近一次更新（含手动上传覆盖时更新） |

### 2.3 content（Content Library 维表）

内容资产库；event_log 只存 `content_id`，详情在此表。详见 [content_library_design.md](content_library_design.md)。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content_id | uuid | ✓ | PK |
| title | text | | |
| content_type | text | | 业务类型：whitepaper / case_study / blog / video / webinar / ebook / ... |
| format | text | | 文件/媒体格式：pdf / text / image / video / audio（或 mime_type） |
| tags | text[] | | 或 jsonb |
| owner_team | text | | |
| file_url | text | | 实际文件在对象存储/OneDrive/Teams；此处只存链接，不存文件本体 |
| thumbnail_url | text | | |
| status | text | | draft / published / archived |
| language | text | | zh / en 等 |
| slug | text | | URL 友好标识 |
| published_at | timestamptz | | |
| source_system | text | | teams / onedrive / manual / cms |
| created_at | timestamptz | ✓ | |
| updated_at | timestamptz | | 最近一次元数据或状态变更 |

### 2.4 campaign（活动）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| campaign_id | uuid | ✓ | PK |
| name | text | | |
| start_date | date | | |
| end_date | date | | |
| objective | text | | |
| channel_mix | jsonb | | |
| created_at | timestamptz | ✓ | |

### 2.5 touchpoint_source（可选 v0）

source / channel 枚举与规范化，便于归因。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | text | ✓ | PK，如 website / email / linkedin |
| label | text | | |
| category | text | | owned / paid / earned |

---

## 3. 派生表（Derived Models，从 event_log 重算）

### 3.1 lead_score_daily

每人每日得分 + 贡献 breakdown。  
唯一约束：(person_id, score_date)。

| 字段 | 类型 | 说明 |
|------|------|------|
| person_id | uuid | → person.person_id |
| score_date | date | |
| score | numeric | |
| score_breakdown | jsonb | 哪几个事件贡献了分数 |
| created_at | timestamptz | |

### 3.2 lifecycle_state

每人当前阶段；reason 存导致变化的事件引用，可解释、可追溯。  
每人一条当前状态；历史可从 event 重算。

| 字段 | 类型 | 说明 |
|------|------|------|
| person_id | uuid | PK，→ person.person_id |
| current_stage | text | subscriber / lead / MQL / SQL / opportunity / ... |
| stage_updated_at | timestamptz | |
| reason | jsonb | 导致变化的事件引用（event_id 或 event_type+occurred_at） |
| created_at | timestamptz | |

### 3.3 attribution_summary（可选 v0）

| 字段 | 类型 | 说明 |
|------|------|------|
| person_id | uuid | → person.person_id |
| conversion_event_id | uuid | → event_log.event_id（如 form_submitted / meeting_booked） |
| first_touch_channel | text | |
| last_touch_channel | text | |
| influencing_events | jsonb | 参与归因的事件列表 |
| created_at | timestamptz | |

主键：(person_id, conversion_event_id)。

---

## 4. 与架构图 / 文件的对应

| 架构图 | 本 schema |
|--------|-----------|
| Customer (Person, Company) | person + company |
| Content + Resource Library | content |
| Campaign | campaign |
| Event Log | event_log |
| lead_lifecycle_state / Lead Score | lifecycle_state + lead_score_daily |

- **可执行建表**：`schema_v0.sql`  
- **可读配置**：`schema_v0.yaml`
