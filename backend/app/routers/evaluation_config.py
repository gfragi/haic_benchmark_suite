from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.evaluation_config import EvaluationConfig, Metric
from app.schemas.evaluation_config import  EvaluationConfigSchema

router = APIRouter()

@router.post("/config", response_model=EvaluationConfigSchema)
def create_evaluation_config(config: EvaluationConfigSchema, db: Session = Depends(get_db)):
    db_metrics = []
    for metric in config.metrics:
        db_metric = db.query(Metric).filter(Metric.metric_name == metric.metric_name).first()
        if not db_metric:
            db_metric = Metric(**metric.dict())
            db.add(db_metric)
            db.commit()
            db.refresh(db_metric)
        db_metrics.append(db_metric)

    db_config = EvaluationConfig(
        application_name=config.application_name,
        ai_model_name=config.ai_model_name,
        description=config.description,
        metrics=db_metrics,
        evaluation_date=config.evaluation_date
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/config/{config_id}", response_model=EvaluationConfigSchema)
def get_evaluation_config(config_id: int, db: Session = Depends(get_db)):
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found")
    return config

@router.get("/config", response_model=List[EvaluationConfigSchema])
def get_all_evaluation_configs(db: Session = Depends(get_db)):
    return db.query(EvaluationConfig).all()
