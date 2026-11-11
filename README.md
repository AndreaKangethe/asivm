# ASIVM

Asset security visibility and machine-learning risk platform.

ASIVM is currently a demonstrable prototype for asset inventory, vulnerability intelligence, risk assessment, anomaly triage, and model-governance foundations. It preserves the existing v1/v2 behavior while adding v3 real-data migration infrastructure without fabricating production labels or outcomes.

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

The default prototype API key is `change-me`.

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

See [docs/PROTOTYPE.md](docs/PROTOTYPE.md) for:

- Docker and native setup
- Demo workflow and API examples
- Public-feed ingestion
- Database migrations 0001–0008
- Tests and troubleshooting
- Prototype scope and limitations

## Important scope note

This is not production-ready software. Public-feed ingestion, approved analyst labels, asset criticality and exposure evidence, verified outcomes, production authentication, monitoring, scheduled retraining, and automatic model promotion still require additional implementation and validation.
