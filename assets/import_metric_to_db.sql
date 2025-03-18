-- Create schema if it does not exist
CREATE SCHEMA IF NOT EXISTS public;

-- Drop tables if exist (useful to start fresh)
-- DROP TABLE IF EXISTS metrics CASCADE;
-- DROP TABLE IF EXISTS metric_groups CASCADE;

-- -- Create table metric_groups
-- CREATE TABLE metric_groups (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(100) NOT NULL UNIQUE
-- );

-- Create table metrics
-- CREATE TABLE metrics (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(100) NOT NULL,
--     group_id INTEGER REFERENCES metric_groups(id)
-- );

-- Insert metric groups first (ensures IDs start from 1)
INSERT INTO metric_groups (name) VALUES
    ('Performance'),
    ('Efficiency'),
    ('Adaptability and Learning'),
    ('Collaboration and Interaction'),
    ('Trust and Safety'),
    ('Robustness and Generalization');

-- Insert the metrics (aligned correctly with group_id)
-- Group 1: Performance
INSERT INTO metrics (name, group_id) VALUES
    ('Prediction Accuracy', 1),
    ('Precision', 1),
    ('Recall', 1),
    ('Overall System Accuracy', 1),
    ('Model Improvement Rate', 1);

-- Group 2: Efficiency
INSERT INTO metrics (name, group_id) VALUES
    ('Response Time', 2),
    ('Teaching Efficiency', 2),
    ('Query Efficiency', 2),
    ('Resource Utilization', 2),
    ('Task Completion Time', 2),
    ('Correction Efficiency', 2),
    ('Error Reduction Rate', 2),
    ('Knowledge Retention', 2);

-- Group 3: Adaptability and Learning
INSERT INTO metrics (name, group_id) VALUES
    ('Feedback Impact', 3),
    ('Adaptability Score', 3),
    ('Impact of Corrections', 3),
    ('Learning Efficiency', 3),
    ('Objective Fulfillment Rate', 3);

-- Group 4: Collaboration and Interaction
INSERT INTO metrics (name, group_id) VALUES
    ('Human-AI Agreement Rate', 4),
    ('AI Assistance Rate', 4),
    ('Decision Effectiveness', 4),
    ('Time to Resolution', 4),
    ('Human Effort Saved', 4);

-- Group 5: Trust and Safety
INSERT INTO metrics (name, group_id) VALUES
    ('Confidence', 5),
    ('Trust Score', 5),
    ('Safety Incidents', 5),
    ('System Reliability', 5);

-- Group 6: Robustness and Generalization
INSERT INTO metrics (name, group_id) VALUES
    ('Adversarial Robustness', 6),
    ('Domain Generalization', 6);
