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
