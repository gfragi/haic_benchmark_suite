import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models.experiments import ExperimentModel
from app.schemas.experiments import (
    CompareRequest,
    ExperimentCreateResponse,
    ExperimentDeleteResponse,
    ExperimentDetail,
    ExperimentModelIn,
    ExperimentModelOut,
    ExperimentRunIn,
    ExperimentSummary,
    ExtractRequest,
    PredictRequest,
    RevealRequest,
)
from app.services import experiment_service
from app.utils.database import get_db
from app.utils.errors import http_error

router = APIRouter()

# ---------- engine wiring: packages/experiment_engine isn't a backend
# package (deliberately no app.* imports there, see its module docstring),
# so it's made importable the same way packages/surrogate and scripts/ are
# elsewhere in this codebase (sys.path insert, not a real install).
def _find_project_root() -> Path:
    here = Path(__file__).resolve()
    for cand in here.parents:
        if (cand / "haic_env_builder").is_dir() and (cand / "packages").is_dir():
            return cand
    return here.parents[3] if len(here.parents) >= 4 else here.parents[-1]


PROJECT_ROOT = _find_project_root()
_ENGINE_PATH = str(PROJECT_ROOT / "packages" / "experiment_engine")
if _ENGINE_PATH not in sys.path:
    sys.path.insert(0, _ENGINE_PATH)

from engine import HAICExperimentEngine  # noqa: E402

UPLOAD_DIR = PROJECT_ROOT / "data" / "experiment_uploads"


@router.post("", response_model=ExperimentCreateResponse, status_code=201, summary="Create an experiment run")
def create_experiment(payload: ExperimentRunIn, db: Session = Depends(get_db)):
    row = experiment_service.create_experiment(db, payload)
    return ExperimentCreateResponse(experiment_id=row.id, status=row.status)


@router.post("/{experiment_id}/models", response_model=ExperimentModelOut, status_code=201, summary="Register a model in an experiment")
async def register_model(experiment_id: UUID, request: Request, db: Session = Depends(get_db)):
    """
    Accepts either multipart/form-data (with an optional log_file upload)
    or a plain JSON body with log_file_path. FastAPI ties a route to one
    body-parsing style, so the two are dispatched manually here based on
    Content-Type - there's no existing precedent in this codebase for an
    endpoint that genuinely needs to accept both.
    """
    content_type = request.headers.get("content-type", "")
    log_file_path: Optional[str] = None

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        model_id = form.get("model_id")
        model_label = form.get("model_label") or None
        role = form.get("role")
        fitted_model_path = form.get("fitted_model_path") or None
        log_file_path = form.get("log_file_path") or None

        upload = form.get("log_file")
        if upload is not None and hasattr(upload, "read"):
            raw = await upload.read()
            if raw:
                UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
                safe_name = Path(upload.filename or "log.json").name
                saved_path = UPLOAD_DIR / f"{experiment_id}_{model_id}_{safe_name}"
                saved_path.write_bytes(raw)
                log_file_path = str(saved_path.relative_to(PROJECT_ROOT))

        payload = ExperimentModelIn(
            model_id=model_id, model_label=model_label, role=role,
            log_file_path=log_file_path, fitted_model_path=fitted_model_path,
        )
    else:
        body = await request.json()
        payload = ExperimentModelIn(**body)

    return experiment_service.register_model(db, experiment_id, payload)


@router.get("", response_model=List[ExperimentSummary], summary="List all experiments")
def list_experiments(db: Session = Depends(get_db)):
    pairs = experiment_service.list_experiments(db)
    out = []
    for row, count in pairs:
        row.model_count = count  # not a mapped column - attached for response_model conversion
        out.append(row)
    return out


@router.get("/{experiment_id}", response_model=ExperimentDetail, summary="Get full experiment detail (models + results)")
def get_experiment(experiment_id: UUID, db: Session = Depends(get_db)):
    return experiment_service.get_experiment(db, experiment_id)


@router.delete("/{experiment_id}", response_model=ExperimentDeleteResponse, summary="Soft-delete (cancel) an experiment")
def delete_experiment(experiment_id: UUID, db: Session = Depends(get_db)):
    experiment_service.cancel_experiment(db, experiment_id)
    return ExperimentDeleteResponse(message="Experiment cancelled", experiment_id=experiment_id)


