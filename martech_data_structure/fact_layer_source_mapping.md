# 事实层（event_log）与多数据源映射

本文档说明 **Google Analytics 4、LinkedIn Analytics/Insight Tag、HubSpot 邮件/活动** 等常见数据源中的“行为/事件”如何映射到我们的事实表 **event_log**，供 Connector 开发与语义层重算使用。  
事实层只关心“谁在何时做了什么”；`source`、`channel` 标识来源，`properties` 存各源原生字段，便于追溯与重算。

---

## 1. 映射通则

| event_log 字段 | 含义 | 各源写入方式 |
|----------------|------|----------------|
| **event_id** | 本系统唯一 ID | 入库时生成（如 uuid） |
| **occurred_at** | 行为发生时间 | 取源系统的 event 时间（如 GA 的 event_timestamp、HubSpot 的 occurredAt） |
| **event_type** | 统一事件类型 | 见下表：源事件 → 我们的 event_type |
| **actor_type** | person / company / anonymous | 有 contact/account 则 person 或 company；**无身份时必填 anonymous**（如 GA 无 person 维度） |
| **person_id** / **company_id** | 维表外键，可选 | 有则填；**无则 null**。GA 等多数事件无 person，写 actor_type=anonymous、person_id=null，匿名 ID 放 properties |
| **content_id** / **campaign_id** | 维表外键 | 能从源带出则写，否则 null |
| **source** | 数据来源系统 | `ga4` / `linkedin` / `hubspot` / `manual` 等 |
| **channel** | 触达渠道 | `website` / `email` / `linkedin` / `paid` / `organic` 等 |
| **properties** | 原生 payload（jsonb） | 存源系统原始参数，便于可解释、可重算 |
| **external_ref** | 源系统事件唯一键 | 防重；如 GA 的 event_id + timestamp，HubSpot 的 eventId |

---

## 2. Google Analytics 4 → event_log

**GA 没有“人”这个 tag**：GA 事件通常不带 contact/email，无法直接得到 person_id。写入 event_log 时：**actor_type** = `anonymous`，**person_id**、**company_id** = `null`；把 GA 的 `client_id`、`ga_session_id` 等放进 **properties**，便于后续用同一 session 内的 form_submit 等做身份解析与归因。

### 2.1 自动收集 + 增强衡量（Web）

| GA4 事件名 | 映射 event_type | channel | properties 建议携带 |
|------------|-----------------|---------|---------------------|
| **page_view** | content_viewed | website | page_location, page_referrer, page_title, engagement_time_msec |
| **first_visit** | session_start（或单独 first_visit） | website | client_id, ga_session_id, page_location, traffic_type |
| **session_start** | session_start | website | client_id, ga_session_id, ga_session_number, page_location |
| **user_engagement** | （可选：不落事件，或 engagement 聚合） | website | engagement_time_msec |
| **click** | asset_clicked | website | link_url, link_domain, link_id, link_classes, outbound |
| **form_start** | （可选：form_start） | website | form_id, form_name, form_destination |
| **form_submit** | form_submitted | website | form_id, form_name, form_destination, form_submit_text |
| **file_download** | content_downloaded | website | file_extension, file_name, link_url, link_id |
| **scroll** | （可选：content_viewed 或 scroll） | website | engagement_time_msec |
| **view_search_results** | search（或 content_viewed） | website | search_term |
| **video_start** | content_viewed | website | video_provider, video_title, video_url, video_percent |
| **video_progress** | content_viewed | website | 同上 + video_percent |
| **video_complete** | content_viewed | website | 同上 |

### 2.2 GA4 推荐事件（与营销/线索相关）

| GA4 事件名 | 映射 event_type | channel | properties 建议携带 |
|------------|-----------------|---------|---------------------|
| **generate_lead** | form_submitted 或 generate_lead | website | currency, value, lead_source |
| **view_item** | content_viewed | website | items[], currency, value |
| **select_content** | asset_clicked 或 content_viewed | website | content_type, content_id |
| **share** | content_shared | website | method, content_type, item_id |
| **sign_up** | form_submitted | website | method |
| **login** | （可选：login） | website | method |
| **qualify_lead** | lifecycle_stage_changed | website / crm | currency, value |
| **disqualify_lead** | lead_status_changed | website / crm | disqualified_lead_reason |
| **close_convert_lead** | opportunity_created 或 lifecycle_stage_changed | crm | currency, value |
| **close_unconvert_lead** | lead_status_changed | crm | unconvert_lead_reason |
| **working_lead** | meeting_booked 或 lead_status_changed | crm | lead_status |

**GA4 → event_log 小结**：  
- `source` = `ga4`；`channel` 一般为 `website`，若从 GA 传了 medium/source 可放入 `properties`（如 utm_source, utm_medium, utm_campaign）。  
- `external_ref` 建议用 GA 的 event 唯一标识（如 event_id + timestamp 或 BigQuery 导出时的 event_id）防重。

---

## 3. LinkedIn（Insight Tag + Conversions API）→ event_log

### 3.1 Insight Tag 站内行为

Insight Tag 可追踪“点击/表单提交/自定义”等转化事件，通常通过 GTM 或页面代码触发。

