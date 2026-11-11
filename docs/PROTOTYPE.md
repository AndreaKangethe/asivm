# ASIVM Prototype Guide

ASIVM is an asset security visibility and machine-learning risk prototype. It collects asset observations, reconciles identifiers to assets, enriches vulnerabilities, calculates demo risk scores, and records anomaly events.

This guide is the operational reference for running the prototype locally, demonstrating the workflow, testing changes, and understanding the boundaries of the implementation.

## What the prototype includes

- Asset creation and listing
- Identifier validity intervals and observation reconciliation
- Simulated lab scans
- NVD, CISA KEV, and FIRST EPSS snapshot parsers
- Vulnerability catalog and effective-dated asset-vulnerability relationships
- Demo risk assessments using CVSS, EPSS, and KEV context
- Demo anomaly events from repeated asset observations
- Anomaly triage
- Frozen model features, bootstrap risk/anomaly models, and inference scheduling
- Versioned v1, v2, and v3 feature contracts
- Historical intelligence snapshots and ingestion audit records
- Shadow model registration, lifecycle audit, and held-out-data validation helpers
- FastAPI documentation at `/docs`
- Browser security operations console for dashboard, findings, assets, scans,
  intelligence, ML registry, and governance navigation

## Prerequisites

For the Docker workflow:

- Docker Engine or Docker Desktop
- Docker Compose v2 (`docker compose`)
- At least two free local ports: `8000` and `8080`

For the native Python workflow:

- Python 3.12+
- A virtual environment
- PostgreSQL for a production-like run, or SQLite for the simple local fallback

## Recommended: run with Docker

From the repository root:

```bash
git clone -b asivm-complete-local https://github.com/AndreaKangethe/asivm.git
cd asivm

docker compose up --build -d
docker compose ps
```

The Compose stack starts PostgreSQL, applies migrations from the backend container, starts the API, and serves the dashboard.

Use `asivm-complete-local` when you want the combined build. It contains the
restored UI and the latest ML/backend implementation from the v3 contract
milestone. The UI is a static responsive console with Dashboard, Findings,
Assets, Scans, Scope, Intelligence, Team, Audit, ML registry visibility,
filters, risk navigation, detail panels, and CSV export.

| Service | Address | Purpose |
| --- | --- | --- |
| Backend API | http://localhost:8000/docs | FastAPI Swagger documentation |
| Dashboard | http://localhost:8080 | Browser demo interface |
| PostgreSQL | internal Docker network | Application database |

Seed the demo asset and vulnerability after the services are healthy:

```bash
docker compose exec backend python scripts/seed.py
```

Useful Docker commands:

```bash
# Follow all service logs
docker compose logs -f

# Check service health
docker compose ps

# Run the backend test suite
docker compose exec backend pytest

# Stop containers but keep the database volume
docker compose down

# Stop containers and remove the demo database volume
docker compose down -v
```

The default prototype API key is `change-me`. Set a different value before starting the stack:

```bash
API_KEY='replace-this-value' docker compose up --build -d
```

If Docker Compose is unavailable, run the API natively and serve the static
frontend separately:

```bash
# Terminal 1
cd backend
DATABASE_URL=sqlite:///./asivm-local.db PYTHONPATH=. \
  .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2
cd frontend
python3 -m http.server 8080 --bind 127.0.0.1
```

## Demonstrate the workflow

1. Start the backend and frontend.
2. Seed the demo asset and vulnerability.
3. Open the dashboard at <http://localhost:8080>.
4. Click **Run demo scan**.
5. Confirm that the asset and vulnerability counts update.
6. Run the scan a second time to create a demo anomaly.
7. Use the findings and assets views to inspect the records returned by the API.
8. Use the API documentation to inspect scans, assessments, and anomalies.

Equivalent API calls:

```bash
curl -H 'X-API-Key: change-me' \
  -X POST http://localhost:8000/scans/run

curl -H 'X-API-Key: change-me' \
  -X POST http://localhost:8000/risk/infer

curl -H 'X-API-Key: change-me' \
  http://localhost:8000/risk/assessments

curl -H 'X-API-Key: change-me' \
  http://localhost:8000/risk/anomalies
```

## Run natively without Docker

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# Seed the demo database
PYTHONPATH=. .venv/bin/python scripts/seed.py

