from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.vulnerabilities.models import VulnerabilityCatalog
from app.modules.vulnerabilities.schemas import VulnerabilityUpsert


def upsert_vulnerability(db: Session, data: VulnerabilityUpsert) -> VulnerabilityCatalog:
    item = db.scalar(select(VulnerabilityCatalog).where(VulnerabilityCatalog.cve_id == data.cve_id))
    if item is None:
        item = VulnerabilityCatalog(cve_id=data.cve_id)
        db.add(item)
    item.description = data.description
    item.cvss_score = data.cvss_score
    item.epss_score = data.epss_score
    item.is_kev = data.is_kev
    item.retrieved_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item


def list_vulnerabilities(db: Session) -> list[VulnerabilityCatalog]:
    return list(db.scalars(select(VulnerabilityCatalog).order_by(VulnerabilityCatalog.cve_id)))
