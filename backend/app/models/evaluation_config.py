from sqlalchemy import Column, ForeignKey, String, Integer, Table, JSON
from sqlalchemy.orm import relationship
from app.utils.database import Base


evaluation_metric_association = Table(
    'evaluation_metric_association',
    Base.metadata,
    Column('evaluation_config_id', Integer, ForeignKey('evaluation_configs.id', ondelete='CASCADE')),
    Column('metric_id', Integer, ForeignKey('metrics.id'))
)

association_table = Table(
    'association', Base.metadata,
    Column('evaluation_config_id', ForeignKey('evaluation_configs.id', ondelete='CASCADE')),
    Column('metric_id', ForeignKey('metrics.id'))
)

class EvaluationConfig(Base):
    __tablename__ = "evaluation_configs"

    id = Column(Integer, primary_key=True, index=True)
    application_name = Column(String, index=True)
    ai_model_name = Column(String)
    description = Column(String, nullable=True)
    metrics = Column(JSON)
    evaluation_date = Column(String, nullable=True)
    config_type = Column(String, nullable=True)

    metrics = relationship(
        "Metric",
        secondary=association_table,
        back_populates="evaluation_configs"
    )

    # Relationship to associate with logs
    logs = relationship("LogEntry", back_populates="evaluation_config")

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)

    evaluation_configs = relationship(
        "EvaluationConfig",
        secondary=association_table,
        back_populates="metrics"
    )
