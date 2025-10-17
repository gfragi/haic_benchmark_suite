
import json, os, time, uuid
from datetime import datetime
from typing import Dict, Any
from .base import Environment
from .plugins import make_agent, make_object, make_environment

def run_from_config(cfg: Dict[str, Any], results_dir: str = "results") -> str: # Run a simulation from a configuration dictionary
    env: Environment = make_environment(cfg["environment"]) # Create environment

    env.sim_id = cfg.get("sim_id") or f"sim_{uuid.uuid4().hex[:8]}" # Unique simulation ID

    for a in cfg.get("agents", []): env.add_agent(make_agent(a)) # Add agents to the environment

    for o in cfg.get("objects", []): env.add_object(make_object(o)) # Add objects to the environment

    t = 0 # Current time step

    for step in cfg.get("script", []): # Execute each step in the script
        t = step.get("t", t + 1)
        agent = env.agents[step["agent"]] # Get the agent
        obj = env.objects[step["object"]] # Get the object
        decision = agent.act(step["action"], obj, effect=step.get("effect", {}), t=t)
        decision.correct = step.get("correct")
        decision.latency_ms = step.get("latency_ms")
        env.record(decision)

        if step.get("sleep_ms"): time.sleep(step["sleep_ms"]/1000) # Optional delay

    os.makedirs(results_dir, exist_ok=True) # Ensure results directory exists

    out = os.path.join(results_dir, f'{env.sim_id}_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.json')
    with open(out, "w", encoding="utf-8") as f: json.dump(env.to_log_json(), f, ensure_ascii=False, indent=2)

    return out
