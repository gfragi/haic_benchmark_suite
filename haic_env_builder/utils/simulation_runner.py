from __future__ import annotations
from typing import Dict, Any, List, Optional, Sequence
from pathlib import Path
import json
from datetime import datetime
import random as _random
import hashlib
import yaml

from haic_env_builder.components.agent import Agent
from haic_env_builder.components.profile import Profile
from haic_env_builder.components.task import Task
from haic_env_builder.utils.metrics import compute_metrics
from haic_env_builder.utils.random_seed import set_all_seeds
from haic_env_builder.utils.event_enrichment import enrich_decisions
from haic_env_builder.adapters.registry import create_adapter
from haic_env_builder.utils.metrics import compute_metrics_by_agent


# -------------------------
# Helpers
# -------------------------

def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)

_POLICY_CACHE: Dict[str, Any] = {}

def _get_policy(agent) -> Any | None:
    name = getattr(agent, "name", "agent")
    if name in _POLICY_CACHE:
        return _POLICY_CACHE[name]
    runtime = getattr(agent, "runtime", None) or getattr(agent, "policy", None)
    policy = None
    if runtime:
        try:
            from haic_env_builder.registry.agent_registry import make_policy  # lazy
            policy = make_policy(runtime)
        except Exception:
            try:
                from haic_env_builder.registry.agent_registry import RUNTIME_POLICIES  # lazy
                factory = RUNTIME_POLICIES.get(runtime)
                if factory is not None:
                    policy = factory() if callable(factory) else factory
            except Exception:
                policy = None
    _POLICY_CACHE[name] = policy
    return policy

def _policy_raw_action(agent) -> Optional[str]:
    """Ask policy for an action without clamping. Returns None if no policy or unusable output."""
    aname = getattr(agent, "name", "agent")
    pol = _get_policy(agent)
    if not pol or not hasattr(pol, "act"):
        return None
    try:
        out = pol.act([aname])
    except TypeError:
        out = pol.act(aname)
    if isinstance(out, dict):
        return out.get(aname) or (next(iter(out.values())) if out else None)
    return out if isinstance(out, str) else None

def _ensure_time(rows: List[Dict[str, Any]], t_value: float) -> None:
    for r in rows or []:
        if r.get("t") is None:
            r["t"] = t_value

# -------------------------
# Main entry
# -------------------------

