from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any, Literal
import uuid

# Kept in sync with the branches in survey_schema_service.validate_answers_against_schema
# and with the frontend's DomainQuestion widget switch - any value outside this set
# renders as a plain textarea and fails answer validation, so it must be rejected here
# at schema-creation time rather than discovered later.
QuestionType = Literal["likert", "single", "multi", "text", "number", "boolean"]

class LikertScale(BaseModel):
    min: int = 1
    max: int = 5
    min_label: Optional[str] = None
    max_label: Optional[str] = None

    @model_validator(mode="after")
    def check_range(self):
        if self.min >= self.max:
            raise ValueError(f"scale.min ({self.min}) must be less than scale.max ({self.max})")
        return self

class Question(BaseModel):
    id: str = Field(..., description="Stable identifier; also used as CSV column")
    label: str
    type: QuestionType
    required: bool = False
    group: Optional[str] = None
    scale: Optional[LikertScale] = None
    options: Optional[List[str]] = None

    @model_validator(mode="after")
    def check_options_present(self):
        if self.type in ("single", "multi") and not self.options:
            raise ValueError(f"question {self.id!r} has type {self.type!r} and requires a non-empty options list")
        return self

class SurveyQuestionSetIn(BaseModel):
    name: Optional[str] = None
    pilot_tag: Optional[str] = None
    version: Optional[int] = 1
    questions: List[Question]
    question_position: Optional[str] = "last"  # "first" | "last" - domain questions relative to SUS/Ethics
    active: bool = True
    created_by: Optional[str] = None
    # Override the public survey form's default heading/subtitle - null on
    # either means the form falls back to its hardcoded default for that one.
    intro_title: Optional[str] = None
    intro_description: Optional[str] = None

class SurveyQuestionSetOut(SurveyQuestionSetIn):
    schema_id: str

class SchemaId(BaseModel):
    schema_id: str

    @field_validator("schema_id")
    @classmethod
    def validate_uuid(cls, v):
        uuid.UUID(str(v))
        return v
