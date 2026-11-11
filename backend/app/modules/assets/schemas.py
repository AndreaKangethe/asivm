from datetime import datetime

from pydantic import BaseModel, Field


class ObservationData(BaseModel):
    identifier_type: str = Field(min_length=1)
    identifier_value: str = Field(min_length=1)
    observed_at: datetime
    metadata: dict[str, object] = Field(default_factory=dict)


class AssetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class AssetRead(AssetCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