# ---------- run phases ----------

@router.post("/{experiment_id}/run/extract", summary="Phase 0: extract a model's AI action frequency (operator data untouched)")
def run_extract(experiment_id: UUID, payload: ExtractRequest, db: Session = Depends(get_db)):
    model = experiment_service.get_model_row(db, experiment_id, payload.model_id)
    if not model.log_file_path:
        http_error(400, "NO_LOG_FILE", f"Model '{payload.model_id}' has no log_file_path registered")

    engine = HAICExperimentEngine(db)
    try:
        engine.phase_0_extract_ai_freq(experiment_id, payload.model_id, model.log_file_path)
    except (ValueError, FileNotFoundError) as e:
        http_error(400, "EXTRACT_FAILED", str(e))

    db.refresh(model)
    return {"model_id": model.model_id, "ai_action_frequency": model.ai_action_frequency, "status": model.status}


@router.post("/{experiment_id}/run/predict", summary="Phase 1: blind prediction for one target (or all targets if omitted)")
def run_predict(experiment_id: UUID, payload: PredictRequest, db: Session = Depends(get_db)):
    engine = HAICExperimentEngine(db)

    targets = (
        [experiment_service.get_model_row(db, experiment_id, payload.target_model_id)]
        if payload.target_model_id
        else experiment_service.get_target_models(db, experiment_id)
    )
    if not targets:
        http_error(400, "NO_TARGET_MODELS", "No target models registered in this experiment")

    # Explicit target: a re-predict attempt is a hard error (predictions are
    # sealed the moment phase_1 first runs). Bulk mode (target omitted)
    # skips already-sealed targets instead of failing the whole call, so a
    # partially-predicted experiment can still be completed with one call.
    if payload.target_model_id and targets[0].status in ("predicted", "revealed"):
        http_error(409, "PREDICTIONS_ALREADY_SEALED", f"Predictions for '{payload.target_model_id}' are already sealed")

    results = {}
    skipped = []
    for target in targets:
        if target.status in ("predicted", "revealed"):
            skipped.append(target.model_id)
            continue
        try:
            preds = engine.phase_1_blind_predict(experiment_id, target.model_id)
        except ValueError as e:
            http_error(400, "PREDICT_FAILED", str(e))
        results[target.model_id] = {
            "predictions_sealed_at": preds["sealed_at"],
            "predictions": {
                "Tr": {"mean": preds["pred_Tr"], "std": preds["pred_Tr_std"]},
                "HCL": {"mean": preds["pred_HCL"], "std": preds["pred_HCL_std"]},
                "EL": {"mean": preds["pred_EL"], "std": preds["pred_EL_std"]},
                "F": {"mean": preds["pred_F"], "std": preds["pred_F_std"]},
            },
        }

    if payload.target_model_id:
        # The upfront check above already 409s an already-sealed explicit
        # target, so reaching here means phase_1 just ran successfully.
        return results[payload.target_model_id]

    return {"results": results, "skipped": skipped}


@router.post("/{experiment_id}/run/reveal", summary="Phase 2: fit the real matrix for one target (or all targets if omitted)")
def run_reveal(experiment_id: UUID, payload: RevealRequest, db: Session = Depends(get_db)):
    experiment = experiment_service.get_experiment(db, experiment_id)
    if experiment.sealed_at is None:
        http_error(400, "PREDICTIONS_NOT_SEALED", "Predictions must be sealed (run/predict) before revealing real data")

    engine = HAICExperimentEngine(db)
    targets = (
        [experiment_service.get_model_row(db, experiment_id, payload.model_id)]
        if payload.model_id
        else experiment_service.get_target_models(db, experiment_id)
    )

    results = []
    for target in targets:
        if not target.log_file_path:
            http_error(400, "NO_LOG_FILE", f"Model '{target.model_id}' has no log_file_path registered")
        try:
            engine.phase_2_fit_real_matrix(experiment_id, target.model_id, target.log_file_path)
        except ValueError as e:
            http_error(400, "REVEAL_FAILED", str(e))
        db.refresh(target)
        results.append({"model_id": target.model_id, "status": target.status, "fitted_model_path": target.fitted_model_path})

    return results[0] if payload.model_id else {"results": results}


