# tests/test_metrics.py
from metrics_core.metrics import compute_metrics

def approx(x, y, eps=1e-6):
    return abs(x - y) <= eps

def test_empty_decisions_all_zero():
    m = compute_metrics(decisions=[])
    assert m["F"] == 0.0
    assert m["D"] == 0.0
    assert m["HCL"] == 0.0 or 0.0 <= m["HCL"] <= 1.0  # defensive
    assert m["Tr"] == 1.0  # no errors over N=0 -> clip01(1 - 0) == 1
    assert m["A"] == 0.0
    assert m["S"] == 0.0
    assert m["EL"] == 0.0

def test_frequency_per_minute_with_T_override():
    # 4 decisions across any times; force T=60s -> F = N / (T/60) = 4 / 1 = 4
    decisions = [
        {"t": 0.0,  "duration_s": 1.0},
        {"t": 10.0, "duration_s": 1.0},
        {"t": 20.0, "duration_s": 1.0},
        {"t": 30.0, "duration_s": 1.0},
    ]
    m = compute_metrics(decisions=decisions, T=60.0)
    assert approx(m["F"], 4.0)

def test_frequency_from_timestamps():
    # 4 events from t=0 to t=15s -> total_time=15 => F = 4 / (15/60) = 16
    decisions = [
        {"t": 0.0,  "duration_s": 1.0},
        {"t": 5.0,  "duration_s": 1.0},
        {"t": 10.0, "duration_s": 1.0},
        {"t": 15.0, "duration_s": 1.0},
    ]
    m = compute_metrics(decisions=decisions)
    assert approx(m["F"], 16.0)

def test_HCL_uses_human_durations():
    # mean human RT = (1.0 + 2.0) / 2 = 1.5; rt_max=5.0 -> HCL = 1 - 1.5/5 = 0.7
    decisions = [
        {"t": 0.0, "actor_type": "human", "duration_s": 1.0},
        {"t": 1.0, "actor_type": "human", "duration_s": 2.0},
        {"t": 2.0, "actor_type": "ai",    "duration_s": 0.2},
    ]
    m = compute_metrics(decisions=decisions, rt_max=5.0)
    assert approx(m["HCL"], 0.7)

def test_Tr_errors_decrease_trust():
    # 1 error in 5 -> Tr = 1 - 1/5 = 0.8
    decisions = [
        {"t": 0.0, "correct": True},
        {"t": 1.0, "correct": True},
        {"t": 2.0, "correct": False},  # one error
        {"t": 3.0, "correct": True},
        {"t": 4.0, "correct": True},
    ]
    m = compute_metrics(decisions=decisions)
    assert approx(m["Tr"], 0.8)

def test_A_adaptability_relative_improvement():
    # N=10; early k=2, late k=2 (20% rule).
    # early acc = 1/2 = 0.5; late acc = 2/2 = 1.0
    # A = (1.0 - 0.5) / 0.5 = 1.0
    decisions = []
    # early
    decisions += [
        {"t": 0, "correct": True},
        {"t": 1, "correct": False},
    ]
    # middle
    decisions += [{"t": i, "correct": True} for i in range(2, 8)]
    # late
    decisions += [
        {"t": 8, "correct": True},
        {"t": 9, "correct": True},
    ]
    m = compute_metrics(decisions=decisions)
    assert approx(m["A"], 1.0)

def test_S_similarity_from_actions():
    # 3/4 action matches -> S = 0.75
    decisions = [
        {"t": 0, "action": "a", "surrogate_action": "a"},
        {"t": 1, "action": "b", "surrogate_action": "b"},
        {"t": 2, "action": "c", "surrogate_action": "x"},
        {"t": 3, "action": "d", "surrogate_action": "d"},
    ]
    m = compute_metrics(decisions=decisions)
    assert approx(m["S"], 0.75)

def test_S_similarity_from_prob_overlap():
    decisions = [
        {
            "t": 0,
            "probs": {"a": 0.8, "b": 0.2},
            "surrogate_probs": {"a": 0.7, "b": 0.3},
        }
    ]
    m = compute_metrics(decisions=decisions)
    # JS-based similarity ~ 0.9745961562775189
    assert abs(m["S"] - 0.9745961562775189) < 1e-6


def test_EL_efficiency_latency_against_baseline():
    # total_time = last-first = 120 - 0 = 120s; baseline=100s -> EL = (120-100)/100 = 0.2
    decisions = [{"t": 0}, {"t": 120}]
    m = compute_metrics(decisions=decisions, baseline_s=100.0)
    assert approx(m["EL"], 0.2)