def simulate_environment(config_path: str, seed: Optional[int] = None) -> Dict[str, Any]:
    cfg = _load_yaml(config_path)

    # stable config hash for provenance (never null)
    try:
        from haic_env_builder.utils.config_hash import stable_config_hash as _cfg_hash
        config_hash = _cfg_hash(cfg)
    except Exception:
        _bytes = yaml.safe_dump(cfg, sort_keys=True).encode("utf-8")
        config_hash = hashlib.sha256(_bytes).hexdigest()[:16]

    # seed (deterministic)
    if seed is not None:
        set_all_seeds(seed)

    # Parse core entities (env-agnostic)
    task = Task(**cfg["task"])
    agents = [Agent(**a) for a in cfg["agents"]]
    profiles = [Profile(**p) for p in cfg.get("profiles", [])]

    params = task.parameters or {}
    env_name = params.get("environment") or params.get("adapter")
    if not env_name:
        raise ValueError("Task.parameters must include 'environment' (e.g., 'overcooked', 'ct_scan', ...).")

    env_params = params.get("env_params", {}) or {}
    adapter = create_adapter(env_name, **env_params)
    adapter.reset(seed=seed)

    # dt used to synthesize timestamps only when the adapter omits 't'
    dt = float(params.get("dt", 0.1))
    t_cur = 0.0
    local_rng = _random.Random(seed if seed is not None else 0)

    # Ask adapter for valid actions per agent
    action_spaces: Dict[str, Sequence[str]] = {a.name: tuple(adapter.action_space(a.name)) for a in agents}

    # Prepare agent dicts for enrichment (inject action_space for off-role detection)
    agents_for_enrich: List[Dict[str, Any]] = []
    for a in agents:
        ad = dict(a.__dict__)
        ad["action_space"] = list(action_spaces.get(a.name) or [])
        agents_for_enrich.append(ad)

    # Generic rollout loop
    decisions: List[Dict[str, Any]] = []
    info: Dict[str, Any] = {}
    env_events_all: List[Dict[str, Any]] = []

    while True:
        # 1) Build action map; keep raw (proposed) before clamping to space
        a_map: Dict[str, str] = {}
        proposed_map: Dict[str, Optional[str]] = {}

        for a in agents:
            allowed = list(action_spaces.get(a.name) or [])
            if not allowed:
                raise RuntimeError(f"Adapter '{env_name}' returned empty action space for agent '{a.name}'.")

            raw_act = _policy_raw_action(a)
            proposed_map[a.name] = raw_act

            # clamp/fallback
            if isinstance(raw_act, str) and raw_act in allowed:
                final_act = raw_act
            else:
                final_act = local_rng.choice(allowed)

            a_map[a.name] = final_act

        # 2) Step the adapter
        step_out, done = adapter.step(a_map)

        # 3) Normalize StepOutput-like payload
        if hasattr(step_out, "decisions"):
            dec_rows = list(getattr(step_out, "decisions", []))
            ev_rows = list(getattr(step_out, "events", []))
            info = getattr(step_out, "info", {}) or {}
        elif isinstance(step_out, dict):
            dec_rows = list(step_out.get("decisions", []))
            ev_rows = list(step_out.get("events", []))
            info = step_out.get("info", {}) or {}
        else:
            raise TypeError("Adapter step must return StepOutput-like object or dict with 'decisions'/'events'/'info'.")

        # 4) Ensure time on both decisions and events if adapter omitted it
        _ensure_time(dec_rows, t_cur)
        _ensure_time(ev_rows, t_cur)

        # 5) Annotate decisions with proposed_action for off-role metrics
        for r in dec_rows:
            an = r.get("agent")
            pa = proposed_map.get(an)
            if r.get("surrogate_action") is None and r.get("proposed_action") is not None:
                r["surrogate_action"] = r["proposed_action"] 

        # 6) Append rows; keep env events separate
        decisions.extend(dec_rows)
        env_events_step: List[Dict[str, Any]] = []
        for e in ev_rows:
            if isinstance(e, dict) and ("agent" in e and "action" in e):
                decisions.append(e)  # agent-originated event with an action
            else:
                env_events_step.append(e)
        env_events_all.extend(env_events_step)

        # 7) Advance synthetic clock
        t_cur += dt

        if done:
            break

    # Sort & enrich
    decisions.sort(key=lambda x: float(x.get("t", 0.0)))

    rng = _random.Random(seed if seed is not None else 0)
    decisions = enrich_decisions(
        decisions=decisions,
        agents=agents_for_enrich,                 # includes action_space for off-role
        profiles=[p.__dict__ for p in profiles],
        scenario=task.name,
        rng=rng,
    )

    # Normalize rows (remove null proposed_action)
    for r in decisions:
        if r.get("proposed_action", "__MISSING__") is None:
            r.pop("proposed_action", None)

    # Metrics
    explicit_T = (decisions[-1]["t"] - decisions[0]["t"]) if len(decisions) >= 2 else 0.0
    metrics = compute_metrics(
        decisions=decisions,
        T=explicit_T,
        baseline_s=params.get("baseline_s"),
        rt_max=params.get("rt_max", 5.0),
    )
    # Keep EfficiencyScore consistent with EL
    try:
        el = float(metrics.get("EL", 0.0))
        metrics["EfficiencyScore"] = 1.0 / (1.0 + max(0.0, el))
    except Exception:
        pass

    metrics_by_agent = compute_metrics_by_agent(decisions=decisions, T=explicit_T,
                                            baseline_s=params.get("baseline_s"),
                                            rt_max=params.get("rt_max", 5.0))

    # Response payload
    result = {
        "task": task.name,
        "seed": seed,
        "agents": [a.name for a in agents],
        "profiles": [
            getattr(p, "profile_id", None) or getattr(p, "id", None) or getattr(p, "role", None) or f"profile_{i}"
            for i, p in enumerate(profiles)
        ],
        "metrics": metrics,
        "decisions": decisions,
        "info": info,
        "status": "success",
        # provenance
        "config_hash": config_hash,
        "config_path": str(Path(config_path).resolve()),
        "config": {
            "environment": env_name,
            "env_params": env_params,
            "dt": dt,
        },
        "events": env_events_all,
        "metrics_by_agent": metrics_by_agent,
    }

    # Persist artifact with readable timestamp + hash in filename
    out_dir = Path("metrics"); out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_task = task.name.replace(" ", "_")
    out_path = out_dir / f"{safe_task}_full_{config_hash}_{ts}.json"
    out_path.write_text(json.dumps(result, indent=2))
    result["log_path"] = str(out_path)

    return result
