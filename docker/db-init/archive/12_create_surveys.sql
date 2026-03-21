
-- 12_create_surveys.sql
-- Idempotent creation of the 'surveys' table used by the HAIC Benchmarking platform.

CREATE TABLE IF NOT EXISTS public.surveys (
    survey_id uuid PRIMARY KEY,
    user_id character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    pilot_tag character varying NOT NULL,
    app_version character varying,
    ai_model_version character varying,
    tam_sus_responses json,
    ethics_responses json,
    domain_specific json
);

-- Helpful indexes (optional)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname='public' AND indexname='idx_surveys_timestamp') THEN
        CREATE INDEX idx_surveys_timestamp ON public.surveys("timestamp");
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname='public' AND indexname='idx_surveys_pilot_tag') THEN
        CREATE INDEX idx_surveys_pilot_tag ON public.surveys(pilot_tag);
    END IF;
END$$;
