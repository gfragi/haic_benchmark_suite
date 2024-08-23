from pydantic import BaseModel
from typing import Optional

class LogParams(BaseModel):
    count: int  # Number of logs to generate
    start_date: str  # Start date for log generation
    end_date: str  # End date for log generation
    model_version_range: Optional[str] = "1.0.0-3.0.0"  # Model version range

class Log(BaseModel):
    session_id: str
    user_id: str
    model_version: str
    app_version: str
    start_time: str
    end_time: str
    interaction_data: dict
    retrain_events: list
    performance_infrastructure: dict
    performance_logs: dict
    ai_model_data: dict
