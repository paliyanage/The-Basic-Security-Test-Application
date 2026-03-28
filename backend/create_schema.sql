-- create_schema.sql

-- 1. Enable pgcrypto for gen_random_uuid() if not already
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Auditors table
CREATE TABLE IF NOT EXISTS auditors (
  id             SERIAL PRIMARY KEY,
  auditor_code   CHAR(8)    NOT NULL UNIQUE,      -- 8‐char uppercase code
  name           TEXT       NOT NULL,             -- auditor’s name
  email          TEXT       NOT NULL,             -- auditor’s email
  team           TEXT       NOT NULL,             -- team name
  team_manager   TEXT       NOT NULL,             -- team manager
  registered_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. Reports table
CREATE TABLE IF NOT EXISTS reports (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  auditor_id       INTEGER     NOT NULL REFERENCES auditors(id) ON DELETE CASCADE,
  client_company   TEXT        NOT NULL,
  it_manager_name  TEXT        NOT NULL,
  report           TEXT       NOT NULL,
  received_at      TIMESTAMPTZ NOT NULL,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Indexes
CREATE INDEX IF NOT EXISTS idx_reports_auditor     ON reports(auditor_id);
CREATE INDEX IF NOT EXISTS idx_reports_received    ON reports(received_at DESC);

-- (Optional) example JSONB path index, e.g. for cpu_percent in your report
-- CREATE INDEX IF NOT EXISTS idx_reports_cpu_percent
--   ON reports (((report->'check_cpu_usage'->>'cpu_percent')::numeric));

-- psql -h localhost -U postgres -d audit_db -f schema.sql