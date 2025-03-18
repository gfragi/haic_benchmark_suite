-- ======================================================
-- Consolidated Database Initialization Script: init_db_consolidated.sql
-- ======================================================

-- Create the schema if it does not exist
CREATE SCHEMA IF NOT EXISTS public;

-- Optional: For a completely fresh start, uncomment these DROP TABLE commands
-- DROP TABLE IF EXISTS public.metrics CASCADE;
-- DROP TABLE IF EXISTS public.metric_groups CASCADE;

--------------------------------------------------
-- 1. Create Table: metric_groups
--------------------------------------------------
CREATE TABLE IF NOT EXISTS public.metric_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255)  -- Optional column; remove if not needed
);

--------------------------------------------------
-- 2. Create Table: metrics
--------------------------------------------------
CREATE TABLE IF NOT EXISTS public.metrics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    group_id INTEGER REFERENCES public.metric_groups(id)
);

--------------------------------------------------
-- 3. Data Insertion Section
--------------------------------------------------

-- Insert metric groups (if they don't already exist)
INSERT INTO public.metric_groups (name)
VALUES
    ('Performance'),
    ('Efficiency'),
    ('Adaptability and Learning'),
    ('Collaboration and Interaction'),
    ('Trust and Safety'),
    ('Robustness and Generalization')
ON CONFLICT (name) DO NOTHING;

-- Insert metrics using subqueries to get the correct group_id

-- Group 1: Performance
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Prediction Accuracy', (SELECT id FROM public.metric_groups WHERE name = 'Performance')),
    ('Precision', (SELECT id FROM public.metric_groups WHERE name = 'Performance')),
    ('Recall', (SELECT id FROM public.metric_groups WHERE name = 'Performance')),
    ('Overall System Accuracy', (SELECT id FROM public.metric_groups WHERE name = 'Performance')),
    ('Model Improvement Rate', (SELECT id FROM public.metric_groups WHERE name = 'Performance'))
ON CONFLICT DO NOTHING;

-- Group 2: Efficiency
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Response Time', (SELECT id FROM public.metric_groups WHERE name = 'Efficiency')),
    ('Teaching Efficiency', (SELECT id FROM public.metric_groups WHERE name = 'Efficiency')),
    ('Query Efficiency', (SELECT id FROM public.metric_groups WHERE name = 'Efficiency')),
    ('Resource Utilization', (SELECT id FROM public.metric_groups WHERE name = 'Efficiency')),
    ('Task Completion Time', (SELECT id FROM public.metric_groups WHERE name = 'Efficiency')),
    ('Correction Efficiency', (SELECT id FROM public.metric_groups WHERE name = 'Efficiency')),
    ('Error Reduction Rate', (SELECT id FROM public.metric_groups WHERE name = 'Efficiency')),
    ('Knowledge Retention', (SELECT id FROM public.metric_groups WHERE name = 'Efficiency'))
ON CONFLICT DO NOTHING;

-- Group 3: Adaptability and Learning
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Feedback Impact', (SELECT id FROM public.metric_groups WHERE name = 'Adaptability and Learning')),
    ('Adaptability Score', (SELECT id FROM public.metric_groups WHERE name = 'Adaptability and Learning')),
    ('Impact of Corrections', (SELECT id FROM public.metric_groups WHERE name = 'Adaptability and Learning')),
    ('Learning Efficiency', (SELECT id FROM public.metric_groups WHERE name = 'Adaptability and Learning')),
    ('Objective Fulfillment Rate', (SELECT id FROM public.metric_groups WHERE name = 'Adaptability and Learning'))
ON CONFLICT DO NOTHING;

-- Group 4: Collaboration and Interaction
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Human-AI Agreement Rate', (SELECT id FROM public.metric_groups WHERE name = 'Collaboration and Interaction')),
    ('AI Assistance Rate', (SELECT id FROM public.metric_groups WHERE name = 'Collaboration and Interaction')),
    ('Decision Effectiveness', (SELECT id FROM public.metric_groups WHERE name = 'Collaboration and Interaction')),
    ('Time to Resolution', (SELECT id FROM public.metric_groups WHERE name = 'Collaboration and Interaction')),
    ('Human Effort Saved', (SELECT id FROM public.metric_groups WHERE name = 'Collaboration and Interaction'))
ON CONFLICT DO NOTHING;

-- Group 5: Trust and Safety
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Confidence', (SELECT id FROM public.metric_groups WHERE name = 'Trust and Safety')),
    ('Trust Score', (SELECT id FROM public.metric_groups WHERE name = 'Trust and Safety')),
    ('Safety Incidents', (SELECT id FROM public.metric_groups WHERE name = 'Trust and Safety')),
    ('System Reliability', (SELECT id FROM public.metric_groups WHERE name = 'Trust and Safety'))
ON CONFLICT DO NOTHING;

-- Group 6: Robustness and Generalization
INSERT INTO public.metrics (name, group_id)
VALUES
    ('Adversarial Robustness', (SELECT id FROM public.metric_groups WHERE name = 'Robustness and Generalization')),
    ('Domain Generalization', (SELECT id FROM public.metric_groups WHERE name = 'Robustness and Generalization'))
ON CONFLICT DO NOTHING;
