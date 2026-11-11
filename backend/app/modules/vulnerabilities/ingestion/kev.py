from app.modules.vulnerabilities.schemas import VulnerabilityUpsert


def parse_kev_snapshot(payload: dict) -> list[VulnerabilityUpsert]:
    return [
        VulnerabilityUpsert(
            cve_id=item["cveID"],
            description=item.get("shortDescription"),
            is_kev=True,
        )
        for item in payload.get("vulnerabilities", [])
        if item.get("cveID")
    ]
