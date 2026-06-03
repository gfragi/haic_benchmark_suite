import logging
from typing import Any

logger = logging.getLogger(__name__)

# Binary-positive labels for prediction/label normalization
_POS = {"1", "true", "positive", "yes", "accept", "confirmed", "correct"}


def _to_binary(val: Any) -> int | None:
    if val is None:
        return None
    return 1 if str(val).strip().lower() in _POS else 0


def compute_fairness_for_logs(logs: list) -> dict | None:
    """
    Attempt fairness evaluation across session log data.

    Required per decision event:
      - prediction or ai_decision  (AI output)
      - ground_truth or op_decision (actual/operator outcome)
      - at least one sensitive feature: cohort, role, op_id, or user_group

    Returns None when data is insufficient or fairlearn is unavailable.
    """
    try:
        from sklearn.metrics import accuracy_score
        from fairlearn.metrics import (
            MetricFrame,
            selection_rate,
            demographic_parity_difference,
        )
    except ImportError:
        logger.warning("Fairness evaluation skipped: fairlearn or sklearn not installed")
        return None

    predictions, labels, sensitive = [], [], []

    for session in logs:
        for decision in (session.get("decisions") or []):
            pred_raw = decision.get("prediction") or decision.get("ai_decision")
            label_raw = decision.get("ground_truth") or decision.get("op_decision")
            group_raw = (
                decision.get("cohort")
                or decision.get("role")
                or decision.get("op_id")
                or decision.get("user_group")
            )
            pred = _to_binary(pred_raw)
            label = _to_binary(label_raw)
            if pred is None or label is None or group_raw is None:
                continue
            predictions.append(pred)
            labels.append(label)
            sensitive.append(str(group_raw))

    n_groups = len(set(sensitive))
    if len(predictions) < 2 or n_groups < 2:
        logger.info(
            "Fairness: insufficient data (%d samples, %d groups) — skipping",
            len(predictions), n_groups,
        )
        return None

    try:
        mf = MetricFrame(
            metrics={"accuracy": accuracy_score, "selection_rate": selection_rate},
            y_true=labels,
            y_pred=predictions,
            sensitive_features=sensitive,
        )
        dpd = demographic_parity_difference(
            y_true=labels, y_pred=predictions, sensitive_features=sensitive
        )
        return {
            "n_samples": len(predictions),
            "groups": sorted(set(sensitive)),
            "by_group": mf.by_group.to_dict(),
            "overall": mf.overall.to_dict(),
            "demographic_parity_difference": float(dpd),
        }
    except Exception as e:
        logger.warning("Fairness computation error: %s", repr(e))
        return None
