from sqlalchemy.orm import Session
from app.models import EvaluationConfig
from app.utils.database import get_db
from app.models.logs import LogEntry


def get_config_by_id(config_id: int, db: Session):
    return db.query(EvaluationConfig).filter(EvaluationConfig.id == config_id).first()


def save_log_entry(log_entry: LogEntry, db: Session):
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry