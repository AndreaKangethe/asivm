from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.vulnerabilities.models import VulnerabilityCatalog
from app.modules.vulnerabilities.models import AssetVulnerability
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
    if data.is_kev:
        item.kev_retrieved_at = item.retrieved_at
    if data.epss_score is not None:
        item.epss_retrieved_at = item.retrieved_at
    db.commit()
    db.refresh(item)
    return item


def list_vulnerabilities(db: Session) -> list[VulnerabilityCatalog]:
    return list(db.scalars(select(VulnerabilityCatalog).order_by(VulnerabilityCatalog.cve_id)))


def match_asset(
    db: Session,
    asset_id: int,
    cve_ids: list[str] | None = None,
    evidence: dict | None = None,
) -> list[AssetVulnerability]:
    wanted = set(cve_ids or [])
    catalog = list(
        db.scalars(
            select(VulnerabilityCatalog).where(
                VulnerabilityCatalog.cve_id.in_(wanted) if wanted else False
            )
        )
    )
    matches: list[AssetVulnerability] = []
    for vulnerability in catalog:
        existing = db.scalar(
            select(AssetVulnerability).where(
                AssetVulnerability.asset_id == asset_id,
                AssetVulnerability.vulnerability_id == vulnerability.id,
            )
        )
        if existing is None:
            existing = AssetVulnerability(
                asset_id=asset_id,
                vulnerability_id=vulnerability.id,
                evidence=evidence or {},
            )
            db.add(existing)
        matches.append(existing)
    return matches
