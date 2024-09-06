from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime



class MetricGroupSchema(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    metrics: Optional[List['MetricSchema']] = []

    class Config:
        from_attributes = True


class MetricSchema(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    group_id: int

    class Config:
        from_attributes = True
