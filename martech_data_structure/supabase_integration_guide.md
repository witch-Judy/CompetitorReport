# 通过 Supabase 连接所有数据

本文档说明如何**以 Supabase 为唯一落点**，把 GA、HubSpot、LinkedIn、Teams、表单、手动上传等数据“连”到一起：所有表在 Supabase，各源通过 **Connector** 写入 Supabase。

---

## 1. 总体思路

- **Supabase** = 本系统唯一的数据库（Postgres）。  
  - 事实表 **event_log**、维表 **person / company / content / campaign**、派生表 **lead_score_daily / lifecycle_state / attribution_summary** 全部建在 Supabase 里（执行 [schema_v0.sql](schema_v0.sql) 即可）。
- **“连所有数据”** = 每个数据源都有一条**写入 Supabase 的链路**，不要求各源之间直连；所有数据最终都进 Supabase。

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ GA4         │     │ HubSpot     │     │ LinkedIn    │     │ 表单/上传   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Connector   │     │ Connector   │     │ Connector   │     │ 直写/导入   │
│ (拉取→映射) │     │ (API/Webhook)│     │ (API/拉取)  │     │ (Supabase   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     │  Client)    │
       │                   │                   │             └──────┬──────┘
       └───────────────────┴───────────────────┴───────────────────┘
                                        │
                                        ▼
                              ┌─────────────────────┐
                              │   Supabase          │
                              │   event_log         │
                              │   person / company  │
                              │   content / campaign│
                              │   (派生表由 job 重算)│
                              └─────────────────────┘
