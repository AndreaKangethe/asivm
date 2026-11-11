# asivm
Asset security visibility and machine-learning risk platform

See [docs/PROTOTYPE.md](docs/PROTOTYPE.md) for setup instructions, API
examples, the demo workflow, migrations, tests, and prototype limitations.

## Run locally

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt
PYTHONPATH=. .venv/bin/uvicorn app.main:app --reload
```

Protected endpoints require `X-API-Key`; configure `API_KEY` in `.env`.

## Run with Docker

```bash
docker compose up --build
```

The API is available at `http://localhost:8000` and the dashboard at
`http://localhost:8080`.

## Tests

```bash
cd backend
PYTHONPATH=. .venv/bin/pytest
```
