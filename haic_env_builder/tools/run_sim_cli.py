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
from metrics_core.metrics import compute_metrics_by_agent
from haic_env_builder.utils.insights import summarize_run_brief, interpret_metrics, derive_aux_rates


CONFIG_DIR = (REPO_ROOT / "haic_env_builder" / "configs").resolve()
METRICS_DIR = (REPO_ROOT / "metrics").resolve()

def _safe_config_path(name: str) -> Path:
    p = (CONFIG_DIR / name).resolve()
    if not p.exists() or p.suffix != ".yaml" or not str(p).startswith(str(CONFIG_DIR)):
        sys.exit(f"[!] Config not found or invalid: {name}")
    return p

def main():
    ap = argparse.ArgumentParser(description="Run a HAIC simulation from a YAML config.")
    ap.add_argument("--name", required=True, help="YAML filename under haic_env_builder/configs/")
    ap.add_argument("--seed", type=int, default=None, help="Random seed")
    ap.add_argument("--save-json", action="store_true", help="Write copy of the result JSON into metrics/")
    ap.add_argument("--by-agent", action="store_true", help="Print per-agent metrics breakdown")
    args = ap.parse_args()

    config_path = _safe_config_path(args.name)
    result = simulate_environment(str(config_path), seed=args.seed)

    print("\n=== Simulation Summary ===")
    print(f"Task        : {result.get('task')}")
    print(f"Environment : {result.get('environment', 'n/a')}")
    print(f"Seed        : {result.get('seed')}")
    print(f"Config hash : {result.get('config_hash', 'n/a')}")
    print(f"Log path    : {result.get('log_path')}")

    print("\n--- Metrics ---")
    pprint(result.get("metrics", {}), width=100)

    print("\n--- Insights ---")
    print(summarize_run_brief(result))
    aux = derive_aux_rates(result)
    for line in interpret_metrics(result.get("metrics", {}), **aux):
        print(" •", line)

    if args.by_agent:
        print("\n--- Metrics by agent ---")
        per_agent = compute_metrics_by_agent(result.get("decisions", []))
        pprint(per_agent, width=100)

    print("\n--- Decisions (first 5) ---")
    for row in result.get("decisions", [])[:5]:
        print({k: row.get(k) for k in ["t", "agent", "actor_type", "action", "correct", "off_role_action"]})

    if args.save_json:
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
        out = METRICS_DIR / f"cli_copy_{Path(result['log_path']).name}"
        out.write_text(json.dumps(result, indent=2))
        print(f"\n[✔] Saved: {out}")

if __name__ == "__main__":
    main()
