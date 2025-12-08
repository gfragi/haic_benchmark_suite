from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.utils.database import Base

class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_id = Column(String, index=True)
    ai_model_version = Column(String)
    app_version = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    interaction_data = Column(JSON)
    retrain_events = Column(JSON)
    performance_infrastructure = Column(JSON)
    performance_logs = Column(JSON)
    ai_model_data = Column(JSON)

    # link to MinIO objects (relative to config_id/)
    raw_filename = Column(String, nullable=True)      # e.g. "uploads/session...json"
    derived_filename = Column(String, nullable=True)  # e.g. "uploads/session...derived.json"

    configuration_id = Column(Integer, ForeignKey('configurations.id'))
    configuration = relationship("EvaluationConfig", back_populates="logs")
