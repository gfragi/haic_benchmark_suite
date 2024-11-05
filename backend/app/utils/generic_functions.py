from sqlalchemy.orm import Session
from app.models import EvaluationConfig
from app.models.logs import LogEntry
from datetime import datetime, timedelta
import random

def get_config_by_id(configuration_id: int, db: Session):
    return db.query(EvaluationConfig).filter(EvaluationConfig.id == configuration_id).first()


def save_log_entry(log_entry: LogEntry, db: Session):
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry



def random_date(start: datetime, end: datetime) -> datetime:
    """Generate a random datetime between `start` and `end`."""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)
