-- Insert the metric groups
INSERT INTO metric_groups (group_name) VALUES
    ('Performance'),
    ('Efficiency'),
    ('Adaptability and Learning'),
    ('Collaboration and Interaction'),
    ('Trust and Safety'),
    ('Robustness and Generalization');

-- Insert the metrics for each group
-- Group 1: Performance
INSERT INTO metrics (metric_name, group_id) VALUES
    ('Prediction Accuracy', 1),
    ('Precision', 1),
    ('Recall', 1),
    ('Overall System Accuracy', 1),
    ('Model Improvement Rate', 1);

-- Group 2: Efficiency
INSERT INTO metrics (metric_name, group_id) VALUES
    ('Response Time', 2),
    ('Teaching Efficiency', 2),
    ('Query Efficiency', 2),
    ('Resource Utilization', 2),
    ('Task Completion Time', 2),
    ('Correction Efficiency', 2),
    ('Error Reduction Rate', 2),
    ('Knowledge Retention', 2);

-- Group 3: Adaptability and Learning
INSERT INTO metrics (metric_name, group_id) VALUES
    ('Feedback Impact', 3),
    ('Adaptability Score', 3),
    ('Impact of Corrections', 3),
    ('Learning Efficiency', 3),
    ('Objective Fulfillment Rate', 3);

-- Group 4: Collaboration and Interaction
INSERT INTO metrics (metric_name, group_id) VALUES
    ('Human-AI Agreement Rate', 4),
    ('AI Assistance Rate', 4),
    ('Decision Effectiveness', 4),
    ('Time to Resolution', 4),
    ('Human Effort Saved', 4);

-- Group 5: Trust and Safety
INSERT INTO metrics (metric_name, group_id) VALUES
    ('Confidence', 5),
    ('Trust Score', 5),
    ('Safety Incidents', 5),
    ('System Reliability', 5);

-- Group 6: Robustness and Generalization
INSERT INTO metrics (metric_name, group_id) VALUES
    ('Adversarial Robustness', 6),
    ('Domain Generalization', 6);
