from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import LogEntry, EvaluationConfig
from app.schemas.log import LogSchema

router = APIRouter()

@router.post("/", response_model=LogSchema)
def create_log(log: LogSchema, db: Session = Depends(get_db)):
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == log.evaluation_config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found")

    log_entry = LogEntry(
        session_id=log.session_id,
        user_id=log.user_id,
        ai_model_version=log.ai_model_version,
        app_version=log.app_version,
        start_time=log.start_time,
        end_time=log.end_time,
        interaction_data=log.interaction_data,
        retrain_events=log.retrain_events,
        evaluation_config_id=log.evaluation_config_id
    )

    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
