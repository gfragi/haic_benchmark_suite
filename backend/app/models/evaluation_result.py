from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.utils.database import Base

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    # log_id = Column(Integer, ForeignKey('logs.id'), nullable=False)
    # log = relationship("LogEntry", back_populates="evaluation_results")

    # metrics = Column(JSON, nullable=False)  # Store evaluation metrics as JSON
    # evaluation_date = Column(String, nullable=False)  # Store the date of evaluation
    # ai_model_name = Column(String, nullable=True)  # AI model used during evaluation
