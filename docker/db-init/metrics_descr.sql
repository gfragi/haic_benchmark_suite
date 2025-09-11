BEGIN;

-- Effectiveness
UPDATE public.metrics SET description = 'Share of correct outcomes over all evaluated cases.'
WHERE name = 'Prediction Accuracy' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Share of predicted positives that are truly positive (precision = TP / (TP + FP)).'
WHERE name = 'Precision' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Share of actual positives that were found (recall = TP / (TP + FN)).'
WHERE name = 'Recall' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Overall accuracy considering the end-to-end system context.'
WHERE name = 'Overall System Accuracy' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Change in performance vs. a baseline or earlier period (improvement over time).'
WHERE name = 'Model Improvement Rate' AND (description IS NULL OR description = '');

-- Efficiency
UPDATE public.metrics SET description = 'Average response/processing latency per task or event.'
WHERE name = 'Response Time' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'How effectively teaching/training actions translate to better outcomes.'
WHERE name = 'Teaching Efficiency' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'How many useful results you get per unit of querying/interaction effort.'
WHERE name = 'Query Efficiency' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Share of available resources consumed (e.g., CPU/GPU, memory, budget).'
WHERE name = 'Resource Utilization' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Time to finish a task from start to completion.'
WHERE name = 'Task Completion Time' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Speed/effort of applying corrections relative to issues found.'
WHERE name = 'Correction Efficiency' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Decrease in errors after AI/human interventions (higher = fewer errors remain).'
WHERE name = 'Error Reduction Rate' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'How well learned knowledge persists over time or transfers to later tasks.'
WHERE name = 'Knowledge Retention' AND (description IS NULL OR description = '');

-- Adaptability and Learning
UPDATE public.metrics SET description = 'Impact of feedback events on subsequent performance (learning from feedback).'
WHERE name = 'Feedback Impact' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Overall capacity to adjust to new conditions, data, or goals.'
WHERE name = 'Adaptability Score' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Effect that applied corrections have on improving outcomes.'
WHERE name = 'Impact of Corrections' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Performance gain achieved per unit of training/feedback effort.'
WHERE name = 'Learning Efficiency' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Rate at which the system or team meets stated objectives.'
WHERE name = 'Objective Fulfillment Rate' AND (description IS NULL OR description = '');

-- Collaboration and Interaction
UPDATE public.metrics SET description = 'How often human and AI reach the same (correct) conclusions.'
WHERE name = 'Human-AI Agreement Rate' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Share of steps assisted by the AI (indicator of AI involvement).'
WHERE name = 'AI Assistance Rate' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Quality of decisions when combining human judgment and AI suggestions.'
WHERE name = 'Decision Effectiveness' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Time from problem identification to successful resolution.'
WHERE name = 'Time to Resolution' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Amount of manual work avoided due to AI assistance.'
WHERE name = 'Human Effort Saved' AND (description IS NULL OR description = '');

-- Trust and Safety
UPDATE public.metrics SET description = 'Calibrated confidence in outputs (or user-reported confidence with the system).'
WHERE name = 'Confidence' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Composite trust indicator (confidence, consistency, clarity of rationale).'
WHERE name = 'Trust Score' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Number of safety-related incidents or violations (lower is better).'
WHERE name = 'Safety Incidents' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Uptime and fault tolerance; probability the system works as expected.'
WHERE name = 'System Reliability' AND (description IS NULL OR description = '');

-- Robustness and Generalization
UPDATE public.metrics SET description = 'Performance under adversarial or stressful inputs (resistance to attacks).'
WHERE name = 'Adversarial Robustness' AND (description IS NULL OR description = '');

UPDATE public.metrics SET description = 'Ability to maintain performance across domains, cohorts, or distributions.'
WHERE name = 'Domain Generalization' AND (description IS NULL OR description = '');

COMMIT;
