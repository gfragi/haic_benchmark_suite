"""
fit_markov.py

Domain-agnostic first-order Markov model fitter - replaces fit_markov_sc.py.
Fits an AI-decision -> human-decision transition model and per-action
response-time statistics from any HAIC-format log file, producing a
haic.markov_model.v1 model file consumable by surrogate.markov.MarkovSurrogate.

All domain-specific knowledge (which field holds the AI/human decision
value, what those raw strings mean, which decisions count as "correct")
is supplied via arguments rather than hardcoded.

Input shape: either {"logs": [...]} (each session has a "decisions" list,
as in haic_sim_mvp/examples/events_all_v0_patched.json) or a flat JSON
array of decision-event dicts. Detected automatically.

Matching logic: for each interaction_id, the AI event is the one with
actor_type == ai_actor_value whose value at ai_action_field is non-null;
the human event is the one with actor_type == human_actor_value whose
value at human_action_field is non-null. interaction_ids missing either,
or whose raw values aren't present in the supplied action maps, are
skipped.

Usage:
    python scripts/fit_markov.py \\
        --input haic_sim_mvp/examples/events_all_v0_patched.json \\
        --domain smart_city \\
        --ai-action-field "payload.ai_decision" \\
        --human-action-field "payload.op_decision" \\
        --ai-actor-value "ai" \\
        --human-actor-value "human" \\
        --ai-action-map '{"Accepted":"ai_accept","Rejected":"ai_reject","Flagged for verification":"ai_flag"}' \\
        --op-action-map '{"Accepted":"op_accept","Rejected":"op_reject","Accepted after verification":"op_accept_verified","Rejected after verification":"op_reject_verified","Fixed & accepted":"op_fix_accept"}' \\
        --accept-actions '["op_accept","op_accept_verified","op_fix_accept"]' \\
        --group-by "payload.op_id" \\
        --output data/sc_markov_model_v2.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

MODEL_SCHEMA = "haic.markov_model.v1"
PERCENTILES = (5, 25, 50, 75, 95)


def _get_path(d: Any, path: str) -> Any:
    """Dot-notation nested lookup - d['a']['b'] via 'a.b'. Returns None if
    any segment is missing or the value along the way isn't a dict."""
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _flatten_events(data: Any) -> list[dict]:
    """Accepts either {"logs": [...]} (session-wrapped) or a flat list of
    decision-event dicts. Returns one flat list of event dicts either way."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "logs" in data:
        events: list[dict] = []
        for session in data.get("logs", []):
            events.extend(session.get("decisions") or [])
        return events
    raise ValueError(
        "Unrecognized input shape: expected a flat list of decision events, "
        "or a dict with a top-level 'logs' key."
    )


def extract_records(
    events: list[dict],
    *,
    ai_action_field: str,
    human_action_field: str,
    ai_actor_value: str,
    human_actor_value: str,
    ai_action_map: dict[str, str],
    op_action_map: dict[str, str],
    accept_actions: set[str],
    correct_field: str = "correct",
    duration_field: str = "duration_s",
    group_by: str | None = None,
) -> list[dict[str, Any]]:
    """
    Per interaction_id, pair one AI event with one human event (see module
    docstring for the matching rule) and extract (ai_action, op_action,
    correct, duration_s, group_id).

    correct is read from correct_field on the human event when present;
    otherwise it's derived as (op_action in accept_actions), so logs that
    don't carry an explicit correctness label can still be fit.
    """
    by_interaction: dict[Any, list[dict]] = defaultdict(list)
    for e in events:
        iid = e.get("interaction_id")
        if iid is not None:
            by_interaction[iid].append(e)

    records = []
    for evs in by_interaction.values():
        ai_event = next(
            (e for e in evs if e.get("actor_type") == ai_actor_value
             and _get_path(e, ai_action_field) is not None),
            None,
        )
        human_event = next(
            (e for e in evs if e.get("actor_type") == human_actor_value
             and _get_path(e, human_action_field) is not None),
            None,
        )
        if ai_event is None or human_event is None:
            continue

        ai_action = ai_action_map.get(_get_path(ai_event, ai_action_field))
        op_action = op_action_map.get(_get_path(human_event, human_action_field))
        if ai_action is None or op_action is None:
            continue

        correct = _get_path(human_event, correct_field)
        if correct is None:
            correct = op_action in accept_actions

        records.append({
            "ai_action": ai_action,
            "op_action": op_action,
            "correct": bool(correct),
            "duration_s": _get_path(human_event, duration_field),
            "group_id": _get_path(human_event, group_by) if group_by else None,
        })
    return records


def compute_transition_matrix(records: list[dict], ai_vocab: list[str], op_vocab: list[str]) -> dict[str, dict[str, float] | None]:
    """P[ai_action][op_action] = count(ai_action -> op_action) / count(ai_action).
    An ai_action with zero occurrences gets None instead of a fabricated row."""
    by_ai: dict[str, Counter] = defaultdict(Counter)
    for r in records:
        by_ai[r["ai_action"]][r["op_action"]] += 1

    matrix: dict[str, dict[str, float] | None] = {}
    for ai_action in ai_vocab:
        counts = by_ai.get(ai_action)
        total = sum(counts.values()) if counts else 0
        if total == 0:
            matrix[ai_action] = None
            continue
        matrix[ai_action] = {op: counts.get(op, 0) / total for op in op_vocab}
    return matrix


def compute_duration_stats(records: list[dict], ai_vocab: list[str]) -> dict[str, dict[str, float] | None]:
    """Per ai_action duration_s statistics (mean, std, p5/p25/p50/p75/p95)."""
    by_ai: dict[str, list[float]] = defaultdict(list)
    for r in records:
        if r["duration_s"] is not None:
            by_ai[r["ai_action"]].append(float(r["duration_s"]))

    stats: dict[str, dict[str, float] | None] = {}
    for ai_action in ai_vocab:
        durs = by_ai.get(ai_action)
        if not durs:
            stats[ai_action] = None
            continue
        arr = np.array(durs, dtype=float)
        entry = {"mean": float(arr.mean()), "std": float(arr.std())}
        for p in PERCENTILES:
            entry[f"p{p}"] = float(np.percentile(arr, p))
        stats[ai_action] = entry
    return stats


def compute_ai_action_frequency(records: list[dict], ai_vocab: list[str]) -> dict[str, float]:
    """Empirical frequency of each AI action among the fitted records."""
    counts = Counter(r["ai_action"] for r in records)
    total = len(records)
    freq = {ai: 0.0 for ai in ai_vocab}
    if total:
        for ai_action, c in counts.items():
            freq[ai_action] = c / total
    return freq


def fit_group(records: list[dict], ai_vocab: list[str], op_vocab: list[str]) -> dict[str, Any]:
    """Bundle the transition matrix + duration stats for one group of records."""
    return {
        "n": len(records),
        "ai_action_frequency": compute_ai_action_frequency(records, ai_vocab),
        "transition_matrix": compute_transition_matrix(records, ai_vocab, op_vocab),
        "duration_stats": compute_duration_stats(records, ai_vocab),
    }


def accept_rate(records: list[dict]) -> float | None:
    """Fraction of records where correct is True - a Tr (trust) proxy."""
    labeled = [r["correct"] for r in records if r["correct"] is not None]
    if not labeled:
        return None
    return sum(1 for c in labeled if c) / len(labeled)


def fit_model(config: dict[str, Any]) -> dict[str, Any]:
    """
    Fit a haic.markov_model.v1 model dict from already-parsed input data.
    Called directly by main() and by the backend's POST /ontology/fit-model
    endpoint (no subprocess involved).

    Required config keys: input_data, domain, ai_action_field,
    human_action_field, ai_actor_value, human_actor_value, ai_action_map,
    op_action_map, accept_actions.
    Optional: correct_field ("correct"), duration_field ("duration_s"),
    group_by (None).
    """
    ai_action_map: dict[str, str] = config["ai_action_map"]
    op_action_map: dict[str, str] = config["op_action_map"]
    accept_actions: list[str] = list(config["accept_actions"])
    group_by: str | None = config.get("group_by")

    events = _flatten_events(config["input_data"])
    records = extract_records(
        events,
        ai_action_field=config["ai_action_field"],
        human_action_field=config["human_action_field"],
        ai_actor_value=config["ai_actor_value"],
        human_actor_value=config["human_actor_value"],
        ai_action_map=ai_action_map,
        op_action_map=op_action_map,
        accept_actions=set(accept_actions),
        correct_field=config.get("correct_field", "correct"),
        duration_field=config.get("duration_field", "duration_s"),
        group_by=group_by,
    )

    ai_vocab = sorted(set(ai_action_map.values()))
    op_vocab = sorted(set(op_action_map.values()))

    aggregate = fit_group(records, ai_vocab, op_vocab)

    by_group: dict[str, list[dict]] = defaultdict(list)
    if group_by:
        for r in records:
            if r["group_id"] is not None:
                by_group[str(r["group_id"])].append(r)
    by_operator = {
        group_id: fit_group(group_records, ai_vocab, op_vocab)
        for group_id, group_records in by_group.items()
    }

    return {
        "schema": MODEL_SCHEMA,
        "domain": config["domain"],
        "ai_actions": ai_vocab,
        "op_actions": op_vocab,
        "accept_actions": accept_actions,
        "ai_action_frequency": aggregate["ai_action_frequency"],
        "ai_action_original_strings": {v: k for k, v in ai_action_map.items()},
        "op_action_original_strings": {v: k for k, v in op_action_map.items()},
        "aggregate": aggregate,
        "by_operator": by_operator,
        "meta": {
            "source": config.get("source_label"),
            "n_events": len(events),
            "n_valid": len(records),
            "aggregate_accept_rate": accept_rate(records),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, help="Path to log JSON file")
    parser.add_argument("--domain", required=True, help="Domain name string (stored in output)")
    parser.add_argument("--ai-action-field", required=True,
                         help="Dot-notation field path to the raw AI decision value within an AI event, e.g. 'payload.ai_decision'")
    parser.add_argument("--human-action-field", required=True,
                         help="Dot-notation field path to the raw human decision value within a human event, e.g. 'payload.op_decision'")
    parser.add_argument("--ai-actor-value", default="ai", help="actor_type value that identifies AI events (default: ai)")
    parser.add_argument("--human-actor-value", default="human", help="actor_type value that identifies human events (default: human)")
    parser.add_argument("--correct-field", default="correct",
                         help="Field that holds True/False on the human event (default: correct)")
    parser.add_argument("--duration-field", default="duration_s",
                         help="Field for response time on the human event (default: duration_s)")
    parser.add_argument("--group-by", default=None,
                         help="Dot-notation field path for operator grouping, e.g. 'payload.op_id'. Optional - omit for no by_operator matrix")
    parser.add_argument("--ai-action-map", required=True,
                         help="JSON object: raw AI decision value -> canonical ai_action id")
    parser.add_argument("--op-action-map", required=True,
                         help="JSON object: raw human decision value -> canonical op_action id")
    parser.add_argument("--accept-actions", required=True,
                         help="JSON array of canonical op_action ids that mean correct=True")
    parser.add_argument("--output", required=True, help="Output path for the model JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    data = json.loads(input_path.read_text(encoding="utf-8"))

    config = {
        "input_data": data,
        "source_label": str(input_path),
        "domain": args.domain,
        "ai_action_field": args.ai_action_field,
        "human_action_field": args.human_action_field,
        "ai_actor_value": args.ai_actor_value,
        "human_actor_value": args.human_actor_value,
        "correct_field": args.correct_field,
        "duration_field": args.duration_field,
        "group_by": args.group_by,
        "ai_action_map": json.loads(args.ai_action_map),
        "op_action_map": json.loads(args.op_action_map),
        "accept_actions": json.loads(args.accept_actions),
    }

    model = fit_model(config)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Domain:                    {model['domain']}")
    print(f"Events scanned:            {model['meta']['n_events']}")
    print(f"Valid interaction pairs:   {model['meta']['n_valid']}")
    print(f"Aggregate accept rate:     {model['meta']['aggregate_accept_rate']}")
    print(f"Model saved to:            {output_path}")


if __name__ == "__main__":
    main()
