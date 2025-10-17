# app/schemas/survey.py
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict
from datetime import datetime
import uuid

class TAMSUSResponses(BaseModel):
    sus_q1: int = Field(..., ge=1, le=5, description="I think that I would like to use this system frequently.")
    sus_q2: int = Field(..., ge=1, le=5, description="I found the system unnecessarily complex.")
    sus_q3: int = Field(..., ge=1, le=5, description="I thought the system was easy to use.")
    sus_q4: int = Field(..., ge=1, le=5, description="I think that I would need the support of a technical person to be able to use this system.")
    sus_q5: int = Field(..., ge=1, le=5, description="I found the various functions in this system were well integrated.")
    sus_q6: int = Field(..., ge=1, le=5, description="I thought there was too much inconsistency in this system.")
    sus_q7: int = Field(..., ge=1, le=5, description="I would imagine that most people would learn to use this system very quickly.")
    sus_q8: int = Field(..., ge=1, le=5, description="I found the system to be very difficult to use.")
    sus_q9: int = Field(..., ge=1, le=5, description="I felt very confident using the system.")
    sus_q10: int = Field(..., ge=1, le=5, description="I needed to learn many things before I could get going with this system.")

class EthicsResponses(BaseModel):
    q_fairness: int = Field(..., ge=1, le=5, description="Fairness: The system handles different tasks (or users, data) without bias.")
    q_transparency: int = Field(..., ge=1, le=5, description="Transparency: I understand how the system/AI arrives at its suggestions or decisions.")
    q_privacy: int = Field(..., ge=1, le=5, description="Privacy: I feel confident that sensitive or personal data is protected by this system.")
    q_accountability: int = Field(..., ge=1, le=5, description="Accountability: It is clear who or what is responsible if the system makes a mistake.")
    q_trust: int = Field(..., ge=1, le=5, description="Trust: Overall, I trust this system to operate ethically and in my best interest.")

class SurveyCreate(BaseModel):
    schema_id: Optional[str] = Field(
        None, description="ID of the domain-specific question set used to render this survey")
    survey_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="An anonymized identifier for the respondent")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    pilot_tag: str = Field(..., description="A tag indicating from which pilot this survey is received (e.g., 'SmartTicketing', 'SmartEnergy', etc.)")
    app_version: Optional[str] = Field(None, description="Version of the pilot's application")
    ai_model_version: Optional[str] = Field(None, description="Version of the AI model being used")
    tam_sus_responses: TAMSUSResponses
    ethics_responses: EthicsResponses
    domain_specific: Optional[Dict[str, Any]] = Field(
        None, description="Optional domain-specific responses, e.g., for pilot-specific questions"
    )
