from metrics_core.interaction_metrics import compute_metrics

def test_e2e_core_metrics_smoke(simulated_run_decisions):
    out = compute_metrics(simulated_run_decisions, rt_max=5.0, baseline_s=60.0)
    # Keys exist
    for k in ["F","D","HCL","Tr","A","S","EL","EfficiencyScore"]:
        assert k in out
    # Ranges sane
    assert 0.0 <= out["HCL"] <= 1.0
    assert 0.0 <= out["Tr"]  <= 1.0
    assert 0.0 <= out["S"]   <= 1.0
    assert out["EL"] >= 0.0