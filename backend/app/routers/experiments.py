from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.experiments import (
    ExperimentCreateResponse,
    ExperimentDeleteResponse,
    ExperimentDetail,
    ExperimentModelIn,
    ExperimentModelOut,
    ExperimentRunIn,
    ExperimentSummary,
)
from app.services import experiment_service
from app.utils.database import get_db

router = APIRouter()


@router.post("", response_model=ExperimentCreateResponse, status_code=201, summary="Create an experiment run")
def create_experiment(payload: ExperimentRunIn, db: Session = Depends(get_db)):
    row = experiment_service.create_experiment(db, payload)
    return ExperimentCreateResponse(experiment_id=row.id)


@router.post("/{experiment_id}/models", response_model=ExperimentModelOut, status_code=201, summary="Register a model in an experiment")
def register_model(experiment_id: UUID, payload: ExperimentModelIn, db: Session = Depends(get_db)):
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