# Start the API
PYTHONPATH=. .venv/bin/uvicorn app.main:app --reload
```

Open http://localhost:8000/docs. Protected endpoints require the `X-API-Key` header. The native fallback uses the database configuration from the environment; see `.env.example`.

Run native tests:

```bash
cd backend
PYTHONPATH=. .venv/bin/pytest
```

Run migrations explicitly when using a PostgreSQL-backed environment:

```bash
cd backend
PYTHONPATH=. .venv/bin/alembic upgrade head
```

## API areas

| Area | Endpoints |
| --- | --- |
| Assets | `POST /assets`, `GET /assets` |
| Scans | `POST /scans/run` and `POST /scans` |
| Vulnerabilities | `POST /vulnerabilities`, `GET /vulnerabilities` |
| Risk | `GET /risk/assessments` |
| Anomalies | `GET /risk/anomalies`, `PATCH /risk/anomalies/{id}/triage` |
| Models | `GET /risk/models`, `POST /risk/infer` |

The interactive OpenAPI reference at `/docs` is the authoritative request and response shape for the running build.

## Public-feed ingestion

The ingestion command imports NVD, CISA KEV, and FIRST EPSS data with retries, NVD pagination, parser validation, provenance, and ingestion audit records. It is intentionally not run during application startup.

Run it from Docker:

```bash
docker compose exec backend python scripts/ingest_vulnerability_feeds.py
```

Run selected feeds only:

```bash
docker compose exec backend python scripts/ingest_vulnerability_feeds.py --skip-nvd
docker compose exec backend python scripts/ingest_vulnerability_feeds.py --skip-kev --skip-epss
```

Run it natively from `backend/`:

```bash
PYTHONPATH=. .venv/bin/python scripts/ingest_vulnerability_feeds.py
```

Feed imports require outbound network access and may take time because NVD is paginated. They update the local database; they do not create assets, analyst labels, incidents, or exploitation outcomes.

## Database migrations

The migration history is split by domain and is applied automatically by the Docker backend before Uvicorn starts:

1. `0001_assets.py` — assets and identifiers
2. `0002_scans.py` — scans and asset observations
3. `0003_vulnerabilities.py` — vulnerability catalog and relationships
4. `0004_ml_registry.py` — model versions and training runs
5. `0005_assessments.py` — risk assessments and anomalies
6. `0006_v3_contract.py` — v3 feature, label, relationship, and model metadata structures
7. `0007_intelligence_history.py` — intelligence snapshots and ingestion audits
8. `0008_lifecycle_audit.py` — model lifecycle and review/audit structures

Check the applied revision:

```bash
docker compose exec backend alembic current
docker compose exec backend alembic history
```

## Tests and validation

Run the complete backend suite:

```bash
docker compose exec backend pytest
```

The tests cover identifier reconciliation, feature-vector ordering, API behavior, NVD/KEV parsing, risk context, the scan-to-inference flow, and real-data contract safeguards.

The pull request contains no fabricated production assets, analyst labels, incidents, or verified exploitation outcomes. Consequently, the v3 training and shadow-model paths require real held-out data before any performance claim or promotion decision is meaningful.

## Troubleshooting

### Port 8000 or 8080 is already in use

Stop the conflicting process or change the host-side port mapping in `docker-compose.yml`, then restart:

```bash
docker compose down
docker compose up --build -d
```

### Backend is restarting

Inspect the backend and database logs:

```bash
docker compose logs backend postgres
```

The backend waits for PostgreSQL health before starting and applies migrations on startup.

### The dashboard is empty

Seed the demo data while the stack is running:

```bash
docker compose exec backend python scripts/seed.py
```

### API requests return 401/403

Send the API key header:

```bash
curl -H 'X-API-Key: change-me' http://localhost:8000/risk/assessments
```

If you configured `API_KEY`, use that value instead.

## Prototype limitations

The collector is simulated, feed parsers consume supplied snapshots, and the
frontend does not invent records for backend features that are not implemented.
The current schema does not yet provide ownership, remediation workflow,
scope authorization, Nmap/Trivy imports, team administration, audit events,
or feed synchronization controls; those screens report the limitation plainly.
Authentication uses a shared API key.
Production authentication, authorization, monitoring, secret management,
high-availability deployment, and large-scale model governance are outside
the prototype scope.
Dashboard integration for every new v3 capability, approved analyst labeling,
asset criticality and exposure evidence, verified outcome sources, scheduled
retraining, and automatic model promotion remain outside the current scope.

Do not present synthetic/demo results as validated real-world model performance.

The frontend is intentionally honest about these boundaries: unsupported
ownership, remediation, scope, Nmap/Trivy import, team, audit, and intelligence
synchronization workflows are shown as unavailable rather than represented by
mock records.
