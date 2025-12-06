"""
Dataset handling for HAIC simulations.
Based on haic_sim_mvp engine/datasets.py
"""
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path


def load_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Load CSV file into list of dicts."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            processed_row = {}
            for k, v in row.items():
                if k is None:
                    continue
                k = str(k).strip()
                v = str(v).strip() if v is not None else ""

                # Try to convert to float if it looks numeric
                try:
                    if '.' in v or 'e' in v.lower():
                        processed_row[k] = float(v)
                    else:
                        processed_row[k] = int(v)
                except ValueError:
                    processed_row[k] = v

            rows.append(processed_row)

    return rows


def make_script_from_dataset(
    rows: List[Dict[str, Any]],
    ai_agent_id: str,
    human_agent_id: str,
    ai_policy: Any,  # Should have predict() method
    positive_label: str = "positive",
    human_accuracy: float = 0.9,
    ai_latency_ms: Optional[float] = None,
    human_latency_ms: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Generate script from dataset rows using a policy.
    Based on haic_sim_mvp engine/datasets.py
    """
    script = []
    t = 1

    for i, row in enumerate(rows):
        obj_id = f"O{i+1}"
        ai_result = ai_policy.predict(row)

        if ai_result.defer:
            # AI defers to human
            script.extend([
                {
                    "t": t,
                    "agent": ai_agent_id,
                    "action": "classify",
                    "object": obj_id,
                    "effect": {"ai_label": "defer", "prob": ai_result.confidence},
                    "latency_ms": ai_latency_ms or 220,
                }
            ])
            t += 1

            # Human classifies
            ground_truth = str(row.get("ground_truth", "")).strip()
            human_correct = (ground_truth == positive_label)

            script.append({
                "t": t,
                "agent": human_agent_id,
                "action": "classify",
                "object": obj_id,
                "effect": {"human_label": ground_truth},
                "correct": human_correct,
                "latency_ms": human_latency_ms or 950,
            })
            t += 1

        else:
            # AI classifies directly
            ai_label = ai_result.label
            ground_truth = str(row.get("ground_truth", "")).strip()
            correct = (ai_label == ground_truth)

            script.append({
                "t": t,
                "agent": ai_agent_id,
                "action": "classify",
                "object": obj_id,
                "effect": {"ai_label": ai_label, "prob": ai_result.confidence},
                "correct": correct,
                "latency_ms": ai_latency_ms or 220,
            })
            t += 1

    return script
