
import json, os, time, uuid
from datetime import datetime
from typing import Dict, Any
from .base import Environment
from .plugins import make_agent, make_object, make_environment

def run_from_config(cfg: Dict[str, Any], results_dir: str = "results") -> str:
    env: Environment = make_environment(cfg["environment"])
    env.sim_id = cfg.get("sim_id") or f"sim_{uuid.uuid4().hex[:8]}"
    for a in cfg.get("agents", []): env.add_agent(make_agent(a))
    for o in cfg.get("objects", []): env.add_object(make_object(o))
    t = 0
    for step in cfg.get("script", []):
        t = step.get("t", t + 1)
        agent = env.agents[step["agent"]]
        obj = env.objects[step["object"]]
        decision = agent.act(step["action"], obj, effect=step.get("effect", {}), t=t)
        decision.correct = step.get("correct")
        decision.latency_ms = step.get("latency_ms")
        env.record(decision)
        if step.get("sleep_ms"): time.sleep(step["sleep_ms"]/1000)
    os.makedirs(results_dir, exist_ok=True)
    out = os.path.join(results_dir, f'{env.sim_id}_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.json')
    with open(out, "w", encoding="utf-8") as f: json.dump(env.to_log_json(), f, ensure_ascii=False, indent=2)
    return out
