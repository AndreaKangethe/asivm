# ASIVM Prototype Guide

ASIVM is an asset security visibility and machine-learning risk prototype. It
collects asset observations, reconciles identifiers to assets, enriches
vulnerabilities, calculates demo risk scores, and records anomaly events.

## Prototype capabilities

- Asset creation and listing
- Identifier validity intervals and observation reconciliation
- Simulated lab scans
- NVD, KEV, and EPSS snapshot parsers
- Vulnerability catalog and asset-vulnerability relationships
- Demo risk assessments using CVSS, EPSS, and KEV context
- Demo anomaly events from repeated asset observations
- Anomaly triage
- Feature contract and model-training utilities
- FastAPI documentation at `/docs`
- Browser dashboard for the end-to-end demo flow

## Start locally

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt
PYTHONPATH=. .venv/bin/python scripts/seed.py
PYTHONPATH=. .venv/bin/uvicorn app.main:app --reload
```

Open:

- API documentation: <http://localhost:8000/docs>
- API health is visible through the Swagger interface.

Protected endpoints require the default prototype header:

```text
X-API-Key: change-me
```

Set a different value with `API_KEY` in `.env`.

## Start with Docker

From the repository root:

```bash
docker compose up --build
```

The services are:

| Service | URL |
| --- | --- |
| Backend API | <http://localhost:8000/docs> |
| Frontend dashboard | <http://localhost:8080> |
| PostgreSQL | internal Docker network |

Seed demo data in the running backend container:

```bash
docker compose exec backend python scripts/seed.py
```

## Demonstrate the workflow

1. Start the backend and frontend.
2. Seed the demo asset and vulnerability.
3. Open the dashboard at <http://localhost:8080>.
4. Click **Run demo scan**.
5. Confirm that the asset and vulnerability counts update.
6. Run the scan a second time to create a demo anomaly.
7. Click **Triage** beside the anomaly.
8. Use the API documentation to inspect scans, assessments, and anomalies.

Equivalent API calls:

```bash
curl -H 'X-API-Key: change-me' \
  -X POST http://localhost:8000/scans

curl -H 'X-API-Key: change-me' \
  http://localhost:8000/risk/assessments

curl -H 'X-API-Key: change-me' \
  http://localhost:8000/risk/anomalies
```

## API areas

| Area | Endpoints |
| --- | --- |
| Assets | `POST /assets`, `GET /assets` |
| Scans | `POST /scans` |
| Vulnerabilities | `POST /vulnerabilities`, `GET /vulnerabilities` |
| Risk | `GET /risk/assessments` |
| Anomalies | `GET /risk/anomalies`, `PATCH /risk/anomalies/{id}/triage` |

## Database migrations

The migration history is intentionally split by domain:

1. `0001_assets.py` — assets and identifiers
2. `0002_scans.py` — scans and asset observations
3. `0003_vulnerabilities.py` — vulnerability catalog and relationships
4. `0004_ml_registry.py` — model versions and training runs
5. `0005_assessments.py` — risk assessments and anomalies

Run migrations with:

```bash
cd backend
PYTHONPATH=. .venv/bin/alembic upgrade head
```

## Tests

```bash
cd backend
PYTHONPATH=. .venv/bin/pytest
```

The tests cover:

- Identifier reconciliation after an IP or identifier change
- Stable feature-vector ordering
- Asset API behavior
- NVD/KEV parsing and risk context
- Scan → risk assessment → anomaly flow

## Prototype limitations

The collector is simulated, feed parsers consume supplied snapshots, and the
frontend is intentionally lightweight. Authentication uses a shared API key.
Production authentication, authorization, monitoring, secret management,
high-availability deployment, and large-scale model governance are outside
the prototype scope.
