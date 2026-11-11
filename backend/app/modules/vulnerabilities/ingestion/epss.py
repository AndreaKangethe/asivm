from app.modules.vulnerabilities.schemas import VulnerabilityUpsert


def parse_epss_csv(rows: list[dict[str, str]]) -> list[VulnerabilityUpsert]:
    return [
        VulnerabilityUpsert(cve_id=row["cve"], epss_score=float(row["epss"]))
        for row in rows
        if row.get("cve") and row.get("epss")
    ]
