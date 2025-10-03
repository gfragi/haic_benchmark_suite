from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.utils.database import Base

def _uuid():
    return uuid.uuid4()

class SurveyQuestionSet(Base):
    __tablename__ = "survey_question_sets"

    schema_id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    name = Column(String, nullable=True)
    pilot_tag = Column(String, nullable=True, index=True)   # if null => generic/ad-hoc
    version = Column(Integer, nullable=False, default=1)
    questions = Column(JSON, nullable=False)                 # array of question dicts
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
