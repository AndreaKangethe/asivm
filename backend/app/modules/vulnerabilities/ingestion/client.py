import csv
import io
import time
from collections.abc import Callable, Iterable
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.modules.vulnerabilities.models import VulnerabilityIngestionRun
from app.modules.vulnerabilities.schemas import VulnerabilityUpsert
from app.modules.vulnerabilities.service import upsert_vulnerability


def fetch_url(url: str, *, timeout: float = 30.0, retries: int = 3, retry_delay: float = 1.0) -> httpx.Response:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                return response
        except (httpx.HTTPError, OSError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(retry_delay * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url} after {retries} attempts") from last_error


def ingest_records(
    db: Session,
    source: str,
    records: Iterable[VulnerabilityUpsert],
    source_version: str | None = None,
) -> VulnerabilityIngestionRun:
    run = VulnerabilityIngestionRun(source=source, source_version=source_version, status="running")
    db.add(run)
    db.commit()
    imported = 0
    seen = 0
    try:
        for record in records:
            seen += 1
            upsert_vulnerability(db, record)
            imported += 1
        run.records_seen = seen
        run.records_imported = imported
        run.status = "completed"
        run.completed_at = datetime.utcnow()
        db.commit()
    except Exception as exc:
        run.records_seen = seen
        run.records_imported = imported
        run.status = "failed"
        run.error = str(exc)
        run.completed_at = datetime.utcnow()
        db.commit()
        raise
    return run


def parse_epss_response(response: httpx.Response) -> list[dict[str, str]]:
    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        payload = response.json()
        return [dict(row) for row in payload.get("data", [])]
    return list(csv.DictReader(io.StringIO(response.text)))
