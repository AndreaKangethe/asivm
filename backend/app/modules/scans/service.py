from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.assets.reconciliation import resolve_observation
from app.modules.scans.collector import collect
from app.modules.scans.models import AssetObservation, Scan
from app.modules.risk_ml.models import AnomalyEvent, RiskAssessment
from app.modules.vulnerabilities.models import AssetVulnerability, VulnerabilityCatalog
from sqlalchemy import func, select


def run_scan(db: Session) -> Scan:
    scan = Scan(status="running")
    db.add(scan)
    db.flush()
    for observation in collect():
        asset = resolve_observation(db, observation)
        persisted = AssetObservation(
                scan_id=scan.id,
                asset_id=asset.id if asset else None,
                identifier_type=observation.identifier_type,
                identifier_value=observation.identifier_value,
                observed_at=observation.observed_at,
                payload=observation.metadata,
        )
        db.add(persisted)
        db.flush()
        if asset:
            vulnerabilities = db.scalars(
                select(VulnerabilityCatalog)
                .join(AssetVulnerability, AssetVulnerability.vulnerability_id == VulnerabilityCatalog.id)
                .where(AssetVulnerability.asset_id == asset.id)
            ).all()
            score = min(
                1.0,
                sum(
                    (v.cvss_score or 0) / 10 * 0.25
                    + (v.epss_score or 0) * 0.25
                    + (0.5 if v.is_kev else 0)
                    for v in vulnerabilities
                ),
            )
            db.add(RiskAssessment(asset_id=asset.id, score=score, model_version="demo"))
            observation_count = db.scalar(
                select(func.count(AssetObservation.id)).where(AssetObservation.asset_id == asset.id)
            ) or 0
            if observation_count > 1:
                db.add(
                    AnomalyEvent(
                        asset_id=asset.id,
                        score=0.75,
                        contributing_features={"observation_change_count": 1},
                    )
                )
    scan.status = "completed"
    scan.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(scan)
    return scan
