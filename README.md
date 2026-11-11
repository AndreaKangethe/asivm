# ASIVM

Asset security visibility and machine-learning risk platform.

ASIVM connects asset identity, vulnerability intelligence, risk assessment, anomaly triage, and model governance in one traceable workflow. It helps security teams prioritize which assets need attention first and understand the evidence behind each decision.

## Quick start with Docker

```bash
git clone -b asivm-complete-local https://github.com/AndreaKangethe/asivm.git
cd asivm

docker compose up --build -d
docker compose exec backend python scripts/seed.py
```

Open:

- Dashboard: http://localhost:8080
- API documentation: http://localhost:8000/docs

The default API key for the local walkthrough is `change-me`.

The `asivm-complete-local` branch is the combined runnable build: it contains
the restored security operations UI and the latest ML/backend implementation.
The UI includes Dashboard, Findings, Assets, Scans, Intelligence, Scope, Team,
Audit, ML registry visibility, filtering, risk navigation, and CSV export.

Check the stack and logs:

```bash
docker compose ps
docker compose logs -f
```

Stop it with:

```bash
docker compose down
```

## Tests

```bash
docker compose exec backend pytest
```

For a native frontend-only server, run `python3 -m http.server 8080` from
`frontend/` after starting the API on port `8000`.

## Documentation

- [Judge presentation brief](docs/JUDGES_PRESENTATION.md) — product story, demo script, value proposition, and scope note
- [Operations guide](docs/PROTOTYPE.md) — Docker/native setup, API examples, ingestion, migrations, tests, and troubleshooting

## Scope note

The local walkthrough uses controlled demo data. The UI displays unavailable
backend capabilities explicitly instead of fabricating ownership, remediation,
scope, team, audit, or synchronization records. Production deployment still
requires approved analyst labels, asset criticality and exposure evidence,
verified outcomes, production authentication, monitoring, scheduled retraining,
and controlled model promotion.
