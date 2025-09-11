-- Active: 1719975402212@@127.0.0.1@5432@test_bench

-- 10_seed_metrics.sql
-- Idempotent seed for metric groups and metrics.
-- Safe to run repeatedly.

CREATE SCHEMA IF NOT EXISTS public;

-- Ensure tables exist
CREATE TABLE IF NOT EXISTS public.metric_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS public.metrics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR,
    group_id INTEGER REFERENCES public.metric_groups(id)
);

-- Ensure uniqueness to avoid duplicates (safe if already present)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE schemaname='public' AND indexname='uq_metric_groups_name'
    ) THEN
        CREATE UNIQUE INDEX uq_metric_groups_name ON public.metric_groups(name);
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE schemaname='public' AND indexname='uq_metrics_name'
    ) THEN
        CREATE UNIQUE INDEX uq_metrics_name ON public.metrics(name);
    END IF;
END$$;

-- Seed groups
INSERT INTO public.metric_groups (name) VALUES
    ('Performance'),
    ('Efficiency'),
    ('Adaptability and Learning'),
    ('Collaboration and Interaction'),
    ('Trust and Safety'),
    ('Robustness and Generalization')
ON CONFLICT (name) DO NOTHING;

-- Helper: get group id by name
WITH grp AS (
    SELECT id, name FROM public.metric_groups
)
INSERT INTO public.metrics (name, group_id)
VALUES
    -- Performance
    ('Prediction Accuracy',      (SELECT id FROM grp WHERE name='Performance')),
    ('Precision',                (SELECT id FROM grp WHERE name='Performance')),
    ('Recall',                   (SELECT id FROM grp WHERE name='Performance')),
    ('Overall System Accuracy',  (SELECT id FROM grp WHERE name='Performance')),
    ('Model Improvement Rate',   (SELECT id FROM grp WHERE name='Performance')),

    -- Efficiency
    ('Response Time',            (SELECT id FROM grp WHERE name='Efficiency')),
    ('Teaching Efficiency',      (SELECT id FROM grp WHERE name='Efficiency')),
    ('Query Efficiency',         (SELECT id FROM grp WHERE name='Efficiency')),
    ('Resource Utilization',     (SELECT id FROM grp WHERE name='Efficiency')),
    ('Task Completion Time',     (SELECT id FROM grp WHERE name='Efficiency')),
    ('Correction Efficiency',    (SELECT id FROM grp WHERE name='Efficiency')),
    ('Error Reduction Rate',     (SELECT id FROM grp WHERE name='Efficiency')),
    ('Knowledge Retention',      (SELECT id FROM grp WHERE name='Efficiency')),

    -- Adaptability and Learning
    ('Feedback Impact',          (SELECT id FROM grp WHERE name='Adaptability and Learning')),
    ('Adaptability Score',       (SELECT id FROM grp WHERE name='Adaptability and Learning')),
    ('Impact of Corrections',    (SELECT id FROM grp WHERE name='Adaptability and Learning')),
    ('Learning Efficiency',      (SELECT id FROM grp WHERE name='Adaptability and Learning')),
    ('Objective Fulfillment Rate',(SELECT id FROM grp WHERE name='Adaptability and Learning')),

    -- Collaboration and Interaction
    ('Human-AI Agreement Rate',  (SELECT id FROM grp WHERE name='Collaboration and Interaction')),
    ('AI Assistance Rate',       (SELECT id FROM grp WHERE name='Collaboration and Interaction')),
    ('Decision Effectiveness',   (SELECT id FROM grp WHERE name='Collaboration and Interaction')),
    ('Time to Resolution',       (SELECT id FROM grp WHERE name='Collaboration and Interaction')),
    ('Human Effort Saved',       (SELECT id FROM grp WHERE name='Collaboration and Interaction')),

    -- Trust and Safety
    ('Confidence',               (SELECT id FROM grp WHERE name='Trust and Safety')),
    ('Trust Score',              (SELECT id FROM grp WHERE name='Trust and Safety')),
    ('Safety Incidents',         (SELECT id FROM grp WHERE name='Trust and Safety')),
    ('System Reliability',       (SELECT id FROM grp WHERE name='Trust and Safety')),

    -- Robustness and Generalization
    ('Adversarial Robustness',   (SELECT id FROM grp WHERE name='Robustness and Generalization')),
    ('Domain Generalization',    (SELECT id FROM grp WHERE name='Robustness and Generalization'))
ON CONFLICT DO NOTHING;

DO $$
BEGIN
-- === Metric group descriptions ============================================
UPDATE metric_groups SET description =
'Measures how accurately the system achieves the intended task (correctness and quality of outputs).'
WHERE id = 1; -- Effectiveness

UPDATE metric_groups SET description =
'Measures speed and resource use: how quickly and efficiently the system delivers results.'
WHERE id = 2; -- Efficiency

UPDATE metric_groups SET description =
'Measures how well the system adapts over time, learns from feedback, and improves.'
WHERE id = 3; -- Adaptability and Learning

