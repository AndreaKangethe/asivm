from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VulnerabilityCatalog(Base):
    __tablename__ = "vulnerability_catalog"

    id: Mapped[int] = mapped_column(primary_key=True)
    cve_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cvss_version: Mapped[str | None] = mapped_column(String(16), nullable=True)
    cvss_published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    epss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    epss_percentile: Mapped[float | None] = mapped_column(Float, nullable=True)
    epss_score_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_kev: Mapped[bool] = mapped_column(default=False)
    kev_date_added: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    kev_due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    kev_required_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    kev_ransomware_use: Mapped[str | None] = mapped_column(String(32), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    kev_retrieved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    epss_retrieved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_provenance: Mapped[dict] = mapped_column(JSON, default=dict)


class VulnerabilityIntelligenceSnapshot(Base):
    __tablename__ = "vulnerability_intelligence_snapshots"
    __table_args__ = (Index("ix_vulnerability_snapshot_lookup", "cve_id", "source", "effective_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cve_id: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    source_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    effective_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    payload_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON)


class VulnerabilityIngestionRun(Base):
    __tablename__ = "vulnerability_ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    source_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32))
    records_seen: Mapped[int] = mapped_column(default=0)
    records_imported: Mapped[int] = mapped_column(default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class AssetVulnerability(Base):
    __tablename__ = "asset_vulnerabilities"
    __table_args__ = (Index("ix_asset_vulnerability_history", "asset_id", "vulnerability_id", "observed_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    vulnerability_id: Mapped[int] = mapped_column(ForeignKey("vulnerability_catalog.id"), index=True)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=datetime.utcnow, index=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=datetime.utcnow)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
