from app.modules.vulnerabilities.schemas import VulnerabilityUpsert


def parse_nvd_snapshot(payload: dict) -> list[VulnerabilityUpsert]:
    result = []
    for item in payload.get("vulnerabilities", []):
        cve = item.get("cve", {})
        cve_id = cve.get("id")
        if not cve_id:
            continue
        descriptions = cve.get("descriptions", [])
        description = next((entry["value"] for entry in descriptions if entry.get("lang") == "en"), None)
        metrics = cve.get("metrics", {}).get("cvssMetricV31", [])
        score = metrics[0].get("cvssData", {}).get("baseScore") if metrics else None
        result.append(VulnerabilityUpsert(cve_id=cve_id, description=description, cvss_score=score))
    return result
