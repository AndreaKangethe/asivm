# ASIVM

Asset security visibility and machine-learning risk platform.

ASIVM connects asset identity, vulnerability intelligence, risk assessment, anomaly triage, and model governance in one traceable workflow. It helps security teams prioritize which assets need attention first and understand the evidence behind each decision.

## Quick start with Docker

```bash
git clone https://github.com/AndreaKangethe/asivm.git
cd asivm

git fetch origin pull/2/head:pr-2
git switch pr-2

docker compose up --build -d
docker compose exec backend python scripts/seed.py
```

Open:

- Dashboard: http://localhost:8080
- API documentation: http://localhost:8000/docs

The default API key for the local walkthrough is `change-me`.

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

## Documentation

- [Judge presentation brief](docs/JUDGES_PRESENTATION.md) — product story, demo script, value proposition, and scope note
- [Operations guide](docs/PROTOTYPE.md) — Docker/native setup, API examples, ingestion, migrations, tests, and troubleshooting

## Scope note

The local walkthrough uses controlled demo data. Production deployment still requires approved analyst labels, asset criticality and exposure evidence, verified outcomes, production authentication, monitoring, scheduled retraining, and controlled model promotion.
