-- 1) new table
CREATE TABLE survey_question_sets (
  schema_id UUID PRIMARY KEY,
  name TEXT NULL,
  pilot_tag TEXT NULL,
  version INT NOT NULL DEFAULT 1,
  questions JSON NOT NULL,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by TEXT NULL
);
CREATE INDEX IF NOT EXISTS idx_sqs_pilot ON survey_question_sets(pilot_tag);

-- 2) surveys add column
ALTER TABLE surveys ADD COLUMN schema_id UUID NULL;
