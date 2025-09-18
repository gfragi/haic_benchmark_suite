
import json
from pathlib import Path
from typing import Dict, Any
from haic_mvp_sim.engine.run_sim import run_from_config
from haic_mvp_sim.engine.datasets import load_csv, make_script_from_dataset
from haic_mvp_sim.engine.policies import ThresholdPolicy, L2DPolicy
from haic_mvp_sim.engine.evaluate import compute_metrics

def run_experiment(dataset_csv: str, mode: str = "baseline", results_dir: str = "results"):
    rows = load_csv(dataset_csv)
    cfg: Dict[str, Any] = {
        "sim_id": f"exp_{mode}",
        "environment": {"id":"HAIC_Exp","class":"base.Environment","attributes":{"task":"classification"}},
        "agents": [
            {"id":"AI","class":"base.Agent","model":"ai","affordances":["classify"]},
            {"id":"H","class":"base.Agent","model":"human","affordances":["classify"]}
        ],
        "objects": [{"id": f"O{i+1}","class":"base.Object","attributes":{"row":i+1},"affordances":["classify"]}
                    for i in range(len(rows))],
        "script": []
    }
    policy = ThresholdPolicy() if mode=="baseline" else L2DPolicy()
    cfg["script"] = make_script_from_dataset(rows, "AI", "H", ai_policy=policy, human_accuracy=0.9)
    out_log = run_from_config(cfg, results_dir=results_dir)
    log = json.loads(Path(out_log).read_text(encoding="utf-8"))
    metrics = compute_metrics(log)
    Path(out_log.replace(".json","_metrics.json")).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return {"log": out_log, "summary": metrics}

if __name__ == "__main__":
    import argparse, json as _j
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True)
    p.add_argument("--mode", choices=["baseline","l2d"], default="baseline")
    p.add_argument("--results", default="results")
    a = p.parse_args()
    print(_j.dumps(run_experiment(a.dataset, a.mode, a.results), indent=2))
