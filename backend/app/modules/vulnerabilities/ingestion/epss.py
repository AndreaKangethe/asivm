from datetime import datetime

from app.modules.vulnerabilities.schemas import VulnerabilityUpsert


def _date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value).replace(tzinfo=None)


def parse_epss_csv(rows: list[dict[str, str]]) -> list[VulnerabilityUpsert]:
    result = []
    for row in rows:
        cve_id = row.get("cve")
        score = row.get("epss")
        if not cve_id or score is None or score == "":
            continue
        result.append(
            VulnerabilityUpsert(
                cve_id=cve_id,
                epss_score=float(score),
                epss_percentile=float(row["percentile"]) if row.get("percentile") not in (None, "") else None,
                epss_score_date=_date(row.get("date")),
                source="first_epss",
                source_version=row.get("model_version"),
                source_effective_at=_date(row.get("date")),
                raw_payload=row,
            )
        )
    return result
