from fastapi import APIRouter, HTTPException, Request
from sklearn.metrics import accuracy_score
from fairlearn.metrics import MetricFrame, selection_rate, demographic_parity_difference, equalized_odds_difference
from app.schemas.fairness import FairnessInput

router = APIRouter()

@router.post("/evaluate/")
async def evaluate_fairness(data: FairnessInput, feature: str):
    # Check if the chosen sensitive feature exists
    if feature not in data.sensitive_features:
        raise HTTPException(status_code=400, detail=f"Sensitive feature '{feature}' not found.")

    preds = data.predictions
    labels = data.labels
    sensitive = data.sensitive_features[feature]

    if len(preds) != len(labels) or len(preds) != len(sensitive):
        raise HTTPException(status_code=400, detail="Length mismatch in input arrays.")

    # Compute metrics
    mf = MetricFrame(
        metrics={"accuracy": accuracy_score, "selection_rate": selection_rate},
        y_true=labels,
        y_pred=preds,
        sensitive_features=sensitive
    )

    return {
        "by_group": mf.by_group.to_dict(),
        "overall": mf.overall,
        "demographic_parity_difference": demographic_parity_difference(
            y_true=labels,
            y_pred=preds,
            sensitive_features=sensitive
        ),
        "equalized_odds_difference": equalized_odds_difference(
            y_true=labels,
            y_pred=preds,
            sensitive_features=sensitive
        )
    }


@router.post("/evaluate-from-log/")
async def evaluate_fairness_from_log(request: Request):
    """
    Accept log data (same session-array format as /logs/upload) and run
    fairness evaluation using compute_fairness_for_logs(). Returns fairness
    metrics or 422 with a description of which fields are missing.
    """
    from app.services.schema_bridge import normalize_log_payload
    from app.services.fairness_service import compute_fairness_for_logs

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")

    try:
        sessions, _warnings = normalize_log_payload(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    logs = [s.model_dump(mode="json") for s in sessions]
    result = compute_fairness_for_logs(logs)

    if result is None:
        raise HTTPException(
            status_code=422,
            detail=(
                "Fairness could not be computed. Required fields: "
                "prediction or ai_decision on AI events, "
                "ground_truth or op_decision on human review events, "
                "and at least one sensitive feature (cohort, role, op_id, or user_group) "
                "in event payload. Need ≥2 samples across ≥2 groups."
            ),
        )
    return result
