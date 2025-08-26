from pydantic import BaseModel, Field
from typing import Optional, Literal

Actor = Literal["human", "ai"]

class Decision(BaseModel):
    t: float = Field(..., description="Timestamp (seconds, monotonic within run)")
    actor: Actor = Field(..., description="'human' or 'ai'")
    action: str = Field(..., description="Action label")
    latency: Optional[float] = Field(None, ge=0, description="Response time in seconds")
    accepted: Optional[bool] = Field(
        None, description="If actor='ai', whether the human accepted the AI suggestion"
    )
    reward: Optional[float] = Field(
        None, description="Cumulative or instantaneous reward (depends on scenario)"
    )
