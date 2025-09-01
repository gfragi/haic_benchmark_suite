#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from pprint import pprint

# ---------- bootstrap: add repo root (directory that contains haic_env_builder/) ----------
def _add_repo_root_to_syspath():
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "haic_env_builder").exists():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            return p
    # fallback to current working dir
    cwd = Path.cwd()
    if (cwd / "haic_env_builder").exists() and str(cwd) not in sys.path:
        sys.path.insert(0, str(cwd))
    return cwd

REPO_ROOT = _add_repo_root_to_syspath()
# ------------------------------------------------------------------------------------------

from haic_env_builder.utils.simulation_runner import simulate_environment
from metrics_core.interaction_metrics import compute_metrics_by_agent
from haic_env_builder.utils.insights import summarize_run_brief, interpret_metrics, derive_aux_rates


CONFIG_DIR = (REPO_ROOT / "haic_env_builder" / "configs").resolve()
METRICS_DIR = (REPO_ROOT / "metrics").resolve()

def _safe_config_path(name: str) -> Path:
    p = (CONFIG_DIR / name).resolve()
    if not p.exists() or p.suffix != ".yaml" or not str(p).startswith(str(CONFIG_DIR)):
        sys.exit(f"[!] Config not found or invalid: {name}")
    return p

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--rt-max", type=float, default=5.0)
    p.add_argument("--baseline-s", type=float, default=None)
    args = p.parse_args()

    run = run_simulation(config_path=args.config, seed=args.seed)
    # assume run.artifacts/events.json already exists or build decisions directly
    decisions = run.decisions  # or load from artifact if you persist events

    summary = compute_metrics(decisions=decisions, rt_max=args.rt_max, baseline_s=args.baseline_s)
    by_agent = compute_metrics_by_agent(decisions, rt_max=args.rt_max, baseline_s=args.baseline_s)

    out = {"summary": summary, "by_agent": by_agent, "params": {"rt_max": args.rt_max, "baseline_s": args.baseline_s}}
    out_dir = Path(run.output_dir) / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "core_v1.json").write_text(json.dumps(out, indent=2))

    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
