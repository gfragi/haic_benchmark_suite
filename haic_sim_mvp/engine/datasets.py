
import csv, random
from typing import Dict, List, Any, Iterable

def load_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f: return list(csv.DictReader(f))

def make_script_from_dataset(rows: Iterable[Dict[str, Any]], ai_agent_id: str, human_agent_id: str,
                             object_id_prefix="O", positive_label="positive", ai_policy=None, human_accuracy=0.9):
    script, t = [], 0
    for i, row in enumerate(rows, 1):
        t += 1
        obj_id = f"{object_id_prefix}{i}"
        gt = row.get("ground_truth", positive_label)
        res = ai_policy.predict(row) if ai_policy else None
        if res and not res.defer:
            pred = res.label
            correct = str(pred) == str(gt)
            script.append({"t": t, "agent": ai_agent_id, "action": "classify", "object": obj_id,
                           "effect": {"ai_label": pred, "ai_conf": getattr(res, "confidence", 1.0)},
                           "correct": correct, "latency_ms": 200})
        else:
            t += 1
            pred_h = gt if random.random() <= human_accuracy else (positive_label if gt != positive_label else f"not_{positive_label}")
            correct_h = str(pred_h) == str(gt)
            script.append({"t": t, "agent": human_agent_id, "action": "classify", "object": obj_id,
                           "effect": {"human_label": pred_h, "deferred": True},
                           "correct": correct_h, "latency_ms": 800})
    return script