```

---

## 2. 各源如何连到 Supabase

| 数据源 | 怎么连 | 写哪些表 | 实现方式建议 |
|--------|--------|----------|--------------|
| **Google Analytics** | 拉取事件 → 映射 → 写入 | **event_log**（actor_type=anonymous，person_id=null）；可选先不写维表 | 定时 job 从 GA4 Reporting API 或 **BigQuery 导出** 拉取，用 [source_event_mapping.yaml](source_event_mapping.yaml) 映射后 insert；job 可跑在 Supabase Edge Functions (cron)、GitHub Actions、或单独 Worker |
| **HubSpot** | API / Webhook → 映射 → 写入 | **event_log**；**person** / **company**（先 upsert 再写 event 的 person_id/company_id） | Webhook 推送到 Supabase Edge Function 或自有接口，再写 Supabase；或定时从 HubSpot Engagements/Events API 拉取后写入 |
| **LinkedIn** | API / Insight Tag 回传 → 映射 → 写入 | **event_log**（source=linkedin）；有 contact 时写 **person** | Conversions API 回传或拉取报表，经小服务/Edge Function 写 Supabase |
| **Teams（文件）** | 已实现 Supabase 接 Teams | **content**（file_url 存 Teams 分享链接）；文件本体在 Teams | 上传走 Teams/Graph API，拿链接写 content 表；见 [content_library_design.md](content_library_design.md) |
| **网站表单** | 前端或后端直连 Supabase | **person** / **company**（upsert）+ **event_log**（form_submitted） | 前端用 Supabase Client（anon key + RLS）或后端 API 调 Supabase；先写/更新 person/company，再 insert event_log |
| **手动上传 / CSV** | 解析后批量写入 | **person** / **company**（及可选 **event_log**） | 上传到自建 Admin 或 Supabase Storage，用 Edge Function 或脚本解析 CSV、upsert 到 Supabase 表；见 [customer_dimension_guide.md](customer_dimension_guide.md) |

---

## 3. 各来源数据以什么格式连进来

Connector 从各源拿到的**输入格式**不同，需先解析再按 [source_event_mapping.yaml](source_event_mapping.yaml) 映射到 event_log/维表。下表给出各源的**数据格式**与**关键字段**，便于实现时对齐。

| 来源 | 输入格式 | 获取方式 | 关键字段（用于映射到 event_log / 维表） |
|------|----------|----------|----------------------------------------|
| **Google Analytics** | **BigQuery**：表 `events_*`，行=事件，列含 `event_name`, `event_timestamp`, `event_params`, `user_pseudo_id`(client_id), `geo`, `device` 等 | GA4 关联 BigQuery 后每日/流式导出 | event_name→event_type；event_timestamp→occurred_at；user_pseudo_id→properties.client_id；event_params / page_location 等→properties；无 person，actor_type=anonymous |
| **Google Analytics** | **Reporting API**：JSON，`rows` 为维度/指标组合 | 定时请求 GA4 Data API (REST) | 按请求的 dimensions/metrics 解析；event_name、date、session 等→event_type、occurred_at、properties；无 person |
| **HubSpot** | **Webhook**：JSON body，含 `subscriptionType`, `eventId`, `occurredAt`, `propertyName`, `propertyValue`, `objectId`（contact/company）等 | HubSpot 配置 Webhook 推送到你的 URL | occurredAt→occurred_at；eventId→external_ref；objectId/email 等→解析 person_id/company_id；propertyName 区分 event_type（如 form_submission） |
| **HubSpot** | **Events API / Engagements API**：JSON，`results[]` 每项含 `id`, `eventType`, `objectId`, `timestamp`, `properties` 等 | 定时 GET 带 filter 的 API | eventType→event_type；timestamp→occurred_at；objectId→external_ref；properties.email 等→person；见 [fact_layer_source_mapping](fact_layer_source_mapping.md) |
| **LinkedIn** | **Conversions API**：你方服务向 LinkedIn 发送 POST（JSON），用于回传转化；**拉取报表**则为 CSV/JSON（Campaign Manager 报表导出） | 回传：你的后端收到转化后发 LinkedIn；拉取：定时从 Campaign Manager / API 拉报表 | 回传时你已有 event，直接再写 Supabase；拉取时报表行为/转化→event_type、occurred_at、source=linkedin |
| **LinkedIn Insight Tag** | 站内触发时由你页面/GTM 发请求到你后端或 Supabase Edge Function；**body 自定**，建议 JSON：`{ event_type, occurred_at, source: "linkedin", properties: { ... } }` | 前端或 GTM 在转化时 POST 到你的接口 | 按约定 JSON 解析；你方接口再写 event_log，external_ref 自生成或从 body 取 |
| **Teams（文件）** | **Microsoft Graph API**：上传后返回 JSON，含 `webUrl`, `id` 等；或人工复制 **分享链接**（字符串） | 上传：POST /me/drive/items/... 等；人工：贴链接到 Admin | webUrl 或分享链接→content.file_url；元数据（title、format）→content 其他列 |
| **网站表单** | **JSON**（前端提交）：如 `{ email, company_name, industry, country, name, ... }` 或与 [customer_dimension_guide](customer_dimension_guide.md) 字段一致 | 前端 POST 到 Supabase（PostgREST）或自有 API 再写 Supabase | 表单字段→person / company；提交动作→event_log event_type=form_submitted，person_id 为刚 upsert 的 person_id |
| **手动上传 / CSV** | **CSV**：首行为列名，列与 [customer_dimension_guide](customer_dimension_guide.md) 一致（Name, Company, Industry, Position, Country, Email, Mobile, Website, Notes, source 等） | 上传文件到 Admin 或 Storage，由 Edge Function/脚本解析 | 每行→upsert person + company；若有“行为”列可再写 event_log；source 列→person/company.source |

**统一写入格式（Supabase 侧）**：无论源格式如何，写入 Supabase 时都按 **schema_v0** 的列类型来——event_log 为单行 insert（uuid、timestamptz、text、jsonb 等），person/company 为 upsert（以 email / company_name+domain 为键）。建议 Connector 内部分层：**解析层**（源格式 → 内部 DTO）→ **映射层**（DTO → event_log/维表字段）→ **写入层**（Supabase Client insert/upsert）。

---

## 4. 实现方式选型

| 方式 | 适用场景 | 说明 |
|------|----------|------|
| **Supabase Client 直连** | 前端表单、自建 Admin、轻量脚本 | 用 `@supabase/supabase-js`，service_role 仅在后端/脚本用；前端用 anon key + RLS 限制可写表与行 |
| **Supabase Edge Functions** | 定时拉取、Webhook 接收 | 用 Deno 写 Function，通过 Supabase client 写库；在 Dashboard 配 cron 触发（如每小时拉 GA） |
| **外部 Worker / 定时任务** | GA/HubSpot/LinkedIn 定时同步 | Node 或 Python 跑在 GitHub Actions、Inngest、或自有机子，拉源数据后调 Supabase REST API 或 Postgres 连接写入 |
| **Supabase Database Webhooks** | 需在数据变更时触发下游 | 表 insert/update 时触发 HTTP 或 Edge Function，可用于“新 event 写入后触发得分重算”等 |

Connector 与 Supabase 的认证：**Service Role Key** 仅放在后端/Edge Function/Worker 中，不要暴露到前端；前端只用于表单/已授权操作，且配合 RLS。

---

## 5. 建议实施顺序

1. **在 Supabase 建表**：执行 [schema_v0.sql](schema_v0.sql)，确认 event_log、person、company、content、campaign 等存在。
2. **先接 1～2 个源**：例如 **网站表单 → person + event_log** 和 **HubSpot → event_log + person/company**，保证端到端能写 Supabase。
3. **再接 GA**：用 BigQuery 导出或 GA4 Reporting API + 定时 job，按 [fact_layer_source_mapping.md](fact_layer_source_mapping.md) 映射，写 event_log（anonymous）。
4. **派生表**：用定时 job 或 Edge Function 从 event_log 重算 lead_score_daily、lifecycle_state；可先写 SQL 或 dbt，再由 cron 触发。
5. **其余源**：LinkedIn、手动上传等按需加 Connector，都写入同一套 Supabase 表。

---

## 6. 小结

- **通过 Supabase 连所有数据** = 以 Supabase 为唯一数据库，每个源通过各自的 Connector 或直写逻辑把数据写入 Supabase。
- 映射规则用 [fact_layer_source_mapping.md](fact_layer_source_mapping.md) 与 [source_event_mapping.yaml](source_event_mapping.yaml)，保证 event 语义统一。
- 实现上可用：Supabase Client、Edge Functions + cron、外部 Worker、Webhook；Connector 用 service_role 写库，前端用 anon + RLS。

按上述方式即可把“所有数据”都连到 Supabase，并在同一套事实层与维表上做分析、培育与归因。
