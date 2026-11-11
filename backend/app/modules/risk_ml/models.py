from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AnomalyStatus(StrEnum):
    OPEN = "open"
    TRIAGED = "triaged"
    CLOSED = "closed"


class MLModelVersion(Base):
    __tablename__ = "ml_model_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    version: Mapped[str] = mapped_column(String(64), unique=True)
    artifact_path: Mapped[str] = mapped_column(String(512))
    feature_version: Mapped[str] = mapped_column(String(32))
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=False)


class MLTrainingRun(Base):
    __tablename__ = "ml_training_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_version_id: Mapped[int | None] = mapped_column(ForeignKey("ml_model_versions.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    score: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(64))
    assessed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AssessmentFactor(Base):
    __tablename__ = "assessment_factors"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("risk_assessments.id"), index=True)
    feature: Mapped[str] = mapped_column(String(128))
    contribution: Mapped[float] = mapped_column(Float)


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    score: Mapped[float] = mapped_column(Float)
    status: Mapped[AnomalyStatus] = mapped_column(default=AnomalyStatus.OPEN)
    contributing_features: Mapped[dict] = mapped_column(JSON, default=dict)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
