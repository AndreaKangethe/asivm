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
        persisted = AssetObservation(
            scan_id=scan.id,
            asset_id=asset.id,
            identifier_type=next(iter(observation.identifiers)),
            identifier_value=observation.identifiers[next(iter(observation.identifiers))],
            observed_at=observation.observed_at,
            payload={"identifiers": observation.identifiers, **observation.metadata},
        )
        db.add(persisted)
    scan.status = "completed"
    scan.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(scan)
    return scan
