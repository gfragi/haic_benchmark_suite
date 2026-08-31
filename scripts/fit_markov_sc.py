"""
fit_markov_sc.py

Fits a first-order Markov transition model (AI decision -> operator
decision) and per-action response-time statistics from real Smart City
(Novoville permit-review) pilot logs, for use by a future probabilistic
surrogate agent.

Input shape (see extras.notes in the file itself): {"logs": [...], "extras":
{"derive_correct_rules": [...]}}. Each session in "logs" has a "decisions"
list; a permit application always has an "application_created" (citizen,
ignored here) and "ai_evaluated" (AI decision) event, but only reaches an
"operator_verified" event if the AI didn't auto-accept it - in this dataset
every "Accepted" AI decision skips operator review entirely (402/402), so
there is no real operator-response data for that AI action. That asymmetry
is preserved in the output (see NOTE below) rather than papered over with a
fabricated row.

Usage:
    python scripts/fit_markov_sc.py
    python scripts/fit_markov_sc.py --input path/to/events.json --output path/to/model.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

DEFAULT_INPUT = "haic_sim_mvp/examples/events_all_v0_patched.json"
DEFAULT_OUTPUT = "data/sc_markov_model.json"

# Canonical vocab. Op-decision values are taken verbatim from the real data
# ("Fixed & accepted", not "Fixed and accepted") - a spec describing this
# task used the latter, which would silently fail to match anything.
AI_CANON = {
    "Accepted": "ai_accept",
    "Rejected": "ai_reject",
    "Flagged for verification": "ai_flag",
}
OP_CANON = {
    "Accepted": "op_accept",
    "Rejected": "op_reject",
    "Accepted after verification": "op_accept_verified",
    "Rejected after verification": "op_reject_verified",
    "Fixed & accepted": "op_fix_accept",
}
AI_VOCAB = ["ai_accept", "ai_reject", "ai_flag"]
OP_VOCAB = ["op_accept", "op_reject", "op_accept_verified", "op_reject_verified", "op_fix_accept"]

PERCENTILES = (5, 25, 50, 75, 95)


def load_logs(path: Path) -> tuple[list[dict], dict]:
    """Load the {"logs": [...], "extras": {...}} file and return both parts."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("logs", []), data.get("extras", {})


def extract_records(logs: list[dict]) -> list[dict[str, Any]]:
    """
    Per application, pull (ai_action, op_action, correct, duration_s, op_id)
    from the ai_evaluated + operator_verified event pair. Sessions whose
    application was auto-decided (no operator_verified event at all) are
    skipped, since there is no operator response to fit against.
    """
    records = []
    for session in logs:
        decisions = session.get("decisions") or []
        ai_event = next((d for d in decisions if d.get("action") == "ai_evaluated"), None)
        op_event = next((d for d in decisions if d.get("action") == "operator_verified"), None)
        if ai_event is None or op_event is None:
            continue

        ai_raw = (ai_event.get("payload") or {}).get("ai_decision")
        op_raw = (op_event.get("payload") or {}).get("op_decision")
        ai_action = AI_CANON.get(ai_raw)
        op_action = OP_CANON.get(op_raw)
        if ai_action is None or op_action is None:
            continue

        records.append({
            "ai_action": ai_action,
            "op_action": op_action,
            "correct": op_event.get("correct"),
            "duration_s": op_event.get("duration_s"),
            "op_id": (op_event.get("payload") or {}).get("op_id"),
        })
    return records


def compute_transition_matrix(records: list[dict]) -> dict[str, dict[str, float] | None]:
    """
    P[ai_action][op_action] = count(ai_action -> op_action) / count(ai_action),
    over the given records. An ai_action with zero occurrences (e.g.
    "ai_accept" in this dataset, which never reaches an operator) gets None
    instead of a fabricated/uniform row.
    """
    by_ai: dict[str, Counter] = defaultdict(Counter)
    for r in records:
        by_ai[r["ai_action"]][r["op_action"]] += 1

    matrix: dict[str, dict[str, float] | None] = {}
    for ai_action in AI_VOCAB:
        counts = by_ai.get(ai_action)
        total = sum(counts.values()) if counts else 0
        if total == 0:
            matrix[ai_action] = None
            continue
        matrix[ai_action] = {op: counts.get(op, 0) / total for op in OP_VOCAB}
    return matrix


