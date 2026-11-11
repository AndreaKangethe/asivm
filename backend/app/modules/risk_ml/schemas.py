from datetime import datetime

from pydantic import BaseModel


class RiskAssessmentRead(BaseModel):
    asset_id: int
    score: float
    model_version: str
    assessed_at: datetime


class AnomalyRead(BaseModel):
    asset_id: int
    score: float
    status: str
    detected_at: datetime
