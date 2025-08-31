from metrics_core.metrics import compute_metrics as core_compute
from metics_core.metrics import compute_metrics as sim_compute

def test_core_vs_sim_equivalence(sample_decisions):
    out_core = core_compute(decisions=sample_decisions, rt_max=5.0, baseline_s=10.0)
    out_sim  = sim_compute(decisions=sample_decisions, rt_max=5.0, baseline_s=10.0)
    assert out_core == out_sim
