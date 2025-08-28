import yaml
from haic_env_builder.utils.simulation_runner import simulate_environment

def _simulate(cfg_text: str):
    import tempfile, os
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write(cfg_text); path = f.name
    try:
        return simulate_environment(path, seed=123)
    finally:
        os.unlink(path)

def test_ct_scan_adapter_smoke():
    cfg = """
task:
  name: CT Scan Diagnosis
  parameters:
    environment: ct_scan
    env_params: {steps: 3, dt: 0.1}
agents:
  - name: RadiologistAssistant
    modality: policy
  - name: VoiceSupportBot
    modality: policy
profiles: []
"""
    out = _simulate(cfg)
    assert out["status"] == "success"
    assert out["agents"] == ["RadiologistAssistant", "VoiceSupportBot"]
    assert len(out["decisions"]) == 3*2
    assert {"F","D","HCL","Tr","A","S","EL","EfficiencyScore"} <= set(out["metrics"].keys())

def test_overcooked_adapter_importable():
    cfg = """
task:
  name: Overcooked CrampedRoom
  parameters:
    environment: overcooked
    env_params: {layout_name: CrampedRoom, dt: 0.1, horizon_s: 0.3}
agents:
  - name: agent_0
    modality: policy
  - name: agent_1
    modality: policy
profiles: []
"""
    try:
        out = _simulate(cfg)
        assert out["status"] == "success"
        assert len(out["decisions"]) > 0
    except RuntimeError as e:
        # If Overcooked isn't installed, that's acceptable; assert helpful error
        assert "Overcooked not installed" in str(e)
