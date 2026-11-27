# Marketing Automation – Full Requirements (2026 MarTech & Event Strategy)

This document consolidates MarTech / Marketing Automation requirements for **2026 global events and campaigns**, for vendor selection, implementation, and internal alignment. Requirements are aligned with the existing **GTM data architecture** ([design.md](design.md), [assets/GTM_architecture.png](assets/GTM_architecture.png)) and **Supabase + HubSpot + Teams** stack, so implementation stays consistent with the event model, dimension tables, and Connectors.

**Source**: 2026 MarTech & Event Strategy Requirements (internal brief); **Architecture reference**: This folder’s GTM diagram and Snowplow-style data structures.

### Current stack (in place or committed)

| Layer / role | Stack | Notes |
|--------------|--------|--------|
| **Database** | **Supabase** (Postgres, to be built) | Single sink for event_log + dimensions (person, company, content, campaign, touchpoint_source) and derived tables (lead_score_daily, lifecycle_state, attribution_summary). See [schema_v0.sql](schema_v0.sql), [schema_v0.md](schema_v0.md). |
| **CRM & Marketing Automation** | **HubSpot** (Enterprise preferred) | Primary CRM and MA; events/leads sync to Supabase or write via Connectors. Workflows, forms, email, Breeze AI (or equivalent) for scoring. |
| **Content file storage** | **Microsoft Teams** (OneDrive / SharePoint) | File bodies in Teams; only metadata and **file_url** (Teams share link) in Supabase **content** table. Supabase ↔ Teams integration already in use. See [content_library_design.md](content_library_design.md). |
| **Event / behavior sources** | **GA4** (BigQuery or Reporting API), **HubSpot** (API / Webhook), **LinkedIn** (API / Insight Tag), **event lead-capture** (e.g. Zuant, Cvent), **web forms**, **CSV / manual upload** | All mapped into **event_log** via Connectors; see [fact_layer_source_mapping.md](fact_layer_source_mapping.md), [supabase_integration_guide.md](supabase_integration_guide.md). |

New tools (e.g. chatbot, CMS for content editing) must integrate with this stack; MA capabilities in §2.5 should align with HubSpot and the above data model.

---

## 1. Core Objective

| Requirement | Description | Mapping to current architecture |
|-------------|-------------|--------------------------------|
| **Unified CRM + Marketing Automation** | Single platform for 2026 global events and campaigns; **HubSpot Enterprise preferred**. | Events and leads use **event_log** + **person** / **company** as single source of truth and dimensions; HubSpot as primary MA source, writing to Supabase or syncing with HubSpot objects. |
| **Intercept leads from competitors** | Enable interception of leads from legacy competitors (ABB, Honeywell, Emerson, etc.) and support **displacement** content and conversion paths. | **Competitor Intelligence** in person/company or Custom Object for “current installed base”; triggers automated displacement content and nurturing. |
| **Closed-loop ROI reporting** | Measurable ROI from acquisition to closed-won for key events (Hannover Messe, GasTech, ADIPEC). | **Multi-touch attribution** (first touch → closed-won) and **event_log + derived tables** (attribution_summary, lifecycle_state); see §4. |

---

## 2. Technical & Data Requirements

### 2.1 Competitor Intelligence Mapping

| Requirement | Description | Implementation notes |
|-------------|-------------|----------------------|
| **Current Installed Base** | Record which **competitor system** the lead/customer currently uses (e.g. ABB, Honeywell, Emerson) and trigger **automated displacement content**. | Add fields to **company** or **person** (e.g. `current_competitor`, `installed_base`) or HubSpot Custom Object; workflows/nurturing rules push displacement content (content table + event_log content_id). |
| **Displacement content automation** | Match and send displacement whitepapers, case studies, and comparison assets by competitor tag. | Tag content in Content Library or link campaign to “competitor displacement”; MA workflows use person/company competitor fields + event behavior to trigger content and campaign. |

### 2.2 Regional Architecture

