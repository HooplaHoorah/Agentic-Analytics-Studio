-- AAS Postgres schema (Option 3 Live Data)
-- Safe to re-run: uses IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS aas_opportunities (
  opportunity_id TEXT PRIMARY KEY,
  owner TEXT NOT NULL,
  region TEXT NOT NULL,
  segment TEXT NOT NULL,
  stage TEXT NOT NULL,
  amount NUMERIC(14,2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  close_date DATE NOT NULL,
  last_touch_date DATE NOT NULL,
  stage_age_days INT NOT NULL
);

CREATE TABLE IF NOT EXISTS aas_pipeline_runs (
  run_id TEXT PRIMARY KEY,
  run_ts TIMESTAMPTZ NOT NULL,
  play TEXT NOT NULL,
  notes TEXT,
  created_by TEXT DEFAULT 'aas'
);

CREATE TABLE IF NOT EXISTS aas_findings (
  finding_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES aas_pipeline_runs(run_id) ON DELETE CASCADE,
  opportunity_id TEXT REFERENCES aas_opportunities(opportunity_id) ON DELETE SET NULL,
  risk_score NUMERIC(6,3) NOT NULL,
  risk_driver TEXT NOT NULL,
  details JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS aas_actions (
  action_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES aas_pipeline_runs(run_id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending','approved','executed','failed','dismissed')),
  action_type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  priority INT NOT NULL DEFAULT 3,
  owner TEXT,
  region TEXT,
  stage TEXT,
  opportunity_id TEXT,
  payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_aas_actions_status ON aas_actions(status);
CREATE INDEX IF NOT EXISTS idx_aas_actions_region ON aas_actions(region);
CREATE INDEX IF NOT EXISTS idx_aas_actions_owner ON aas_actions(owner);
CREATE INDEX IF NOT EXISTS idx_aas_actions_stage ON aas_actions(stage);

CREATE TABLE IF NOT EXISTS aas_executions (
  execution_id TEXT PRIMARY KEY,
  action_id TEXT NOT NULL REFERENCES aas_actions(action_id) ON DELETE CASCADE,
  executed_at TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('ok','error','skipped')),
  result JSONB NOT NULL
);
