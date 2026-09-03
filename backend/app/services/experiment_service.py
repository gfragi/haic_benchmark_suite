from typing import List, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.experiments import ExperimentModel, ExperimentResult, ExperimentRun
from app.schemas.experiments import ExperimentModelIn, ExperimentRunIn
from app.utils.errors import http_error


def create_experiment(db: Session, payload: ExperimentRunIn) -> ExperimentRun:
    row = ExperimentRun(
        name=payload.name,
        description=payload.description,
        domain=payload.domain,
        source_model_id=payload.source_model_id,
        n_sessions=payload.n_sessions,
        n_items=payload.n_items,
        smooth_epsilon=payload.smooth_epsilon,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_experiment(db: Session, experiment_id: UUID) -> ExperimentRun:
    row = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_id).first()
    if not row:
        http_error(404, "EXPERIMENT_NOT_FOUND", f"Experiment {experiment_id} not found")
    return row


def list_experiments(db: Session) -> List[Tuple[ExperimentRun, int]]:
    rows = db.query(ExperimentRun).order_by(ExperimentRun.created_at.desc()).all()
    counts = dict(
        db.query(ExperimentModel.experiment_id, func.count(ExperimentModel.id))
        .group_by(ExperimentModel.experiment_id)
        .all()
    )
    return [(row, counts.get(row.id, 0)) for row in rows]


def register_model(db: Session, experiment_id: UUID, payload: ExperimentModelIn) -> ExperimentModel:
    experiment = get_experiment(db, experiment_id)
    # domain isn't part of the request body - an experiment_model always
    # belongs to its parent experiment's domain, not a separately chosen one.
    row = ExperimentModel(
        experiment_id=experiment.id,
        model_id=payload.model_id,
        model_label=payload.model_label,
        role=payload.role,
        domain=experiment.domain,
        log_file_path=payload.log_file_path,
        fitted_model_path=payload.fitted_model_path,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def cancel_experiment(db: Session, experiment_id: UUID) -> ExperimentRun:
    row = get_experiment(db, experiment_id)
    row.status = "cancelled"
    db.commit()
    db.refresh(row)
    return row


def get_model_row(db: Session, experiment_id: UUID, model_id: str) -> ExperimentModel:
    row = (
        db.query(ExperimentModel)
        .filter(ExperimentModel.experiment_id == experiment_id, ExperimentModel.model_id == model_id)
        .first()
    )
    if not row:
        http_error(404, "MODEL_NOT_FOUND", f"Model '{model_id}' not registered in experiment {experiment_id}")
    return row


def get_all_models(db: Session, experiment_id: UUID) -> List[ExperimentModel]:
    return db.query(ExperimentModel).filter(ExperimentModel.experiment_id == experiment_id).all()


def get_target_models(db: Session, experiment_id: UUID) -> List[ExperimentModel]:
    return (
        db.query(ExperimentModel)
        .filter(ExperimentModel.experiment_id == experiment_id, ExperimentModel.role == "target")
        .all()
    )


def get_result_rows(db: Session, experiment_id: UUID) -> List[ExperimentResult]:
    return db.query(ExperimentResult).filter(ExperimentResult.experiment_id == experiment_id).all()
