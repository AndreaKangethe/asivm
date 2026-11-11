from datetime import datetime

from pydantic import BaseModel, Field


class VulnerabilityRead(BaseModel):
    id: int
    cve_id: str
    description: str | None
    cvss_score: float | None
    cvss_version: str | None
    cvss_published_at: datetime | None
    epss_score: float | None
    epss_percentile: float | None
    epss_score_date: datetime | None
    is_kev: bool
    kev_date_added: datetime | None
    kev_due_date: datetime | None
    kev_required_action: str | None
    kev_ransomware_use: str | None
    retrieved_at: datetime
    kev_retrieved_at: datetime | None
    epss_retrieved_at: datetime | None
    source_provenance: dict

    model_config = {"from_attributes": True}


class VulnerabilityUpsert(BaseModel):
    cve_id: str = Field(pattern=r"^CVE-\d{4}-\d+$")
    description: str | None = None
    cvss_score: float | None = Field(default=None, ge=0, le=10)
    cvss_version: str | None = None
    cvss_published_at: datetime | None = None
    epss_score: float | None = Field(default=None, ge=0, le=1)
    epss_percentile: float | None = Field(default=None, ge=0, le=1)
    epss_score_date: datetime | None = None
    is_kev: bool | None = None
    kev_date_added: datetime | None = None
    kev_due_date: datetime | None = None
    kev_required_action: str | None = None
    kev_ransomware_use: str | None = None
    source: str = "unknown"
    source_version: str | None = None
    source_effective_at: datetime | None = None
    raw_payload: dict = Field(default_factory=dict)
