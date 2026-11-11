from datetime import datetime

from pydantic import BaseModel, Field


class VulnerabilityRead(BaseModel):
    id: int
    cve_id: str
    description: str | None
    cvss_score: float | None
    epss_score: float | None
    is_kev: bool
    retrieved_at: datetime
    kev_retrieved_at: datetime | None
    epss_retrieved_at: datetime | None

    model_config = {"from_attributes": True}


class VulnerabilityUpsert(BaseModel):
    cve_id: str = Field(pattern=r"^CVE-\d{4}-\d+$")
    description: str | None = None
    cvss_score: float | None = Field(default=None, ge=0, le=10)
    epss_score: float | None = Field(default=None, ge=0, le=1)
    is_kev: bool = False
