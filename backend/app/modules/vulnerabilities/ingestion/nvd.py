from datetime import datetime

from app.modules.vulnerabilities.schemas import VulnerabilityUpsert


def _timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def _select_cvss(metrics: dict) -> tuple[float | None, str | None]:
    for key, version in (("cvssMetricV40", "4.0"), ("cvssMetricV31", "3.1"), ("cvssMetricV30", "3.0"), ("cvssMetricV2", "2.0")):
        entries = metrics.get(key) or []
        if not entries:
            continue
        preferred = next((entry for entry in entries if entry.get("type") == "Primary"), entries[0])
        data = preferred.get("cvssData", {})
        score = data.get("baseScore")
        if score is not None:
            return float(score), version
    return None, None


def parse_nvd_snapshot(payload: dict) -> list[VulnerabilityUpsert]:
    result = []
    for item in payload.get("vulnerabilities", []):
        cve = item.get("cve", {})
        cve_id = cve.get("id")
        if not cve_id:
            continue
        descriptions = cve.get("descriptions", [])
        description = next((entry.get("value") for entry in descriptions if entry.get("lang") == "en"), None)
        score, cvss_version = _select_cvss(cve.get("metrics", {}))
        result.append(
            VulnerabilityUpsert(
                cve_id=cve_id,
                description=description,
                cvss_score=score,
                cvss_version=cvss_version,
                cvss_published_at=_timestamp(cve.get("published")),
                source="nvd",
                source_version=cve.get("lastModified"),
                source_effective_at=_timestamp(cve.get("lastModified") or cve.get("published")),
                raw_payload=item,
            )
        )
    return result
