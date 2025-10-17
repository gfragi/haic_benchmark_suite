from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import EvaluationResult
from app.services.metrics_adapter import compute_from_log

# Canonical metric names (match what outcome_metrics emits)
PERFORMANCE = ("Prediction Accuracy","Precision","Recall","Overall System Accuracy","Model Improvement Rate")
EFFICIENCY = ("Response Time","Task Completion Time","Error Reduction Rate","Resource Utilization",
              "Teaching Efficiency","Correction Efficiency","Knowledge Retention")
ADAPT_LEARN = ("Feedback Impact","Adaptability Score","Impact of Corrections","Learning Efficiency",
               "Objective Fulfillment Rate")
COLLAB = ("AI Assistance Rate","Human-AI Agreement Rate","Decision Effectiveness","Time to Resolution",
          "Human Effort Saved")
TRUST = ("Trust Score","Confidence","Safety Incidents","System Reliability")
ROBUST = ("Adversarial Robustness","Domain Generalization")

GROUP_MAP: Dict[str, tuple[str, ...]] = {
    "Effectiveness": PERFORMANCE,
    "Efficiency": EFFICIENCY,
    "Adaptability and Learning": ADAPT_LEARN,
    "Collaboration and Interaction": COLLAB,
    "Trust and Safety": TRUST,
    "Robustness and Generalization": ROBUST,
}


def _mean(nums: List[Optional[float]]) -> Optional[float]:
    vals = [x for x in nums if isinstance(x, (int, float))]
    return (sum(vals) / len(vals)) if vals else None


def aggregate_derived(logs: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    """
    Mean aggregation over by_metric across raw logs using the adapter.
    Each log can be a full session dict (your LogSchema).
    """
    derived = [compute_from_log(l) for l in logs]
    keys = set().union(*(d["by_metric"].keys() for d in derived)) if derived else set()
    out: Dict[str, Optional[float]] = {}
    for k in keys:
        out[k] = _mean([d["by_metric"].get(k) for d in derived])
    return out


def calculate_metrics_for_group_from_logs(logs: List[Dict[str, Any]], group_name: str) -> Dict[str, Optional[float]]:
    """
    Compute group metrics from a list of raw log dicts (no DB/LogEntry dependency).
    """
    if not logs:
        return {}

    # Compute derived per session via the adapter
    derived = [compute_from_log(l) for l in logs]
    group_keys = GROUP_MAP.get(group_name, ())
    result: Dict[str, Optional[float]] = {}

    for name in group_keys:
        per_session_vals = []
        for d in derived:
            v = d["by_metric"].get(name)
            if isinstance(v, (int, float)):
                per_session_vals.append(v)
        result[name] = _mean(per_session_vals)

    return result


def save_evaluation_result(db: Session, configuration_id: int, aggregated_metrics: Dict[str, Any]) -> EvaluationResult:
    """
    Persist a minimal subset to EvaluationResult, using canonical keys.
    (Extend fields as your model grows.)
    """
    result = EvaluationResult(
        configuration_id=configuration_id,
        evaluation_date=datetime.now(timezone.utc),

        # Effectiveness
        accuracy=aggregated_metrics.get("Prediction Accuracy") or 0,
        precision=aggregated_metrics.get("Precision") or 0,
        recall=aggregated_metrics.get("Recall") or 0,

        # Collaboration & Interaction
        human_ai_agreement_rate=aggregated_metrics.get("Human-AI Agreement Rate") or 0,
        time_to_resolution=aggregated_metrics.get("Time to Resolution") or 0,
        human_effort_saved=aggregated_metrics.get("Human Effort Saved") or 0,
        ai_assistance_rate=aggregated_metrics.get("AI Assistance Rate") or 0,

        # Adaptability & Learning
        learning_efficiency=aggregated_metrics.get("Learning Efficiency") or 0,

        # Efficiency
        correction_efficiency=aggregated_metrics.get("Correction Efficiency") or 0,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result