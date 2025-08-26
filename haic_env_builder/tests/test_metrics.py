# haic_env_builder/tests/test_metrics.py
from haic_env_builder.utils.metrics import compute_metrics

def test_compute_metrics_basic():
    decisions = [
        {"t": 0.0, "agent":"A","actor_type":"ai","action":"x","duration_s":1.0,"correct":True},
        {"t": 1.0, "agent":"A","actor_type":"ai","action":"x","duration_s":1.0,"correct":True},
        {"t": 2.0, "agent":"A","actor_type":"ai","action":"x","duration_s":1.0,"correct":False},
        {"t": 3.0, "agent":"A","actor_type":"ai","action":"x","duration_s":1.0,"correct":True},
    ]
    m = compute_metrics(decisions=decisions, T=None, baseline_s=2.0)
    assert m["F"] > 0
    assert 0 <= m["HCL"] <= 1
    assert 0 <= m["Tr"] <= 1
