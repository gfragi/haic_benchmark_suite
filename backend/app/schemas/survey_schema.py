from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
import uuid

QuestionType = str  # "likert" | "single" | "multi" | "text" | "number" | "boolean"

class LikertScale(BaseModel):
    min: int = 1
    max: int = 5
    min_label: Optional[str] = None
    max_label: Optional[str] = None

class Question(BaseModel):
    id: str = Field(..., description="Stable identifier; also used as CSV column")
    label: str
    type: QuestionType
    required: bool = False
    group: Optional[str] = None
    scale: Optional[LikertScale] = None
    options: Optional[List[str]] = None

class SurveyQuestionSetIn(BaseModel):
    name: Optional[str] = None
    pilot_tag: Optional[str] = None
    version: Optional[int] = 1
    questions: List[Question]
    active: bool = True
    created_by: Optional[str] = None

class SurveyQuestionSetOut(SurveyQuestionSetIn):
    schema_id: str

class SchemaId(BaseModel):
    schema_id: str

    @field_validator("schema_id")
    @classmethod
    def validate_uuid(cls, v):
        uuid.UUID(str(v))
        return v
