from datetime import datetime

from app.modules.vulnerabilities.schemas import VulnerabilityUpsert


def _date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value).replace(tzinfo=None)


def parse_kev_snapshot(payload: dict) -> list[VulnerabilityUpsert]:
    result = []
    for item in payload.get("vulnerabilities", []):
        cve_id = item.get("cveID")
        if not cve_id:
            continue
        result.append(
            VulnerabilityUpsert(
                cve_id=cve_id,
                description=item.get("shortDescription"),
                is_kev=True,
                kev_date_added=_date(item.get("dateAdded")),
                kev_due_date=_date(item.get("dueDate")),
                kev_required_action=item.get("requiredAction"),
                kev_ransomware_use=item.get("knownRansomwareCampaignUse"),
                source="cisa_kev",
                source_version=payload.get("catalogVersion"),
                source_effective_at=_date(item.get("dateAdded")),
                raw_payload=item,
            )
        )
    return result