| Requirement | Description | Implementation notes |
|-------------|-------------|----------------------|
| **Independent BUs** | Support **SEA, Europe, NA, Middle East** with separate lead routing, language partitioning, and regional data privacy compliance. | **person** / **company** need **region** / **business_unit** (and country, language); routing and permissions by region; event_log **properties** or dimensions for language/region for reporting and compliance. |
| **Localized lead routing** | Route leads to the correct regional sales/marketing. | Workflow and assignment rules based on person/company region/country; Hot leads pushed to Sales with region (aligned with §3.1 SLA). |
| **Regional data privacy** | Meet data residency and privacy requirements per region. | Storage and access policies by region; Supabase and HubSpot configured for regional rules; event and person data partitionable and auditable. |

### 2.3 High-Speed Lead Integration

| Requirement | Description | Implementation notes |
|-------------|-------------|----------------------|
| **Event lead-capture integration** | Seamless API integration with **Zuant, Cvent** (or similar) for **Speed-to-Lead < 4 hours** (booth scan to sales outreach). | Event tool → API/Webhook → **Connector** → write **person** / **company** + **event_log** (e.g. event_type=form_submitted or event_lead_captured); format see [supabase_integration_guide.md §3](supabase_integration_guide.md#3-各来源数据以什么格式连进来). |
| **Single sink** | Event leads and web forms, HubSpot, GA, etc. land in the same **event_log + dimensions** for attribution and scoring. | All sources mapped into Supabase (or HubSpot as primary with sync to Supabase); external_ref for deduplication; see [fact_layer_source_mapping.md](fact_layer_source_mapping.md). |

### 2.4 Lead Scoring & AI

| Requirement | Description | Implementation notes |
|-------------|-------------|----------------------|
| **Predictive lead scoring** | **HubSpot Breeze AI** (or equivalent) to rank and prioritize leads by event engagement and intent signals. | Intent and engagement from **event_log** (event check-in, downloads, forms, email clicks); scores in **lead_score_daily** or HubSpot native; derivable and explainable (see [design.md](design.md)). |
| **Event-driven scoring** | Scoring rules based on behavioral events; configurable and iterable. | event_taxonomy and scoring rules (e.g. [event_taxonomy.yaml](event_taxonomy.yaml) scoring_rules_v0) recomputed from event_log by MA or batch jobs; Breeze AI can use event features. |

### 2.5 Marketing Automation – Concrete Capabilities

Under “unified CRM + MA”, vendors/implementation must support these **concrete capabilities**, aligned with event_log, dimensions, and workflows:

| Capability | Requirements | Mapping to data architecture |
|------------|--------------|------------------------------|
| **Email Marketing** | Sending, templates, A/B tests, open/click tracking, unsubscribe and compliance (e.g. regional consent); segment by region, competitor, score. | Email actions (open, click, unsubscribe) as events in **event_log** (e.g. email_opened, email_clicked), source=hubspot; **person** for segmentation and dedup; see [fact_layer_source_mapping.md](fact_layer_source_mapping.md). |
| **Lead Nurturing** | Behavior- and attribute-based automation (e.g. whitepaper download → email series; event sign-up → welcome + displacement content); branching and cadence by lifecycle and score. | Triggers from **event_log** (form_submitted, content_downloaded, email_clicked); **lifecycle_state**, **lead_score_daily** for branching; content from **content**; workflows as execution layer (HubSpot Workflows or equivalent). |
| **Campaign Management** | Cross-channel campaign create, schedule, audience and budget; unified naming and attribution for events, online, ABM; campaign-level reporting. | **campaign** table for metadata (name, dates, objective, channel_mix); **event_log.campaign_id** links behavior to campaign; attribution and reporting by campaign, see **attribution_summary** and §4. |
| **Chatbot / Conversational marketing** | **Chatbot** on site or product: book meetings, qualify leads; trigger email sequence after conversation ends; personalize with CRM data; configurable flows without code; UI matches site/product theme. | Chat actions (session start/end, meeting booked) in **event_log** (e.g. chat_started, chat_ended, meeting_booked); triggered sequences align with Lead Nurturing and Email Marketing; **person** for personalization and lead identification. |

These four are **concrete requirements**; confirm platform coverage at selection and Sprint 0, and align with this folder’s event model, dimensions, and derived tables.

---

## 3. Campaign & Sales Alignment

### 3.1 Automated SLAs & Escalation

| Requirement | Description | Implementation notes |
|-------------|-------------|----------------------|
| **Follow-up timing** | Workflows track and enforce **sales follow-up SLAs**; **escalation** if Hot event leads are not contacted within agreed time. | “Assigned time” from **lifecycle_state** or HubSpot state + **event_log** (e.g. event_lead_captured, form_submitted); timeout triggers alert/escalation; Hot aligned with lead_score_daily or Breeze AI. |
| **Traceability** | Escalations and SLA breaches traceable to specific lead and events. | **lifecycle_state.reason** stores event references for state changes; SLA logic from event timestamps and assignment delta. |

### 3.2 Omnichannel intercepts & ABM

| Requirement | Description | Implementation notes |
|-------------|-------------|----------------------|
| **Geo-fencing & ABM** | Run **geo-fenced digital ads** and **ABM** targeting accounts attending specific 2026 global events. | **campaign** and event_log campaign_id/channel support “event + region + ABM list”; person/company with region and account tags for targeting and attribution; multi-source events (GA, LinkedIn, HubSpot) in event_log for attribution. |
| **Event context** | Tie to venues/dates (Hannover Messe, GasTech, ADIPEC). | campaign or content linked to event/venue; event properties or dimensions for event_venue, event_date for reporting and attribution. |

### 3.3 Sales Enablement

| Requirement | Description | Implementation notes |
|-------------|-------------|----------------------|
| **Mobile-first CRM** | **Mobile-first** CRM for field teams to manage leads and view **competitor Battlecards** on the show floor. | CRM (HubSpot or Supabase-synced UI) with mobile; Battlecards keyed by **current_competitor** / installed_base; content from Content Library or Teams. |
| **Live leads & Battlecards** | After booth scan/sign-up, sales see lead summary and talking points immediately. | Event Connector writes person/company + event_log; CRM/mobile shows in near real time; competitor field drives Battlecard recommendation. |

---

## 4. Reporting & Analytics Requirements

Vendors must be able to build a **2026 Command Center Dashboard** with:

| Requirement | Description | Mapping to current architecture |
|-------------|-------------|--------------------------------|
| **Multi-touch attribution (W-shaped)** | Revenue attribution from **first touch** to **closed-won** with W-shaped weights. | **event_log** as source; **attribution_summary** (or equivalent) for first_touch_channel, last_touch_channel, influencing_events; Dashboard queries event_log + dimensions; attribution model (incl. W) in semantic layer; see [design.md](design.md), [schema_v0.md](schema_v0.md). |
| **Competitor displacement win-rate** | Analytics on **which competitor installed bases** we convert successfully (Competitor Displacement Win-Rate). | **company** / **person** current_competitor / installed_base + **lifecycle_state** or closed-won; report by competitor with conversion and revenue. |
| **Regional pipeline velocity** | **Regional Pipeline Velocity**: compare lead movement speed across regions/countries. | **event_log** occurred_at + **lifecycle_state** stage_updated_at by person/company region for “sign-up → MQL/SQL/closed” duration; Dashboard by region/BU. |
| **Command Center** | Single view: events, campaigns, lead quality, follow-up SLA, attribution, pipeline. | Data = **event_log** + **person** / **company** / **content** / **campaign** + **lead_score_daily** / **lifecycle_state** / **attribution_summary**; via Supabase or HubSpot reporting. |

---

## 5. Implementation & Sprint 0 Expectations

| Requirement | Description | Implementation notes |
|-------------|-------------|----------------------|
| **Sprint 0 Discovery** | Dedicated phase to align **2026 event calendar** with **CRM data model** (event types, attributes, reporting). | Use this folder’s **event_taxonomy.yaml**, **schema_v0**, and [fact_layer_source_mapping.md](fact_layer_source_mapping.md) as baseline; map 2026 events and campaigns to campaign table and event_type; define Zuant/Cvent input format and Connector spec. |
| **Data migration** | Strategy for **cleaning and importing** legacy lead data. | See [customer_dimension_guide.md](customer_dimension_guide.md): person/company source, dedup (email, company_name), batch import source (e.g. import_202601); historical behavior into event_log if recoverable, else dimension backfill only. |
| **Training** | **Train-the-Trainer** for regional marketing and sales leads. | Cover: unified data model (events + dimensions), HubSpot and Supabase usage, event lead ingestion, SLA and Battlecards, Command Center and attribution; reference this folder for technical detail. |

---

## 6. Mapping to existing data architecture

- **Facts & dimensions**: “Leads, behavior, competitor, region, event, campaign” map to **event_log** and **person** / **company** / **content** / **campaign** in [design.md](design.md); Custom Objects (e.g. competitor) extend dimensions or HubSpot and link to events.
- **Data landing**: All Connectors write to **Supabase** (or HubSpot with sync to Supabase); files in **Teams**; see [supabase_integration_guide.md](supabase_integration_guide.md), [content_library_design.md](content_library_design.md).
- **Score, lifecycle, attribution**: All **derived** from **event_log**; rules configurable and replaceable; see [design.md §2 Design guarantees](design.md#2-设计保证为什么不怕规则变、指标变、业务换说法).
- **Sales boundary**: System owns nurturing and pushing Hot leads; Sales follow-up, SLA, Battlecards are joint capabilities; closed-won via feedback or CRM sync for attribution and competitor win-rate; see [design.md §1 Sales boundary](design.md#与-sales-的边界scope).

---

## 7. Existing database & size (Database & Size)

The **existing data architecture** for these requirements is this folder’s schema ([schema_v0.sql](schema_v0.sql), [schema_v0.md](schema_v0.md)): fact table **event_log**, dimension tables **person / company / content / campaign / touchpoint_source**, derived **lead_score_daily / lifecycle_state / attribution_summary**, hosted on **Supabase** (Postgres).

**Recommend documenting database size** in the requirements for capacity, performance, and migration scope:

| Dimension | Description | Example / to be filled |
|-----------|-------------|------------------------|
| **DB type** | Current prod/staging | e.g. Supabase (Postgres 15) |
| **Table count** | Fact + dimensions + derived | 1 fact + 5 dimensions + 3 derived (see schema_v0) |
| **event_log row count** | Total events (current or annual) | e.g. 10^6/year, 10^7 cumulative |
| **person / company row count** | Contact and company master data | e.g. 10^5 person, 10^4 company |
| **content row count** | Content asset count | e.g. order 10^3 |
| **Storage** | Total DB size or by table | e.g. xx GB (fill from Supabase if available) |
| **Retention** | event_log retention, partitioning/archival | e.g. 2 years hot + archive |

Replace the examples with **actual numbers** when available; if not yet live, use “expected scale” and note it. Including database and size in the requirements helps Sprint 0 migration, Command Center, and Connector capacity planning.

---

## 8. Document index (this folder)

| Document | Purpose |
|----------|---------|
| [design.md](design.md) | Data architecture, two-layer model, three rules, event taxonomy |
| [schema_v0.md](schema_v0.md) / [schema_v0.sql](schema_v0.sql) | Table structures and DDL |
| [event_taxonomy.yaml](event_taxonomy.yaml) | Event types and scoring rules |
| [customer_dimension_guide.md](customer_dimension_guide.md) | Customer dimensions and import rules |
| [content_library_design.md](content_library_design.md) | Content Library and Teams |
| [fact_layer_source_mapping.md](fact_layer_source_mapping.md) | Multi-source events → event_log mapping |
| [supabase_integration_guide.md](supabase_integration_guide.md) | Connecting all sources via Supabase and input formats |
| [assets/GTM_architecture.png](assets/GTM_architecture.png) | GTM architecture diagram |

This document is the **Marketing Automation – full requirements** summary; use it with the above technical docs for selection, Sprint 0, and implementation. **§7 Database & size** should be filled with actual or expected numbers before sharing with vendors or implementation teams.
