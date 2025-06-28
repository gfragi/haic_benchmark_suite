from fastapi import APIRouter, HTTPException
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
