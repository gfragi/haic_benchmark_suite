import math
from haic_env_builder.utils.metrics import compute_metrics

def test_compute_metrics_empty():
    m = compute_metrics([], total_time=10.0)
    assert m == {"F":0.0,"D":0.0,"HCL":0.0,"Tr":0.0,"A":0.0,"S":0.0,"EL":0.0}

def test_compute_metrics_basic():
    decisions = [
        {"t":0.0,"actor":"ai","action":"suggest","latency":0.10,"accepted":True,"reward":0.0},
        {"t":0.5,"actor":"human","action":"confirm","latency":0.40,"reward":0.1},
        {"t":1.0,"actor":"ai","action":"suggest","latency":0.12,"accepted":False,"reward":0.2},
        {"t":1.5,"actor":"human","action":"override","latency":0.35,"reward":0.25},
    ]
    m = compute_metrics(decisions)  # total_time inferred = 1.5 - 0.0 = 1.5
    assert m["F"] > 0                      # some events / time
    assert 0 <= m["D"] <= 1                # balanced-ish
    assert 0 <= m["HCL"] <= 1              # clipped
    assert 0 <= m["Tr"] <= 1               # suggestions override rate
    assert math.isclose(m["A"], 0.25 - 0.0, rel_tol=1e-6)
    assert m["S"] == 0.0                   # placeholder
    assert m["EL"] > 0                     # average latency

def test_compute_metrics_total_time_override():
    decisions = [
        {"t":0.0,"actor":"ai","action":"s","latency":0.1},
        {"t":10.0,"actor":"human","action":"h","latency":0.3},
    ]
    m1 = compute_metrics(decisions)               # inferred total_time=10.0
    m2 = compute_metrics(decisions, total_time=5) # forced total_time=5.0
    assert m2["F"] == 2/5 and m1["F"] == 2/10
