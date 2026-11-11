from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VulnerabilityCatalog(Base):
    __tablename__ = "vulnerability_catalog"

    id: Mapped[int] = mapped_column(primary_key=True)
    cve_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    epss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_kev: Mapped[bool] = mapped_column(default=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    kev_retrieved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    epss_retrieved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AssetVulnerability(Base):
    __tablename__ = "asset_vulnerabilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    vulnerability_id: Mapped[int] = mapped_column(ForeignKey("vulnerability_catalog.id"), index=True)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