@router.post("/{experiment_id}/run/compare", summary="Phase 3: compare predictions vs reality for one pair (or all source/target pairs if omitted)")
def run_compare(experiment_id: UUID, payload: CompareRequest, db: Session = Depends(get_db)):
    experiment = experiment_service.get_experiment(db, experiment_id)
    engine = HAICExperimentEngine(db)

    if payload.model_a_id and payload.model_b_id:
        pairs = [(payload.model_a_id, payload.model_b_id)]
    else:
        pairs = [(experiment.source_model_id, t.model_id) for t in experiment_service.get_target_models(db, experiment_id)]

    results = []
    for model_a_id, model_b_id in pairs:
        try:
            results.append(engine.phase_3_compare(experiment_id, model_a_id, model_b_id))
        except ValueError as e:
            http_error(400, "COMPARE_FAILED", str(e))

    return results[0] if (payload.model_a_id and payload.model_b_id) else {"results": results}


# ---------- reporting ----------

def _build_results_report(db: Session, experiment_id: UUID) -> dict:
    experiment = experiment_service.get_experiment(db, experiment_id)
    models = experiment_service.get_all_models(db, experiment_id)
    result_rows = experiment_service.get_result_rows(db, experiment_id)

    by_pair: dict = {}
    for r in result_rows:
        by_pair.setdefault((r.model_a_id, r.model_b_id), {})[r.comparison_type] = r

    comparisons = []
    for (model_a, model_b), rows in by_pair.items():
        pvr = rows.get("predicted_vs_real")
        mvm = rows.get("matrix_vs_matrix")
        comparisons.append({
            "model_a": model_a,
            "model_b": model_b,
            "predicted": {
                "Tr": {"mean": pvr.pred_Tr, "std": pvr.pred_Tr_std} if pvr else None,
                "HCL": {"mean": pvr.pred_HCL, "std": pvr.pred_HCL_std} if pvr else None,
                "EL": {"mean": pvr.pred_EL, "std": pvr.pred_EL_std} if pvr else None,
                "F": {"mean": pvr.pred_F, "std": pvr.pred_F_std} if pvr else None,
            },
            "real": {
                "Tr": pvr.real_Tr if pvr else None,
                "HCL": pvr.real_HCL if pvr else None,
                "EL": pvr.real_EL if pvr else None,
                "F": pvr.real_F if pvr else None,
            },
            "errors": {
                "Tr_pct": pvr.err_Tr_pct if pvr else None,
                "HCL_pct": pvr.err_HCL_pct if pvr else None,
                "EL_pct": pvr.err_EL_pct if pvr else None,
                "F_pct": pvr.err_F_pct if pvr else None,
            },
            "S_cross": mvm.S_cross if mvm else (pvr.S_cross if pvr else None),
            "S_cross_per_action": mvm.S_cross_per_action if mvm else (pvr.S_cross_per_action if pvr else None),
            "hypotheses": {
                "H1": pvr.h1_supported if pvr else None,
                "H2": pvr.h2_supported if pvr else None,
                "H3": pvr.h3_supported if pvr else None,
            },
        })

    return {
        "experiment": {
            "id": str(experiment.id), "name": experiment.name, "domain": experiment.domain,
            "status": experiment.status, "model_count": len(models),
        },
        "models": [
            {"model_id": m.model_id, "role": m.role, "status": m.status, "ai_action_frequency": m.ai_action_frequency}
            for m in models
        ],
        "comparisons": comparisons,
    }


@router.get("/{experiment_id}/results", summary="Assembled comparison report")
def get_results(experiment_id: UUID, db: Session = Depends(get_db)):
    return _build_results_report(db, experiment_id)


@router.get("/{experiment_id}/results/export", summary="Same report as a downloadable JSON file")
def export_results(experiment_id: UUID, db: Session = Depends(get_db)):
    report = _build_results_report(db, experiment_id)
    return JSONResponse(
        content=report,
        headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_id}_results.json"},
    )
