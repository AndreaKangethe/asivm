# ASIVM — Judge Presentation Brief

## 30-second pitch

ASIVM is an asset security visibility and machine-learning risk platform that helps security teams move from disconnected vulnerability findings to prioritized, evidence-based action. It connects asset identity, vulnerability intelligence, risk assessment, anomaly detection, and governance in one traceable workflow.

## The goal—and what ASIVM achieved

**Goal:** Build a credible, governed foundation for combining asset context, vulnerability intelligence, and machine-learning risk decisions without inventing evidence or hiding uncertainty.

**Achieved outcome:** ASIVM now delivers an end-to-end platform foundation that:

- Preserves the existing v1/v2 workflows while introducing a versioned v3 feature contract.
- Models the full path from asset identity and observations to vulnerability relationships and risk review.
- Imports NVD, CISA KEV, and FIRST EPSS intelligence with pagination, retries, provenance, historical snapshots, and ingestion audits.
- Maintains effective-dated asset-vulnerability relationships so historical state can be reconstructed.
- Provides validated dataset-building safeguards for duplicates, timestamps, asset grouping, and leakage.
- Supports multiclass candidate evaluation that requires held-out data before performance is accepted.
- Provides shadow model registration, promotion controls, retirement paths, and lifecycle audit events.
- Separates risk-review labels and independently verified exploitation outcomes instead of treating public severity scores as business truth.
- Runs locally as a Dockerized API, PostgreSQL database, and browser dashboard with migrations, seed data, tests, and interactive API documentation.

The result is not just a screen or a scoring formula. It is a traceable, extensible foundation for responsible asset-risk prioritization and future real-data model validation.

## The problem

Security teams often have three disconnected views:

1. An inventory of assets and identifiers.
2. Vulnerability findings from scans and public intelligence feeds.
3. Risk decisions and analyst follow-up captured somewhere else.

This makes it difficult to answer: **Which asset should we investigate first, why, and what evidence supports that decision?**

## The ASIVM solution

ASIVM creates a continuous path from observation to action:

- Reconcile changing asset identifiers over time.
- Connect assets to vulnerability records.
- Enrich vulnerabilities with NVD, CISA KEV, and FIRST EPSS intelligence.
- Produce transparent risk assessments with visible evidence.
- Detect repeated-observation anomalies.
- Capture triage, provenance, historical snapshots, and model lifecycle events.
- Preserve the contracts and audit controls needed for governed machine-learning improvement.

## Why it is different

**Traceability:** Every important decision can be connected back to an asset, observation, vulnerability, intelligence source, timestamp, review event, or model version.

**Prioritization:** The platform is designed to help teams focus on the assets and vulnerabilities that deserve attention first, rather than treating every finding as equal.

**Governance by design:** The data contracts, provenance records, held-out evaluation requirement, shadow registration, and lifecycle audit prevent unsupported model decisions from silently reaching users.

**Extensible foundation:** The platform preserves existing workflows while providing a structured path to richer business-impact, exposure, analyst-label, and verified-outcome data.

## What the current build demonstrates

- FastAPI backend with interactive OpenAPI documentation.
- PostgreSQL-backed Docker Compose environment.
- Eight Alembic migration revisions covering assets, scans, vulnerabilities, ML registry, assessments, v3 contracts, intelligence history, and lifecycle audit.
- Idempotent, provenance-aware public-feed ingestion with NVD pagination and retry handling.
- Versioned v1/v2/v3 feature contracts.
- Dataset validation safeguards for duplicates, timestamps, asset grouping, and leakage.
- Held-out-data-required multiclass candidate evaluation.
- Shadow model registration and explicit lifecycle audit controls.
- Lightweight browser dashboard for the end-to-end workflow.

## Live demo script (5–7 minutes)

### 1. Start the platform

From the repository root:

```bash
docker compose up --build -d
docker compose ps
docker compose exec backend python scripts/seed.py
```

Open:

- Dashboard: http://localhost:8080
- API documentation: http://localhost:8000/docs

### 2. Show the starting view

Point out the seeded asset and vulnerability. Explain that this gives the audience a controlled, repeatable environment for seeing the workflow end to end.

### 3. Run an observation

Click **Run demo scan** in the dashboard, or run:

```bash
curl -H 'X-API-Key: change-me' \
  -X POST http://localhost:8000/scans/run
```

Explain that ASIVM records the observation and reconciles it to the asset model rather than treating every observation as a new asset.

### 4. Generate risk and inspect evidence

Run inference and open the assessments view:

```bash
curl -H 'X-API-Key: change-me' \
  -X POST http://localhost:8000/risk/infer

curl -H 'X-API-Key: change-me' \
  http://localhost:8000/risk/assessments
```

Highlight the evidence behind the assessment and the ability to inspect the result through the API.

### 5. Create and triage an anomaly

Run the scan a second time. The repeated observation creates an anomaly. Use **Triage** in the dashboard, or inspect anomalies through:

```bash
curl -H 'X-API-Key: change-me' \
  http://localhost:8000/risk/anomalies
```

Explain that the workflow preserves the event, review status, reviewer, and optional note for later auditability.

### 6. Close with the platform foundation

Show the repository documentation and explain that ASIVM already represents intelligence snapshots, provenance, effective-dated relationships, feature contracts, dataset validation, and controlled model lifecycle events.

## Suggested narration

> “Our goal was to build more than a vulnerability list. We built a traceable asset-risk platform that connects identity, evidence, intelligence, prioritization, review, and governance.”

> “The achieved outcome is a working foundation for responsible real-data migration. It preserves current workflows, adds the contracts and auditability required for future machine learning, and makes the remaining evidence requirements explicit rather than hiding them behind synthetic metrics.”

> “ASIVM is designed around one question: which asset deserves attention first, and can we explain why? The platform connects asset identity, vulnerability evidence, intelligence context, risk assessment, anomaly review, and model governance so security decisions are more focused and more defensible.”

## Strong, accurate claims

- ASIVM unifies asset, vulnerability, risk, anomaly, and governance workflows.
- The Dockerized platform runs locally with an API, database, and dashboard.
- Public intelligence parsers and ingestion infrastructure are implemented.
- Provenance, historical snapshots, feature contracts, validation safeguards, and shadow lifecycle controls are implemented.
- The architecture is prepared for approved real-data onboarding and governed model evaluation.

## Scope note

The current build uses controlled demo data for the repeatable walkthrough. Production deployment still requires approved analyst labels, asset criticality and exposure evidence, verified outcomes, production authentication, monitoring, scheduled retraining, and controlled model promotion. Those are clearly defined next steps—not hidden assumptions.

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

## Closing statement

> “ASIVM turns asset and vulnerability data into a traceable risk workflow. We achieved the core goal: a working, governed foundation that helps teams prioritize attention, understand the evidence behind decisions, and create a responsible path toward stronger organizational intelligence.”
