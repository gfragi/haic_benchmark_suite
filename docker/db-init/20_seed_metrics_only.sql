-- 20_seed_metrics_only.sql
-- Inserts only; assumes tables already exist (created by migrations).
-- Idempotent via WHERE NOT EXISTS checks (no need for unique constraints).

WITH vals(name, description) AS (
  VALUES
    ('Performance', 'Technical performance metrics'),
    ('Efficiency', 'Latency, time, and resource efficiency'),
    ('Adaptability and Learning', 'Learning from feedback and adaptation'),
    ('Collaboration and Interaction', 'Human-AI collaboration quality'),
    ('Trust and Safety', 'User trust and safety-related signals'),
    ('Robustness and Generalization', 'Robustness under shift and generalization')
)
INSERT INTO public.metric_groups (name, description)
SELECT v.name, v.description
FROM vals v
WHERE NOT EXISTS (
  SELECT 1 FROM public.metric_groups g WHERE g.name = v.name
);
WITH rows(name, description, group_name) AS (
  VALUES
    ('Prediction Accuracy',      'Accuracy of predictions',                  'Performance'),
    ('Precision',                'Positive predictive value',                'Performance'),
    ('Recall',                   'Sensitivity / true positive rate',        'Performance'),
    ('Overall System Accuracy',  'End-to-end accuracy',                      'Performance'),
    ('Model Improvement Rate',   'Improvement per iteration',                'Performance'),
    ('Response Time',            'Time to respond',                          'Efficiency'),
    ('Teaching Efficiency',      'Effort to teach the model',                'Efficiency'),
    ('Query Efficiency',         'Effort to retrieve information',           'Efficiency'),
    ('Resource Utilization',     'CPU/GPU/memory use',                       'Efficiency'),
    ('Task Completion Time',     'Time to complete tasks',                   'Efficiency'),
    ('Correction Efficiency',    'Effort to correct mistakes',               'Efficiency'),
    ('Error Reduction Rate',     'Decline in errors over time',              'Efficiency'),
    ('Knowledge Retention',      'Retention of learned info',                'Efficiency'),
    ('Feedback Impact',          'Impact of feedback on performance',        'Adaptability and Learning'),
    ('Adaptability Score',       'Ability to adapt to changes',              'Adaptability and Learning'),
    ('Impact of Corrections',    'Effect of user corrections',               'Adaptability and Learning'),
    ('Learning Efficiency',      'Learning speed/efficiency',                'Adaptability and Learning'),
    ('Objective Fulfillment Rate','Rate of meeting objectives',              'Adaptability and Learning'),
    ('Human-AI Agreement Rate',  'Agreement between human and AI',           'Collaboration and Interaction'),
    ('AI Assistance Rate',       'How often AI helps',                       'Collaboration and Interaction'),
    ('Decision Effectiveness',   'Quality of assisted decisions',            'Collaboration and Interaction'),
    ('Time to Resolution',       'Time to resolve tasks/issues',             'Collaboration and Interaction'),
    ('Human Effort Saved',       'Reduction in human effort',                'Collaboration and Interaction'),
    ('Confidence',               'Model confidence or self-estimate',        'Trust and Safety'),
    ('Trust Score',              'User trust indicators',                    'Trust and Safety'),
    ('Safety Incidents',         'Safety-related incidents',                 'Trust and Safety'),
    ('System Reliability',       'Stability/uptime-related metric',          'Trust and Safety'),
    ('Adversarial Robustness',   'Robustness to adversarial input',          'Robustness and Generalization'),
    ('Domain Generalization',    'Cross-domain generalization',              'Robustness and Generalization')
)
INSERT INTO public.metrics (name, description, group_id)
SELECT r.name, r.description, g.id
FROM rows r
JOIN public.metric_groups g ON g.name = r.group_name
WHERE NOT EXISTS (
  SELECT 1 FROM public.metrics m WHERE m.name = r.name
);
