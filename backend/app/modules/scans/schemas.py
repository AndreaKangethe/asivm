from datetime import datetime

from pydantic import BaseModel


class ScanRead(BaseModel):
    id: int
    status: str
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
