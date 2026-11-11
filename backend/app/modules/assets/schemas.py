from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ObservationData(BaseModel):
    identifiers: dict[str, str] = Field(default_factory=dict)
    identifier_type: str | None = None
    identifier_value: str | None = None
    observed_at: datetime
    metadata: dict[str, object] = Field(default_factory=dict)
    asset_name: str | None = None

    @model_validator(mode="after")
    def normalize_identifiers(self) -> "ObservationData":
        if not self.identifiers and self.identifier_type and self.identifier_value:
            self.identifiers = {self.identifier_type: self.identifier_value}
        if not self.identifiers:
            raise ValueError("at least one identifier is required")
        if self.identifier_type is None:
            self.identifier_type = next(iter(self.identifiers))
            self.identifier_value = self.identifiers[self.identifier_type]
        return self

    @classmethod
    def from_identifier(
        cls,
        *,
        identifier_type: str,
        identifier_value: str,
        observed_at: datetime,
        metadata: dict[str, object] | None = None,
        asset_name: str | None = None,
    ) -> "ObservationData":
        return cls(
            identifiers={identifier_type: identifier_value},
            observed_at=observed_at,
            metadata=metadata or {},
            asset_name=asset_name,
        )


class AssetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

class IdentifierRead(BaseModel):
    identifier_type: str
    value: str
    valid_from: datetime
    valid_to: datetime | None

    model_config = {"from_attributes": True}


class AssetRead(AssetCreate):
    id: int
    created_at: datetime
    identifiers: list[IdentifierRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}
