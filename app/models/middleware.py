import time

from pydantic import BaseModel, Field


class IpInSurveillance(BaseModel):
    ip: str = Field()
    last_modification_timestamp: float | None = Field(default_factory=time.time, description="timestamp in seconds")
    attempts: int = Field(default=1)
