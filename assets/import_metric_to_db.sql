-- ======================================================
-- Consolidated Database Initialization Script: init_db.sql
-- ======================================================

-- Create the schema if it does not exist
CREATE SCHEMA IF NOT EXISTS public;

-- Optional: For a completely fresh start, you can uncomment the DROP TABLE commands
-- DROP TABLE IF EXISTS public.metrics CASCADE;
-- DROP TABLE IF EXISTS public.metric_groups CASCADE;

-- Create the table for metric_groups
CREATE TABLE IF NOT EXISTS public.metric_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255)  -- Optional column; remove if not needed
);

-- Create the table for metrics
CREATE TABLE IF NOT EXISTS public.metrics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description character varying,

    group_id INTEGER REFERENCES public.metric_groups(id)
);

-- ======================================================
-- Data Insertion Section
-- ======================================================

-- Insert metric groups
INSERT INTO public.metric_groups (name)
VALUES
    ('Performance'),
    ('Efficiency'),
    ('Adaptability and Learning'),
    ('Collaboration and Interaction'),
    ('Trust and Safety'),
    ('Robustness and Generalization')
ON CONFLICT (name) DO NOTHING;

-- Insert metrics for each group

-- Group 1: Performance
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Prediction Accuracy', 1),
    ('Precision', 1),
    ('Recall', 1),
    ('Overall System Accuracy', 1),
    ('Model Improvement Rate', 1)
ON CONFLICT DO NOTHING;

-- Group 2: Efficiency
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Response Time', 2),
    ('Teaching Efficiency', 2),
    ('Query Efficiency', 2),
    ('Resource Utilization', 2),
    ('Task Completion Time', 2),
    ('Correction Efficiency', 2),
    ('Error Reduction Rate', 2),
    ('Knowledge Retention', 2)
ON CONFLICT DO NOTHING;

-- Group 3: Adaptability and Learning
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Feedback Impact', 3),
    ('Adaptability Score', 3),
    ('Impact of Corrections', 3),
    ('Learning Efficiency', 3),
    ('Objective Fulfillment Rate', 3)
ON CONFLICT DO NOTHING;

-- Group 4: Collaboration and Interaction
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Human-AI Agreement Rate', 4),
    ('AI Assistance Rate', 4),
    ('Decision Effectiveness', 4),
    ('Time to Resolution', 4),
    ('Human Effort Saved', 4)
ON CONFLICT DO NOTHING;

-- Group 5: Trust and Safety
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Confidence', 5),
    ('Trust Score', 5),
    ('Safety Incidents', 5),
    ('System Reliability', 5)
ON CONFLICT DO NOTHING;

-- Group 6: Robustness and Generalization
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Adversarial Robustness', 6),
    ('Domain Generalization', 6)
ON CONFLICT DO NOTHING;