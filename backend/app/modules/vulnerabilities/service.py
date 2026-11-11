from datetime import datetime
import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.vulnerabilities.models import (
    AssetVulnerability,
    VulnerabilityCatalog,
    VulnerabilityIntelligenceSnapshot,
)
from app.modules.vulnerabilities.schemas import VulnerabilityUpsert


def _snapshot_hash(data: VulnerabilityUpsert) -> str:
    payload = json.dumps(data.raw_payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{data.source}:{data.cve_id}:{payload}".encode()).hexdigest()


def upsert_vulnerability(db: Session, data: VulnerabilityUpsert) -> VulnerabilityCatalog:
    now = datetime.utcnow()
    item = db.scalar(select(VulnerabilityCatalog).where(VulnerabilityCatalog.cve_id == data.cve_id))
    if item is None:
        item = VulnerabilityCatalog(cve_id=data.cve_id, source_provenance={})
        db.add(item)
        db.flush()

    if data.description is not None:
        item.description = data.description
    if data.cvss_score is not None:
        item.cvss_score = data.cvss_score
        item.cvss_version = data.cvss_version
        item.cvss_published_at = data.cvss_published_at
    if data.epss_score is not None:
        item.epss_score = data.epss_score
        item.epss_percentile = data.epss_percentile
        item.epss_score_date = data.epss_score_date
        item.epss_retrieved_at = now
    if data.is_kev is True:
        item.is_kev = True
        item.kev_date_added = data.kev_date_added
        item.kev_due_date = data.kev_due_date
        item.kev_required_action = data.kev_required_action
        item.kev_ransomware_use = data.kev_ransomware_use
        item.kev_retrieved_at = now
    item.retrieved_at = now
    provenance = dict(item.source_provenance or {})
    provenance[data.source] = {
        "source_version": data.source_version,
        "source_effective_at": data.source_effective_at.isoformat() if data.source_effective_at else None,
        "retrieved_at": now.isoformat(),
    }
    item.source_provenance = provenance

    if data.raw_payload:
        payload_hash = _snapshot_hash(data)
        existing = db.scalar(
            select(VulnerabilityIntelligenceSnapshot).where(
                VulnerabilityIntelligenceSnapshot.payload_hash == payload_hash
            )
        )
        if existing is None:
            db.add(
                VulnerabilityIntelligenceSnapshot(
                    cve_id=data.cve_id,
                    source=data.source,
                    source_version=data.source_version,
                    effective_at=data.source_effective_at or now,
                    retrieved_at=now,
                    payload_hash=payload_hash,
                    payload=data.raw_payload,
                )
            )
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
    observed_at: datetime | None = None,
) -> list[AssetVulnerability]:
    wanted = set(cve_ids or [])
    timestamp = observed_at or datetime.utcnow()
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
                AssetVulnerability.observed_at == timestamp,
            )
        )
        if existing is None:
            existing = AssetVulnerability(
                asset_id=asset_id,
                vulnerability_id=vulnerability.id,
                observed_at=timestamp,
                valid_from=timestamp,
                evidence=evidence or {},
            )
            db.add(existing)
        matches.append(existing)
    return matches
