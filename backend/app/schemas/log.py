from pydantic import BaseModel
from typing import List, Optional

class LogSchema(BaseModel):
    session_id: str
    user_id: str
    ai_model_version: str
    app_version: str
    start_time: str
    end_time: str
    evaluation_config_id: int
    interaction_data: List[dict]
    retrain_events: List[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "unique_session_id",
                "user_id": "unique_user_id",
                "ai_model_version": "1.0.0",
                "app_version": "1.0.0",
                "start_time": "2024-06-28T12:00:00Z",
                "end_time": "2024-06-28T12:30:00Z",
                "evaluation_config_id": 1,
                "interaction_data": [],
                "retrain_events": []
            }
        }