| LinkedIn 转化类型 / 行为 | 映射 event_type | channel | source |
|--------------------------|-----------------|---------|--------|
| 表单提交 | form_submitted | linkedin | linkedin |
| 按钮/链接点击（如下载、注册） | asset_clicked 或 content_downloaded / webinar_registered | linkedin | linkedin |
| 自定义转化（如白皮书下载） | content_downloaded | linkedin | linkedin |
| 页面浏览（若通过 Tag 上报） | content_viewed | linkedin | linkedin |

### 3.2 Conversions API 回传（线下/站外转化）

通过 Conversions API 回传的“转化”（如 Lead、Download、Custom），本质是“某人在某时完成了某行为”，可统一落一条 event_log。

| LinkedIn 转化类别（示例） | 映射 event_type | channel | 说明 |
|---------------------------|-----------------|---------|------|
| Lead | form_submitted / generate_lead | linkedin | 表单/留资 |
| Download | content_downloaded | linkedin | 下载资料 |
| 自定义 | 按业务选 content_downloaded / webinar_registered 等 | linkedin | 与 Conversion Rule 配置一致 |

**LinkedIn → event_log 小结**：  
- `source` = `linkedin`；`channel` = `linkedin`（或 `linkedin_paid` 若需区分广告触达）。  
- `properties` 可存：conversion_rule_id、campaign_id、creative_id、referrer、URL、device 等 Insight Tag / API 提供的字段。  
- `external_ref` 用 LinkedIn 的 conversion 唯一 id（若有）防重。

---

## 4. HubSpot（邮件 + 营销活动）→ event_log

### 4.1 邮件生命周期事件（Email Events API / Engagements）

| HubSpot 邮件事件 | 映射 event_type | channel | properties 建议携带 |
|------------------|-----------------|---------|---------------------|
| SENT | （可选：email_sent，或仅作审计不落行为） | email | email_id, campaign_id, recipient |
| DELIVERED | （可选：email_delivered） | email | 同上 |
| OPEN | email_opened | email | email_id, campaign_id, recipient, user_agent, ip 等 |
| CLICK | email_clicked | email | email_id, campaign_id, recipient, click_url, link_id |
| BOUNCE | （可选：email_bounced） | email | 同上 |
| 其他（如 SPAM、UNSUBSCRIBE） | 按需扩展 event_type | email | 同上 |

### 4.2 表单提交与营销活动

| HubSpot 行为 | 映射 event_type | channel | 说明 |
|--------------|-----------------|---------|------|
| Form 提交 | form_submitted | website / email | 来自站内表单或邮件内表单 |
| Webinar 注册 | webinar_registered | email / website | Marketing Events API 或 workflow |
| Webinar 参会 | webinar_attended | email / website | 同上 |
| 营销活动参与（活动维度） | 按具体类型：content_downloaded / asset_clicked 等 | email / website | campaign_id 可写入 event_log.campaign_id |

**HubSpot → event_log 小结**：  
- `source` = `hubspot`；`channel` = `email` / `website` 等按触达方式区分。  
- `person_id` 建议通过 hubspot_contact_id 解析到我们的 person 表。  
- `external_ref` 用 HubSpot 的 eventId 或 engagement id 防重。  
- `properties` 存原始 payload（如 emailCampaignId、portalId、recipient 等），便于“为什么算成 MQL”的可解释性。

---

## 5. 常见 Campaign / Email 行为汇总（统一口径）

以下为**语义层与报表常用**的“行为类型”，与各源的映射关系已在上文分源列出；事实层只需保证这些 event_type 被稳定写入，派生层即可按同一套规则重算。

| 我们的 event_type | 典型来源 | 用途（语义层） |
|-------------------|----------|----------------|
| content_viewed | GA4 page_view / view_item；LinkedIn 页面浏览 | 内容参与、漏斗 |
| content_downloaded | GA4 file_download；LinkedIn 下载转化；HubSpot 表单下载 | 得分、MQL、归因 |
| content_shared | GA4 share | 传播 |
| asset_clicked | GA4 click、select_content；LinkedIn 点击转化 | CTA、归因 |
| form_submitted | GA4 form_submit、generate_lead；LinkedIn 表单；HubSpot Form | 得分、线索、归因 |
| email_opened | HubSpot OPEN | 得分、参与度 |
| email_clicked | HubSpot CLICK | 得分、归因 |
| webinar_registered | HubSpot Marketing Events | 得分、生命周期 |
| webinar_attended | HubSpot Marketing Events | 得分、生命周期 |
| lead_status_changed / lifecycle_stage_changed | GA4 qualify_lead / working_lead；CRM 同步 | lifecycle_state 重算 |
| meeting_booked | CRM / Calendly 等 | 归因、SQL |
| opportunity_created | CRM；GA4 close_convert_lead | 归因、闭环 |

---

## 6. 实施要点（Connector 与事实层）

1. **每个源一条事件只落一次**：用 `external_ref`（GA event_id、HubSpot eventId、LinkedIn conversion id）做唯一约束或幂等写入。  
2. **person/company 解析**：能在源侧拿到 email/company 则解析到 `person_id`/`company_id`；否则先 `actor_type=anonymous`，后续用 identity 解析再补。  
3. **properties 尽量保留源字段**：便于排查、归因与语义层重算时引用“导致变化的事件”。  
4. **source / channel 枚举**：可与 `touchpoint_source` 维表或配置表一致，便于归因时做 first_touch / last_touch 的 channel 标准化。

按上述映射，GA4、LinkedIn、HubSpot 等多源异构行为可统一进入同一事实层，语义层（得分、生命周期、归因）只依赖 event_log + 维表重算即可。
