from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict

class MetricSchema(BaseModel):
    metric_name: str

class SmartCitiesConfigSchema(BaseModel):
    specific_field_smart_cities_1: Optional[str] = None
    specific_field_smart_cities_2: Optional[str] = None

class RadiologyConfigSchema(BaseModel):
    specific_field_radiology_1: Optional[str] = None
    specific_field_radiology_2: Optional[str] = None

class EnergyConfigSchema(BaseModel):
    specific_field_energy_1: Optional[str] = None
    specific_field_energy_2: Optional[str] = None

class GenericConfigSchema(BaseModel):
    generic_field_1: Optional[str] = None
    generic_field_2: Optional[str] = None

class EvaluationConfigSchema(BaseModel):
    config_id: Optional[int] = Field(None, alias="id")
    application_name: str
    ai_model_name: str
    metrics: List[MetricSchema]
    evaluation_date: Optional[str] = None
    description: Optional[str] = None
    config_type: str  # Either 'specific' or 'generic'
    application_specific_details: Optional[
        Union[SmartCitiesConfigSchema, RadiologyConfigSchema, EnergyConfigSchema]
    ] = None
    generic_config_details: Optional[GenericConfigSchema] = None

    class Config:
        json_schema_extra = {
            "example": {
                "application_name": "RadiologyApp",
                "ai_model_name": "TumorDetectionModelV1",
                "metrics": [
                    {"metric_name": "Prediction Accuracy"},
                    {"metric_name": "Response Time"},
                ],
                "evaluation_date": "2024-07-01",
                "description": "Evaluation of Tumor Detection Model in RadiologyApp",
                "config_type": "specific",
                "application_specific_details": {
                    "specific_field_radiology_1": "Example detail specific to Radiology",
                    "specific_field_radiology_2": "Another example"
                },
            }
        }