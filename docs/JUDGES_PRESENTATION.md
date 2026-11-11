# ASIVM — Judge Presentation Brief

## 30-second pitch

ASIVM is an asset security visibility and machine-learning risk platform prototype. It connects asset observations with vulnerability intelligence, produces explainable demo risk assessments, and records anomaly and model-governance events in a traceable way.

The prototype demonstrates the foundation for moving from isolated vulnerability lists to prioritized, evidence-based asset risk—while deliberately avoiding fabricated production labels, incidents, or model-performance claims.

## The problem

Security teams often have three disconnected views:

1. An inventory of assets and identifiers.
2. Vulnerability findings from scans and public intelligence feeds.
3. Risk decisions and analyst follow-up captured somewhere else.

This makes it difficult to answer: **Which asset should we investigate first, why, and what evidence supports that decision?**

## The solution

ASIVM provides one workflow for:

- Reconciling changing asset identifiers over time.
- Connecting assets to vulnerability records.
- Enriching vulnerabilities with NVD, CISA KEV, and FIRST EPSS intelligence.
- Calculating transparent prototype risk assessments.
- Detecting repeated-observation anomalies.
- Recording triage, provenance, historical snapshots, and model lifecycle events.
- Preserving feature-contract and audit foundations for future real-data training.

## What is technically demonstrated

- FastAPI backend with interactive OpenAPI documentation.
- PostgreSQL-backed Docker Compose environment.
- Eight Alembic migration revisions covering assets, scans, vulnerabilities, ML registry, assessments, v3 contracts, intelligence history, and lifecycle audit.
- Idempotent, provenance-aware public-feed ingestion with NVD pagination and retry handling.
- Versioned v1/v2/v3 feature contracts.
- Dataset validation safeguards for duplicates, timestamps, asset grouping, and leakage.
- Held-out-data-required multiclass candidate evaluation.
- Shadow model registration and explicit lifecycle audit controls.
- Lightweight browser dashboard for the end-to-end demo flow.

## Live demo script (5–7 minutes)

### 1. Start the stack

From the repository root:

```bash
docker compose up --build -d
docker compose ps
docker compose exec backend python scripts/seed.py
```

Open:

- Dashboard: http://localhost:8080
- API documentation: http://localhost:8000/docs

### 2. Show the initial state

Point out the seeded asset and vulnerability. Explain that the seed data is intentionally labeled as demo data so the audience can distinguish the working workflow from future production-data integration.

### 3. Run a scan

Click **Run demo scan** in the dashboard, or run:

```bash
curl -H 'X-API-Key: change-me' \
  -X POST http://localhost:8000/scans/run
```

Explain that the prototype records the observation and reconciles it to the asset model rather than treating every observation as a new asset.

### 4. Generate risk and inspect evidence

Run inference and open the assessments view:

```bash
curl -H 'X-API-Key: change-me' \
  -X POST http://localhost:8000/risk/infer

curl -H 'X-API-Key: change-me' \
  http://localhost:8000/risk/assessments
```

Emphasize that the risk result is explainable prototype output based on recorded vulnerability context—not a claim of validated production model accuracy.

### 5. Create and triage an anomaly

Run the scan a second time. The repeated observation creates a demo anomaly. Use **Triage** in the dashboard, or inspect anomalies through:

```bash
curl -H 'X-API-Key: change-me' \
  http://localhost:8000/risk/anomalies
```

Explain that the workflow preserves the event, review status, reviewer, and optional note for later auditability.

### 6. Close with the migration foundation

Show the repository documentation and explain that the system is ready for approved real-data onboarding: intelligence snapshots, provenance, effective-dated relationships, feature contracts, dataset validation, and shadow model controls are already represented.

## Suggested narration

> “The key design choice is traceability. ASIVM does not jump from a vulnerability score to an unsupported business decision. It keeps the asset identity, vulnerability evidence, intelligence provenance, timestamps, review information, and model lifecycle state visible so the future production system can be evaluated and governed.”

> “This is a working prototype, not a claim that the final model is production-ready. We intentionally did not invent analyst labels, incidents, asset criticality, exposure evidence, or exploitation outcomes. That makes the next validation steps explicit rather than hiding them behind synthetic metrics.”

## What to claim

- The Dockerized prototype runs locally.
- The API, database migrations, dashboard, seed workflow, tests, and demo scan flow are implemented.
- Public intelligence parsers and ingestion infrastructure are implemented.
- Provenance, historical snapshots, feature contracts, validation safeguards, and shadow lifecycle controls are implemented.
- The architecture is prepared for approved real-data onboarding and governed model evaluation.

## What not to claim

- Do not claim production readiness.
- Do not claim validated real-world model accuracy.
- Do not claim that demo assets or labels represent customer data.
- Do not claim automatic model promotion or fully automated retraining.
- Do not claim that public feeds alone provide business impact, asset criticality, exposure, or exploitation outcome labels.

## Honest limitations and next milestones

The next required inputs are:

1. An approved analyst risk-label rubric and reviewed labels.
2. Asset criticality, business impact, and exposure evidence.
3. Independently verified exploitation or incident outcomes.
4. Local and CI execution of migration, integration, and live-feed checks.
5. Dashboard wiring for the newer v3 governance capabilities.
6. Scheduled retraining, monitoring, production authentication, and controlled promotion workflows.

## Backup commands

```bash
# View service status
docker compose ps

# View logs
docker compose logs --tail=100 backend postgres frontend

# Run tests
docker compose exec backend pytest

# Check database migration state
docker compose exec backend alembic current

# Stop the demo
docker compose down
```

## Final closing statement

> “ASIVM turns asset and vulnerability data into a traceable risk workflow. The prototype proves the end-to-end interaction and establishes the governance needed to add real labels and outcomes responsibly. The next phase is validation with approved evidence—not pretending that synthetic data is production truth.”
