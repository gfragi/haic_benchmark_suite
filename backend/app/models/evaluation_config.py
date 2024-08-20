from sqlalchemy import Column, ForeignKey, String, Integer, Table
from sqlalchemy.orm import relationship
from app.utils.database import Base


evaluation_metric_association = Table(
    'evaluation_metric_association',
    Base.metadata,
    Column('evaluation_config_id', Integer, ForeignKey('evaluation_configs.id')),
    Column('metric_id', Integer, ForeignKey('metrics.id'))
)

class EvaluationConfig(Base):
    __tablename__ = "evaluation_configs"

    id = Column(Integer, primary_key=True, index=True)
    application_name = Column(String, index=True)
    ai_model_name = Column(String)
    description = Column(String, nullable=True)
    metrics = relationship("Metric", secondary=evaluation_metric_association, back_populates="evaluation_configs")
    evaluation_date = Column(String, nullable=True)

    logs = relationship("LogEntry", back_populates="evaluation_config")


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)
    metric_formula = Column(String, nullable=True)
    description = Column(String, nullable=True)
    evaluation_configs = relationship("EvaluationConfig", secondary=evaluation_metric_association, back_populates="metrics")
