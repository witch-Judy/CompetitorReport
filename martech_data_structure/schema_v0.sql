-- Martech Schema v0 (Snowplow 范式)
-- Postgres / Supabase 可直接执行
-- 事实表 1 + 维表 5 + 派生表 3

-- ========== 维表（先建，被 event_log 引用） ==========

CREATE TABLE IF NOT EXISTS person (
  person_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       TEXT NOT NULL UNIQUE,
  full_name   TEXT,
  first_name  TEXT,
  last_name   TEXT,
  job_title   TEXT,
  mobile_number TEXT,
  interested_products_solutions TEXT,
  notes       TEXT,
  source     TEXT,
  hubspot_contact_id TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS company (
  company_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name TEXT,
  domain      TEXT,
  website     TEXT,
  industry    TEXT,
  country     TEXT,
  source      TEXT,
  hubspot_company_id TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS content (
  content_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title         TEXT,
  content_type  TEXT,   -- 业务类型: whitepaper | case_study | blog | video | webinar | ebook
  format        TEXT,   -- 文件/媒体格式: pdf | text | image | video | audio (或 mime_type)
  tags          TEXT[],
  owner_team    TEXT,
  file_url      TEXT,
  thumbnail_url TEXT,
  status        TEXT,   -- draft | published | archived
  language      TEXT,   -- zh | en
  slug          TEXT,
  published_at  TIMESTAMPTZ,
  source_system TEXT,   -- teams | onedrive | manual | cms
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS campaign (
  campaign_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT,
  start_date  DATE,
  end_date    DATE,
  objective   TEXT,
  channel_mix JSONB,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS touchpoint_source (
  code     TEXT PRIMARY KEY,
  label    TEXT,
  category TEXT  -- owned | paid | earned
);

-- ========== 事实表：Event Log（唯一事实来源） ==========

CREATE TABLE IF NOT EXISTS event_log (
  event_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  occurred_at TIMESTAMPTZ NOT NULL,
  event_type  TEXT NOT NULL,
  actor_type  TEXT NOT NULL,  -- person | company | anonymous
  person_id   UUID REFERENCES person(person_id),
  company_id  UUID REFERENCES company(company_id),
  content_id  UUID REFERENCES content(content_id),
  campaign_id UUID REFERENCES campaign(campaign_id),
  source      TEXT,
  channel     TEXT,
  properties  JSONB,
  external_ref TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_event_external_ref UNIQUE (external_ref)
);

CREATE INDEX IF NOT EXISTS idx_event_log_occurred_at ON event_log(occurred_at);
CREATE INDEX IF NOT EXISTS idx_event_log_person_occurred ON event_log(person_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_event_log_event_type_occurred ON event_log(event_type, occurred_at);

-- ========== 派生表（从 event_log 算出来，供 dashboard 用） ==========

CREATE TABLE IF NOT EXISTS lead_score_daily (
  person_id      UUID NOT NULL REFERENCES person(person_id),
  score_date     DATE NOT NULL,
  score          NUMERIC NOT NULL DEFAULT 0,
  score_breakdown JSONB,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (person_id, score_date)
);

CREATE TABLE IF NOT EXISTS lifecycle_state (
  person_id        UUID PRIMARY KEY REFERENCES person(person_id),
  current_stage    TEXT NOT NULL,   -- subscriber | lead | MQL | SQL | opportunity
  stage_updated_at TIMESTAMPTZ NOT NULL,
  reason           JSONB,           -- 导致变化的事件引用，可解释、可追溯
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS attribution_summary (
  person_id            UUID NOT NULL REFERENCES person(person_id),
  conversion_event_id  UUID NOT NULL REFERENCES event_log(event_id),
  first_touch_channel  TEXT,
  last_touch_channel   TEXT,
  influencing_events   JSONB,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (person_id, conversion_event_id)
);

-- ========== 注释（可选，便于协作） ==========

COMMENT ON TABLE event_log IS '铁律 A：唯一事实来源。所有行为都是事件，统计/得分/阶段均由此重算。';
COMMENT ON COLUMN event_log.properties IS '铁律 B：不稳定字段放这里。细节在维表。';
COMMENT ON TABLE lifecycle_state IS '铁律 C：从 event 重算的切片；reason 存导致变化的事件引用。';