UPDATE metric_groups SET description =
'Measures the quality of human–AI teamwork: alignment, assistance, and joint outcomes.'
WHERE id = 4; -- Collaboration and Interaction

UPDATE metric_groups SET description =
'Measures safety, reliability, and user confidence while avoiding harmful behavior.'
WHERE id = 5; -- Trust and Safety

UPDATE metric_groups SET description =
'Measures performance under distribution shifts, edge cases, and adversarial conditions.'
WHERE id = 6; -- Robustness and Generalization


-- === Metric descriptions ===================================================
-- Effectiveness (id 1–5)
UPDATE metrics SET description = 'Share of correct predictions (0–1).'
WHERE id = 1;  -- Prediction Accuracy
UPDATE metrics SET description = 'Positive predictive value of model outputs (0–1).'
WHERE id = 2;  -- Precision
UPDATE metrics SET description = 'Sensitivity: fraction of positives correctly found (0–1).'
WHERE id = 3;  -- Recall
UPDATE metrics SET description = 'End-to-end accuracy at the system level (0–1).'
WHERE id = 4;  -- Overall System Accuracy
UPDATE metrics SET description = 'Rate of accuracy improvement across versions or time.'
WHERE id = 5;  -- Model Improvement Rate

-- Efficiency (id 6–13)
UPDATE metrics SET description = 'Time from input to model response (seconds).'
WHERE id = 6;  -- Response Time
UPDATE metrics SET description = 'How much guidance accelerates learning or task success (0–1).'
WHERE id = 7;  -- Teaching Efficiency
UPDATE metrics SET description = 'Efficiency of information requests or queries (0–1).'
WHERE id = 8;  -- Query Efficiency
UPDATE metrics SET description = 'Compute / memory / bandwidth efficiency (0–1, higher = better).'
WHERE id = 9;  -- Resource Utilization
UPDATE metrics SET description = 'Elapsed time to complete the task (seconds).'
WHERE id = 10; -- Task Completion Time
UPDATE metrics SET description = 'Speed/quality of fixing errors or refining outputs (0–1).'
WHERE id = 11; -- Correction Efficiency
UPDATE metrics SET description = 'Retention of relevant knowledge over time (0–1).'
WHERE id = 12; -- Error Reduction Rate  << NOTE
UPDATE metrics SET description = 'Share of previously made errors that no longer occur (0–1).'
WHERE id = 12; -- Error Reduction Rate (clarified)
UPDATE metrics SET description = 'User or system’s ability to recall learned information (0–1).'
WHERE id = 13; -- Knowledge Retention

-- Adaptability & Learning (id 14–18)
UPDATE metrics SET description = 'Observed impact of user feedback on model behavior (0–1).'
WHERE id = 14; -- Feedback Impact
UPDATE metrics SET description = 'Overall capacity to adjust to new goals, data, or instructions (0–1).'
WHERE id = 15; -- Adaptability Score
UPDATE metrics SET description = 'Effect that corrections have on subsequent outputs (0–1).'
WHERE id = 16; -- Impact of Corrections
UPDATE metrics SET description = 'Learning progress per unit time or interaction (0–1).'
WHERE id = 17; -- Learning Efficiency
UPDATE metrics SET description = 'Rate of meeting stated objectives or acceptance criteria (0–1).'
WHERE id = 18; -- Objective Fulfillment Rate

-- Collaboration & Interaction (id 19–23)
UPDATE metrics SET description = 'Agreement between human judgment and AI suggestion (0–1).'
WHERE id = 19; -- Human-AI Agreement Rate
UPDATE metrics SET description = 'Portion of steps where AI provides useful assistance (0–1).'
WHERE id = 20; -- AI Assistance Rate
UPDATE metrics SET description = 'Quality of decisions made with AI vs without AI (0–1).'
WHERE id = 21; -- Decision Effectiveness
UPDATE metrics SET description = 'Elapsed time from issue start to satisfactory resolution (seconds).'
WHERE id = 22; -- Time to Resolution
UPDATE metrics SET description = 'Reduction in human effort compared to baseline (0–1 or %).'
WHERE id = 23; -- Human Effort Saved

-- Trust & Safety (id 24–27)
UPDATE metrics SET description = 'User-reported or model-estimated confidence in outputs (0–1).'
WHERE id = 24; -- Confidence
UPDATE metrics SET description = 'Composite trust indicator derived from quality, transparency, and safety (0–1).'
WHERE id = 25; -- Trust Score
UPDATE metrics SET description = 'Count of safety issues or policy violations (count).'
WHERE id = 26; -- Safety Incidents
UPDATE metrics SET description = 'Service reliability / uptime / fault-free rate (0–1).'
WHERE id = 27; -- System Reliability

-- Robustness & Generalization (id 28–29)
UPDATE metrics SET description = 'Resistance to adversarial or worst-case inputs (0–1).'
WHERE id = 28; -- Adversarial Robustness
UPDATE metrics SET description = 'Ability to maintain performance on new domains or distributions (0–1).'
WHERE id = 29; -- Domain Generalization
END$$;