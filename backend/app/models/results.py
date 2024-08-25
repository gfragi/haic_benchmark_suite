import datetime
from sqlalchemy import Column, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.database import Base

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey('configurations.id', ondelete='CASCADE'), nullable=False)

    # AI Model Performance Metrics
    prediction_accuracy = Column(Float, nullable=True)
    response_time = Column(Float, nullable=True)
    teaching_efficiency = Column(Float, nullable=True)
    overall_system_accuracy = Column(Float, nullable=True)
    objective_fulfillment_rate = Column(Float, nullable=True)
    feedback_impact = Column(Float, nullable=True)
    adaptability_score = Column(Float, nullable=True)
    query_efficiency = Column(Float, nullable=True)
    error_reduction_rate = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    model_improvement_rate = Column(Float, nullable=True)
    resource_utilization = Column(Float, nullable=True)
    impact_of_corrections = Column(Float, nullable=True)
    decision_effectiveness = Column(Float, nullable=True)
    knowledge_retention = Column(Float, nullable=True)
    task_completion_time = Column(Float, nullable=True)
    trust_score = Column(Float, nullable=True)
    safety_incidents = Column(Float, nullable=True)
    adversarial_robustness = Column(Float, nullable=True)
    domain_generalization = Column(Float, nullable=True)
    system_reliability = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    human_ai_agreement_rate = Column(Float, nullable=True)
    time_to_resolution = Column(Float, nullable=True)
    human_effort_saved = Column(Float, nullable=True)
    ai_assistance_rate = Column(Float, nullable=True)
    learning_efficiency = Column(Float, nullable=True)
    correction_efficiency = Column(Float, nullable=True)

    evaluation_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Establish a relationship with the Configuration table
    configuration = relationship("EvaluationConfig", back_populates="evaluation_results")