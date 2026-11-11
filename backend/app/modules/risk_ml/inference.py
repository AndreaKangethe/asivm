from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.assets.models import Asset
from app.modules.risk_ml.anomaly import detect_anomaly, explain_anomaly
from app.modules.risk_ml.features import FEATURE_VERSION, FEATURE_NAMES
from app.modules.risk_ml.models import (
    AnomalyEvent,
    AssessmentFactor,
    MLModelVersion,
    RiskAssessment,
)
from app.modules.risk_ml.predictor import explain_risk, predict_risk
from app.modules.risk_ml.registry import ModelRegistry
from app.modules.risk_ml.risk_engine import combine_risk
from app.modules.scans.models import AssetObservation
from app.modules.vulnerabilities.models import AssetVulnerability, VulnerabilityCatalog
from app.modules.risk_ml.retraining import train_anomaly, train_candidate


def ensure_demo_models(db: Session) -> None:
    artifact_dir = Path(get_settings().model_artifact_path)
    if db.scalar(select(MLModelVersion).where(MLModelVersion.name == "risk", MLModelVersion.is_active.is_(True))) is None:
        features = [[0.0, 0.05, 10.0, 0.0], [1.0, 0.95, 100.0, 1.0], [0.0, 0.1, 20.0, 0.0], [2.0, 0.8, 200.0, 3.0]]
        result = train_candidate(features, [0, 1, 0, 1], str(artifact_dir), "risk-initial")
        db.add(MLModelVersion(name="risk", version="risk-initial", artifact_path=result["artifact_path"], feature_version=FEATURE_VERSION, metrics={"roc_auc": 1.0}, is_active=True))
    if db.scalar(select(MLModelVersion).where(MLModelVersion.name == "anomaly", MLModelVersion.is_active.is_(True))) is None:
        features = [[0.0, 0.05, 10.0, 0.0], [0.0, 0.1, 20.0, 0.0], [1.0, 0.9, 100.0, 2.0], [2.0, 0.95, 200.0, 3.0]]
        artifact = train_anomaly(features, str(artifact_dir), "anomaly-initial")
        db.add(MLModelVersion(name="anomaly", version="anomaly-initial", artifact_path=artifact, feature_version=FEATURE_VERSION, metrics={}, is_active=True))
    db.commit()


def _latest_observation(db: Session, asset_id: int) -> AssetObservation | None:
    return db.scalar(
        select(AssetObservation)
        .where(AssetObservation.asset_id == asset_id)
        .order_by(AssetObservation.observed_at.desc(), AssetObservation.id.desc())
    )


def _previous_observation(db: Session, asset_id: int, latest_id: int) -> AssetObservation | None:
    return db.scalar(
        select(AssetObservation)
        .where(AssetObservation.asset_id == asset_id, AssetObservation.id < latest_id)
        .order_by(AssetObservation.observed_at.desc(), AssetObservation.id.desc())
    )


def infer_all(db: Session) -> int:
    ensure_demo_models(db)
    registry = ModelRegistry(get_settings().model_artifact_path)
    risk_model = registry.load_active(db, "risk").estimator
    anomaly_model = registry.load_active(db, "anomaly").estimator
    created = 0
    for asset in db.scalars(select(Asset).order_by(Asset.id)):
        latest = _latest_observation(db, asset.id)
        if latest is None:
            continue
        previous = _previous_observation(db, asset.id, latest.id)
        vulnerabilities = list(
            db.scalars(
                select(VulnerabilityCatalog)
                .join(AssetVulnerability, AssetVulnerability.vulnerability_id == VulnerabilityCatalog.id)
                .where(AssetVulnerability.asset_id == asset.id)
            )
        )
        values = {
            "kev_count": float(sum(1 for item in vulnerabilities if item.is_kev)),
            "epss_max": float(max((item.epss_score or 0.0 for item in vulnerabilities), default=0.0)),
            "asset_age_days": max(0.0, (datetime.utcnow() - asset.created_at).total_seconds() / 86400),
            "observation_change_count": float(previous is not None and previous.payload != latest.payload),
        }
        model_score = predict_risk(risk_model, values)
        context = max(vulnerabilities, key=lambda item: (item.is_kev, item.epss_score or 0.0), default=None)
        score = combine_risk(
            model_score,
            cvss_score=context.cvss_score if context else None,
            epss_score=context.epss_score if context else None,
            is_kev=context.is_kev if context else False,
        )
        assessment = RiskAssessment(asset_id=asset.id, score=score, model_version="risk-initial")
        db.add(assessment)
        db.flush()
        for feature, contribution in explain_risk(risk_model, values).items():
            db.add(AssessmentFactor(assessment_id=assessment.id, feature=feature, contribution=contribution))
        anomaly_score = detect_anomaly(anomaly_model, values)
        if anomaly_score < 0 or values["observation_change_count"]:
            db.add(
                AnomalyEvent(
                    asset_id=asset.id,
                    score=max(0.0, -anomaly_score),
                    contributing_features=explain_anomaly(values, anomaly_score),
                )
            )
        created += 1
    db.commit()
    return created
