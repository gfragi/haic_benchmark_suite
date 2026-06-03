"""
Smart Energy Pilot — Test Dataset Generator
============================================
All tunable parameters are in the CONFIG block below.
Change anything there — number of operators, sessions per policy,
model versions, thresholds, timing, task parameters — and re-run.
The rest of the file is logic; it reads only from CONFIG.

Output: pilot_se_v0_test_dataset.json  (platform-ready, matches HAIC schema)
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta, timezone

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG  — everything you might want to change is here
# ══════════════════════════════════════════════════════════════════════════════

CONFIG = {

    # ── Identifiers ───────────────────────────────────────────────────────────
    "sim_id":        "pilot_se_v0",
    "pilot_tag":     "energy",
    "app_version":   "se_v2.0",

    # ── Model versions (change when you update the pilot models) ──────────────
    "ai_model_version":    "rf-security-2025-v2.quick",
    "agent_model_version": "operator-agent-llm-v2",
    "forecast_model":      "xgboost-forecast-2025-v2",

    # ── Operators ─────────────────────────────────────────────────────────────
    # Add/remove operator ids here. Policies will round-robin across them.
    # Having multiple operators enables the Fairness slice in the dashboard.
    "operator_ids": ["op_01", "op_02", "op_03", "op_04", "op_05"],

    # ── Sessions per policy ───────────────────────────────────────────────────
    # Each session = one operator working through n_cycles grid states.
    # More sessions -> auto-derivation of baseline_s becomes available.
    "sessions_per_policy": 3,     # increase to 3+ for EL auto-derivation
    "n_cycles_per_session": 220,   # grid states assessed per session

    # ── Policies to generate ──────────────────────────────────────────────────
    # Remove a policy name to skip it.
    "policies": ["baseline", "al_aided", "agent_mediated"],

    # ── Task parameters (written into meta block; read by platform) ───────────
    # rt_max_s:    maximum expected human reaction time for this task (seconds).
    #              Grid security review is deliberate -- 120s is realistic.
    #              If too low, HCL will be artificially deflated.
    # baseline_s:  expected human task duration WITHOUT AI assistance (seconds).
    #              Used to compute Effort Loss (EL). Based on domain knowledge:
    #              a trained operator doing N-1 review without AI ~ 90-120s.
    "task_parameters": {
        "rt_max_s":   120.0,
        "baseline_s":  95.0,
        "task":        "n1_security_assessment",
        "domain":      "energy_grid",
    },

    # ── AI behaviour ──────────────────────────────────────────────────────────
    # ai_accuracy:   probability that the AI classification is correct.
    #                Current pilot baseline is 0.92.
    # ai_latency_ms: mean RF classifier response time (milliseconds).
    # agent_latency_ms: mean OperatorAgent (LLM) response time.
    "ai_accuracy":       0.92,
    "ai_latency_ms":     145.0,
    "agent_latency_ms":  3500.0,

    # ── Deferral thresholds ───────────────────────────────────────────────────
    # tau:           Baseline / Agent-Mediated defer band: defer if
    #                prob_secure in (1-tau, tau).  0.75 means defer when
    #                the AI is between 25% and 75% confident.
    # al_risk_cutoff: AL-Aided defers states with risk_score above this,
    #                in addition to al_flagged states.
    "tau":            0.65,
    "al_risk_cutoff": 0.55,

    # ── Operator behaviour per policy ─────────────────────────────────────────
    # agree_rate:           probability operator accepts the AI recommendation.
    # duration_s:           mean decision time in seconds.
    # override_correct_rate: probability operator is right when they override.
    "operator_profiles": {
        "baseline": {
            "agree_rate":             0.72,
            "duration_s":             52.0,
            "override_correct_rate":  0.65,
        },
        "al_aided": {
            "agree_rate":             0.58,   # sees harder cases -> more overrides
            "duration_s":             68.0,   # deliberate labelling takes longer
            "override_correct_rate":  0.78,   # AL cases: operator is more often right
        },
        "agent_mediated": {
            "agree_rate":             0.80,   # agent summary nudges toward agreement
            "duration_s":             34.0,   # faster: agent did the reading
            "override_correct_rate":  0.65,
        },
    },

    # ── Grid state distribution ───────────────────────────────────────────────
    # Beta(alpha, beta) shape for prob_secure.  Beta(6,2) is right-skewed
    # (most states are secure) -- realistic for a well-managed grid.
    "prob_secure_beta_alpha": 6,
    "prob_secure_beta_beta":  2,

    # Regional and weather distributions (must sum to 1.0 each)
    "regions":        ["north", "south", "central", "islands"],
    "region_weights": [0.30,    0.25,    0.30,      0.15],

    "weather_regimes": ["normal", "high_wind", "peak_demand", "storm", "low_generation"],
    "weather_weights": [0.50,     0.20,        0.15,          0.05,    0.10],

    # Multipliers applied to prob_secure in adverse conditions
    "weather_risk_multipliers": {"storm": 0.75, "peak_demand": 0.75},
    "region_risk_multipliers":  {"islands": 0.85},

    # ── Timing ────────────────────────────────────────────────────────────────
    # Mean gap between arriving grid states (seconds). ~3 min is realistic
    # for a real-time grid monitoring loop.
    "grid_state_arrival_s": 180.0,

    # Start datetime for session 0. Subsequent sessions are offset by 1 day.
    "start_datetime": "2026-03-10T06:00:00Z",

    # ── Output ────────────────────────────────────────────────────────────────
    "output_path": "haic_sim_mvp/examples/pilot_se_v2_test_dataset.json",

    # ── Reproducibility ───────────────────────────────────────────────────────
    "random_seed": 42,
}

# ══════════════════════════════════════════════════════════════════════════════
#  GENERATOR  -- reads from CONFIG; no magic numbers below this line
# ══════════════════════════════════════════════════════════════════════════════

random.seed(CONFIG["random_seed"])
np.random.seed(CONFIG["random_seed"])

XAI_FACTORS = [
    "load_margin", "line_loading_L014", "voltage_bus_B07",
    "generation_imbalance", "reactive_power_deficit",
]


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def jitter(base, spread=0.30):
    """Gaussian noise around a base value; always positive."""
    return round(max(1.0, base * (1 + random.gauss(0, spread))), 2)


def parse_start():
    s = CONFIG["start_datetime"]
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def make_grid_state(idx):
    region  = random.choices(CONFIG["regions"],        CONFIG["region_weights"])[0]
    weather = random.choices(CONFIG["weather_regimes"], CONFIG["weather_weights"])[0]

    prob = float(np.random.beta(
        CONFIG["prob_secure_beta_alpha"],
        CONFIG["prob_secure_beta_beta"],
    ))

    if weather in CONFIG["weather_risk_multipliers"]:
        prob *= CONFIG["weather_risk_multipliers"][weather]
    if region in CONFIG["region_risk_multipliers"]:
        prob *= CONFIG["region_risk_multipliers"][region]

    prob = round(min(0.99, max(0.01, prob)), 3)

    naive_gt  = prob > 0.5
    flip      = random.random() < (1 - CONFIG["ai_accuracy"])
    secure_gt = not naive_gt if flip else naive_gt

    al_flag     = 0.35 < prob < 0.72
    risk_score  = round(min(1.0, (1 - prob) + (0.10 if al_flag else 0)), 3)
    ai_decision = "secure" if prob >= 0.50 else "insecure"
    ai_correct  = (ai_decision == "secure") == secure_gt

    return {
        "grid_state_id":  f"GS_{idx:06d}",
        "prob_secure":    prob,
        "secure_gt":      secure_gt,
        "ai_decision":    ai_decision,
        "ai_correct":     ai_correct,
        "al_flag":        al_flag,
        "risk_score":     risk_score,
        "region":         region,
        "weather_regime": weather,
        "xai_top_factor": random.choice(XAI_FACTORS),
    }


def is_deferred(gs, policy):
    tau = CONFIG["tau"]
    if policy in ("baseline", "agent_mediated"):
        return (1 - tau) < gs["prob_secure"] < tau
    if policy == "al_aided":
        return gs["al_flag"] or gs["risk_score"] > CONFIG["al_risk_cutoff"]
    raise ValueError(f"Unknown policy: {policy}")


def simulate_operator(gs, policy):
    prof = CONFIG["operator_profiles"][policy]
    if random.random() < prof["agree_rate"]:
        return {
            "action":             "operator_accepted",
            "operator_decision":  gs["ai_decision"],
            "duration_s":         jitter(prof["duration_s"]),
            "correct":            gs["ai_correct"],
        }
    else:
        flipped = "insecure" if gs["ai_decision"] == "secure" else "secure"
        return {
            "action":             "operator_overridden",
            "operator_decision":  flipped,
            "duration_s":         jitter(prof["duration_s"]),
            "correct":            random.random() < prof["override_correct_rate"],
        }


def build_session(session_id, policy, operator_id, gs_offset, start):
    cycles = []
    t = start
    n = CONFIG["n_cycles_per_session"]

    for i in range(n):
        gs  = make_grid_state(gs_offset + i)
        iid = f"SE_{gs_offset + i:06d}"
        decisions = []

        # AI classification
        t += timedelta(seconds=jitter(CONFIG["grid_state_arrival_s"], 0.40))
        decisions.append({
            "interaction_id": iid,
            "timestamp":      iso(t),
            "actor_type":     "ai",
            "action":         "security_classified",
            "latency_ms":     round(jitter(CONFIG["ai_latency_ms"], 0.20), 1),
            "correct":        gs["ai_correct"],
            "payload": {
                "grid_state_id":  gs["grid_state_id"],
                "prob_secure":    gs["prob_secure"],
                "ai_decision":    gs["ai_decision"],
                "al_flag":        gs["al_flag"],
                "risk_score":     gs["risk_score"],
                "region":         gs["region"],
                "weather_regime": gs["weather_regime"],
                "xai_top_factor": gs["xai_top_factor"],
            },
        })

        deferred = is_deferred(gs, policy)

        # OperatorAgent summary (Agent-Mediated only, deferred cases)
        if policy == "agent_mediated" and deferred:
            t += timedelta(seconds=jitter(3.5, 0.30))
            decisions.append({
                "interaction_id": iid,
                "timestamp":      iso(t),
                "actor_type":     "ai",
                "action":         "agent_response",
                "latency_ms":     round(jitter(CONFIG["agent_latency_ms"], 0.25), 1),
                "payload": {
                    "grid_state_id":     gs["grid_state_id"],
                    "query_type":        "security_assessment_review",
                    "ai_recommendation": gs["ai_decision"],
                    "xai_summary":       gs["xai_top_factor"],
                    "tools_called":      ["get_xai_explanation", "get_simulation_result"],
                    "model_version":     CONFIG["agent_model_version"],
                },
            })

        # Human review (all policies, deferred cases)
        if deferred:
            op = simulate_operator(gs, policy)
            t += timedelta(seconds=op["duration_s"])
            decisions.append({
                "interaction_id": iid,
                "timestamp":      iso(t),
                "actor_type":     "human",
                "action":         op["action"],
                "duration_s":     op["duration_s"],
                "correct":        op["correct"],
                "payload": {
                    "grid_state_id":     gs["grid_state_id"],
                    "ai_decision":       gs["ai_decision"],
                    "operator_decision": op["operator_decision"],
                    "operator_id":       operator_id,
                    "region":            gs["region"],
                    "weather_regime":    gs["weather_regime"],
                },
            })

            # AL label event (AL-Aided + al_flagged)
            if policy == "al_aided" and gs["al_flag"]:
                label_dur = jitter(12.0, 0.40)
                t += timedelta(seconds=label_dur)
                decisions.append({
                    "interaction_id": iid,
                    "timestamp":      iso(t),
                    "actor_type":     "human",
                    "action":         "al_label_selected",
                    "duration_s":     label_dur,
                    "correct":        op["correct"],
                    "payload": {
                        "instance_id":       gs["grid_state_id"],
                        "uncertainty_score": round(1 - abs(gs["prob_secure"] - 0.5) * 2, 3),
                        "operator_label":    op["operator_decision"],
                        "operator_id":       operator_id,
                    },
                })

        # Cycle wrapper with meta.task_parameters for platform config
        cycles.append({
            "sim_id":           CONFIG["sim_id"],
            "session_id":       session_id,
            "pilot_tag":        CONFIG["pilot_tag"],
            "app_version":      CONFIG["app_version"],
            "ai_model_version": CONFIG["ai_model_version"],
            "policy":           policy,
            # meta.task_parameters tells the platform how to interpret
            # timing for this domain:
            #   rt_max_s   -> needed for correct HCL normalisation
            #   baseline_s -> needed for Effort Loss (EL) computation
            "meta": {
                "task_parameters": CONFIG["task_parameters"],
                "operator_id":     operator_id,
                "forecast_model":  CONFIG["forecast_model"],
            },
            "decisions":          decisions,
            "session_started_at": decisions[0]["timestamp"],
            "session_ended_at":   decisions[-1]["timestamp"],
        })

    return cycles


def build_dataset():
    """
    Round-robins operators across sessions so each operator appears
    in multiple policies, enabling the Fairness cross-slice.
    Grid state indices are globally offset to avoid overlap.
    """
    dataset    = []
    start      = parse_start()
    op_ids     = CONFIG["operator_ids"]
    n_sessions = CONFIG["sessions_per_policy"]
    n_cycles   = CONFIG["n_cycles_per_session"]
    session_n  = 0

    for policy in CONFIG["policies"]:
        for s in range(n_sessions):
            operator_id = op_ids[session_n % len(op_ids)]
            date_str    = (start + timedelta(days=session_n)).strftime("%Y-%m-%d")
            session_id  = f"se_{policy}_{date_str}"
            gs_offset   = session_n * n_cycles

            cycles = build_session(
                session_id  = session_id,
                policy      = policy,
                operator_id = operator_id,
                gs_offset   = gs_offset,
                start       = start + timedelta(days=session_n),
            )
            dataset.extend(cycles)
            session_n += 1

    return dataset


def print_summary(dataset):
    seen = {}
    for c in dataset:
        sid = c["session_id"]
        if sid not in seen:
            seen[sid] = {
                "policy": c["policy"], "op": c["meta"]["operator_id"],
                "cycles": 0, "deferred": 0, "overrides": 0,
                "al_labels": 0, "ai_correct": 0,
            }
        seen[sid]["cycles"] += 1
        if any(d["actor_type"] == "human" for d in c["decisions"]):
            seen[sid]["deferred"] += 1
        for d in c["decisions"]:
            if d.get("action") == "operator_overridden":
                seen[sid]["overrides"] += 1
            if d.get("action") == "al_label_selected":
                seen[sid]["al_labels"] += 1
        if c["decisions"][0].get("correct"):
            seen[sid]["ai_correct"] += 1

    total = sum(s["cycles"] for s in seen.values())
    print(f"\nGenerated {total} cycles across {len(seen)} sessions\n")
    print(f"  {'session':<44} {'policy':<18} {'op':<7} "
          f"{'cycles':>6} {'defer%':>7} {'overrides':>10} "
          f"{'al_labels':>10} {'ai_acc':>8}")
    print("  " + "-" * 115)
    for sid, s in seen.items():
        n = s["cycles"]
        print(f"  {sid:<44} {s['policy']:<18} {s['op']:<7} "
              f"{n:>6} {100*s['deferred']//n:>6}% "
              f"{s['overrides']:>10} {s['al_labels']:>10} "
              f"{s['ai_correct']:>6}/{n}")
    print()
    print(f"  rt_max_s  = {CONFIG['task_parameters']['rt_max_s']}s  "
          f"(HCL normalisation)")
    print(f"  baseline_s = {CONFIG['task_parameters']['baseline_s']}s  "
          f"(EL computation)")
    print()


dataset = build_dataset()
print_summary(dataset)

with open(CONFIG["output_path"], "w") as f:
    json.dump(dataset, f, indent=2)

print(f"Written to {CONFIG['output_path']}")
