import json
from pathlib import Path
from typing import Optional
import argparse

from engine.metrics_bridge import haic_metrics_for_log, haic_metrics_by_agent_for_log

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--log", required=True, help="Path to MVP results JSON")
    p.add_argument("--baseline", type=float, default=None, help="Baseline seconds (optional)")
    p.add_argument("--rt-max", type=float, default=5.0, help="RT max seconds for HCL (default 5.0)")
    p.add_argument("--by-agent", action="store_true", help="Also compute per-agent pillars")
    args = p.parse_args()

    log = json.loads(Path(args.log).read_text(encoding="utf-8"))

    metrics = haic_metrics_for_log(log, baseline_s=args.baseline, rt_max=args.rt_max)
    out_path = str(args.log).replace(".json", "_haic_metrics.json")
    Path(out_path).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"HAIC metrics saved to: {out_path}")
    print(json.dumps(metrics, indent=2))

    if args.by_agent:
        per_agent = haic_metrics_by_agent_for_log(log, baseline_s=args.baseline, rt_max=args.rt_max)
        out2 = str(args.log).replace(".json", "_haic_metrics_by_agent.json")
        Path(out2).write_text(json.dumps(per_agent, indent=2), encoding="utf-8")
        print(f"Per-agent metrics saved to: {out2}")

if __name__ == "__main__":
    main()