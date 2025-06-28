from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.utils.database import Base



class Survey(Base):
    __tablename__ = "surveys"

    survey_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    pilot_tag = Column(String, nullable=False)  # Field to capture the pilot tag
    app_version = Column(String)
    ai_model_version = Column(String)
    tam_sus_responses = Column(JSON)   # Store the SUS/TAM responses as JSON
    ethics_responses = Column(JSON)    # Store the ethics responses as JSON
    domain_specific = Column(JSON)       # Optional domain-specific data