def compute_duration_stats(records: list[dict]) -> dict[str, dict[str, float] | None]:
    """Per ai_action duration_s statistics (mean, std, p5/p25/p50/p75/p95)."""
    by_ai: dict[str, list[float]] = defaultdict(list)
    for r in records:
        if r["duration_s"] is not None:
            by_ai[r["ai_action"]].append(float(r["duration_s"]))

    stats: dict[str, dict[str, float] | None] = {}
    for ai_action in AI_VOCAB:
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


def fit(records: list[dict]) -> dict[str, Any]:
    """Bundle the transition matrix + duration stats for one group of records."""
    return {
        "n": len(records),
        "transition_matrix": compute_transition_matrix(records),
        "duration_stats": compute_duration_stats(records),
    }


def accept_rate(records: list[dict]) -> float | None:
    """Fraction of records where correct is True - a Tr (trust) proxy."""
    labeled = [r["correct"] for r in records if r["correct"] is not None]
    if not labeled:
        return None
    return sum(1 for c in labeled if c) / len(labeled)


def print_summary(n_sessions: int, records: list[dict], aggregate: dict, by_operator: dict[str, dict]) -> None:
    """Human-readable console summary of the fit."""
    print(f"Total sessions parsed:     {n_sessions}")
    print(f"Valid sessions (used):     {len(records)}  (reached operator review)")
    skipped = n_sessions - len(records)
    print(f"Skipped (auto-decided):    {skipped}")
    print()

    print("Aggregate transition matrix  P(op_action | ai_action)")
    header = f"{'ai_action':<12}" + "".join(f"{op:>22}" for op in OP_VOCAB)
    print(header)
    for ai_action in AI_VOCAB:
        row = aggregate["transition_matrix"][ai_action]
        if row is None:
            print(f"{ai_action:<12}" + "  (no operator data - always auto-decided)")
            continue
        print(f"{ai_action:<12}" + "".join(f"{row[op]:>22.1%}" for op in OP_VOCAB))
    print()

    print("Per-operator accept rate (Tr proxy), descending:")
    rates = []
    for op_id, group in by_operator.items():
        recs = group["_records"]
        rate = accept_rate(recs)
        rates.append((op_id, rate, len(recs)))
    rates.sort(key=lambda x: (x[1] is None, -(x[1] or 0)))
    for op_id, rate, n in rates:
        rate_str = f"{rate:.1%}" if rate is not None else "n/a"
        print(f"  operator {op_id}: {rate_str:>7}  (n={n})")
    print()

    print("Duration stats (mean ± std seconds) per AI action:")
    for ai_action in AI_VOCAB:
        d = aggregate["duration_stats"][ai_action]
        if d is None:
            print(f"  {ai_action:<12}: no data")
            continue
        print(f"  {ai_action:<12}: {d['mean']:.1f}s ± {d['std']:.1f}s  (median {d['p50']:.1f}s)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to the raw pilot log JSON")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Path to write the fitted model JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    logs, extras = load_logs(input_path)
    records = extract_records(logs)

    aggregate = fit(records)

    by_operator: dict[str, dict] = {}
    by_op_id: dict[Any, list[dict]] = defaultdict(list)
    for r in records:
        by_op_id[r["op_id"]].append(r)
    for op_id in sorted(by_op_id, key=lambda x: (x is None, x)):
        group_records = by_op_id[op_id]
        entry = fit(group_records)
        entry["_records"] = group_records  # used for the printed summary only, not saved
        by_operator[str(op_id)] = entry

    print_summary(len(logs), records, aggregate, by_operator)

    # Strip the summary-only _records field before saving.
    by_operator_out = {
        op_id: {k: v for k, v in entry.items() if k != "_records"}
        for op_id, entry in by_operator.items()
    }

    model = {
        "meta": {
            "source": str(input_path),
            "n_sessions": len(logs),
            "n_valid": len(records),
            "action_vocab": {"ai": AI_VOCAB, "op": OP_VOCAB},
            "derive_correct_rules": extras.get("derive_correct_rules", []),
            "note": (
                "ai_accept never reaches operator review in this dataset "
                f"({sum(1 for s in logs for d in s.get('decisions', []) if d.get('action') == 'ai_evaluated' and (d.get('payload') or {}).get('ai_decision') == 'Accepted')} "
                "of its occurrences were auto-decided) - its transition_matrix "
                "and duration_stats entries are null rather than fabricated."
            ),
        },
        "aggregate": aggregate,
        "by_operator": by_operator_out,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(model, indent=2), encoding="utf-8")
    print()
    print(f"Model saved to: {output_path}")


if __name__ == "__main__":
    main()
