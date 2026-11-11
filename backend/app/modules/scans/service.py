from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.assets.reconciliation import resolve_observation
from app.modules.scans.collector import collect
from app.modules.scans.models import AssetObservation, Scan


def run_scan(db: Session) -> Scan:
    scan = Scan(status="running")
    db.add(scan)
    db.flush()
    for observation in collect():
        asset = resolve_observation(db, observation)
        db.add(
            AssetObservation(
                scan_id=scan.id,
                asset_id=asset.id if asset else None,
                identifier_type=observation.identifier_type,
                identifier_value=observation.identifier_value,
                observed_at=observation.observed_at,
                payload=observation.metadata,
            )
        )
    scan.status = "completed"
    scan.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(scan)
    return scan
