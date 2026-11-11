from datetime import datetime
from enum import IntEnum, StrEnum

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AnomalyStatus(StrEnum):
    OPEN = "open"
    TRIAGED = "triaged"
    CLOSED = "closed"


class RiskClass(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class RiskLabelSource(StrEnum):
    EXPERT_REVIEW = "expert_review"


class MLModelVersion(Base):
    __tablename__ = "ml_model_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    version: Mapped[str] = mapped_column(String(64), unique=True)
    artifact_path: Mapped[str] = mapped_column(String(512))
    feature_version: Mapped[str] = mapped_column(String(32))
    feature_names: Mapped[list[str]] = mapped_column(JSON, default=list)
    contract_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    training_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    deployment_mode: Mapped[str] = mapped_column(String(32), default="active")
    is_active: Mapped[bool] = mapped_column(default=False)


class MLTrainingRun(Base):
    __tablename__ = "ml_training_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_version_id: Mapped[int | None] = mapped_column(ForeignKey("ml_model_versions.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running")


class RiskLabel(Base):
    __tablename__ = "risk_labels"
    __table_args__ = (
        CheckConstraint("risk_class IN (0, 1, 2)", name="ck_risk_label_class"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    observation_id: Mapped[int] = mapped_column(ForeignKey("asset_observations.id"), index=True)
    risk_class: Mapped[int] = mapped_column(Integer)
    label_source: Mapped[str] = mapped_column(String(64), default=RiskLabelSource.EXPERT_REVIEW.value)
    reviewer: Mapped[str] = mapped_column(String(255))
    assessed_at: Mapped[datetime] = mapped_column(DateTime)
    justification: Mapped[str] = mapped_column(String(4000))
    label_version: Mapped[str] = mapped_column(String(32))


class ExploitationOutcome(Base):
    __tablename__ = "exploitation_outcomes"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    observation_id: Mapped[int | None] = mapped_column(ForeignKey("asset_observations.id"), nullable=True, index=True)
    outcome_type: Mapped[str] = mapped_column(String(128))
    occurred_at: Mapped[datetime] = mapped_column(DateTime)
    verified_at: Mapped[datetime] = mapped_column(DateTime)
    verifier: Mapped[str] = mapped_column(String(255))
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    source: Mapped[str] = mapped_column(String(128))


class TrainingDatasetRow(Base):
    __tablename__ = "training_dataset_rows"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_version: Mapped[str] = mapped_column(String(128), index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    observation_id: Mapped[int] = mapped_column(ForeignKey("asset_observations.id"), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    feature_version: Mapped[str] = mapped_column(String(32))
    feature_values: Mapped[dict] = mapped_column(JSON)
    vulnerability_relationships: Mapped[list] = mapped_column(JSON, default=list)
    intelligence_provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    risk_label_id: Mapped[int] = mapped_column(ForeignKey("risk_labels.id"), index=True)
    row_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    score: Mapped[float] = mapped_column(Float)
    risk_class: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_version: Mapped[str] = mapped_column(String(64))
    assessed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    observation_id: Mapped[int | None] = mapped_column(ForeignKey("asset_observations.id"), nullable=True, index=True)
    deployment_mode: Mapped[str] = mapped_column(String(32), default="active")


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
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_note: Mapped[str | None] = mapped_column(String(2000), nullable=True)
