# Backend

The backend is a local FastAPI application for Careero Layer 1.

## PostgreSQL

Create local development and test databases before running migrations. One simple local setup is:

```sql
CREATE ROLE careero WITH LOGIN PASSWORD 'careero';
CREATE DATABASE careero OWNER careero;
CREATE DATABASE careero_test OWNER careero;
```

If PostgreSQL is installed on Windows but `psql` is not on your `PATH`, run it from the PostgreSQL `bin` directory for your installed version.

## Setup

Run from this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edit `.env` for your local machine. The default values are:

```dotenv
CAREERO_APP_NAME=Careero API
CAREERO_ENVIRONMENT=local
CAREERO_DATABASE_URL=postgresql://careero:careero@localhost:5432/careero
CAREERO_TEST_DATABASE_URL=postgresql://careero:careero@localhost:5432/careero_test
CAREERO_OPENAI_API_KEY=
CAREERO_LOG_LEVEL=INFO
```

`CAREERO_OPENAI_API_KEY` is intentionally empty in local setup. Do not commit real secrets.

## Migrate and Seed

Run migrations:

```powershell
python -m alembic upgrade head
```

Seed the default local user:

```powershell
python -m app.seed
```

The seed command is idempotent. It creates or updates `local-user@careero.local` and the canonical job sources: `manual`, `linkedin_manual`, `greenhouse`, `lever`, `ashby`, `workable`, and `other`.

## Run

```powershell
uvicorn app.main:app --reload
```

Health checks:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/database
```

`/health/database` connects to the PostgreSQL database configured by `CAREERO_DATABASE_URL` and runs a lightweight probe.

## Role Intake API

Role intake is manual-only in this phase. Paste role details discovered from LinkedIn or another source into Careero; the backend does not scrape LinkedIn, poll job boards, call OpenAI, or score STRIDE.

Create a role from a LinkedIn manual paste:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/roles `
  -ContentType "application/json" `
  -Body '{
    "title": "Senior Backend Engineer",
    "company": {
      "name": "Example Company",
      "website_url": "https://example.com"
    },
    "source": {
      "source_type": "linkedin_manual"
    },
    "job_url": "https://www.linkedin.com/jobs/view/example",
    "location": "Chicago, IL",
    "remote_type": "hybrid",
    "compensation_min": "120000.00",
    "compensation_max": "150000.00",
    "compensation_currency": "USD",
    "raw_description": "Paste the original job description here.",
    "normalized_description": null,
    "status": "found",
    "date_found": "2026-05-13",
    "date_posted": "2026-05-01"
  }'
```

List active roles:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/roles
```

Update a role:

```powershell
Invoke-RestMethod `
  -Method Patch `
  -Uri http://127.0.0.1:8000/api/roles/{role_id} `
  -ContentType "application/json" `
  -Body '{ "status": "interested", "remote_type": "remote" }'
```

Archive a role:

```powershell
Invoke-RestMethod -Method Delete http://127.0.0.1:8000/api/roles/{role_id}
```

Company intake accepts either an existing company ID or a name. When a name is supplied, Careero reuses an existing company for the default local user using case-insensitive name matching or creates a new company if one does not exist.

## STRIDE Evaluation API

STRIDE evaluation support is a backend foundation only in this phase. The API creates deterministic placeholder records so the data model, service boundary, and route shape are ready for the later evaluator. It does not call OpenAI, score roles, infer resume facts, generate resumes or cover letters, scrape jobs, or poll sources.

Create a placeholder evaluation for a role:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/roles/{role_id}/evaluations `
  -ContentType "application/json" `
  -Body '{
    "user_notes": "Evaluate this role once the real STRIDE engine is connected.",
    "user_context": {
      "priority": "medium"
    }
  }'
```

Get the latest evaluation for a role:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/roles/{role_id}/evaluations/latest
```

List evaluations:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/stride-evaluations
Invoke-RestMethod "http://127.0.0.1:8000/api/stride-evaluations?evaluation_status=completed"
```

Get one evaluation by ID:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/stride-evaluations/{evaluation_id}
```

Placeholder evaluations currently return `evaluation_status` as `completed` while `overall_score`, `recommendation`, and `confidence_level` remain empty. Alignment, risk, and keyword fields are stored as structured JSON so future AI-generated output can fit without changing callers.

## Test

Run tests:

```powershell
$env:CAREERO_TEST_DATABASE_URL="postgresql://careero:careero@localhost:5432/careero_test"
pytest
```

Database-backed tests run Alembic migrations against `CAREERO_TEST_DATABASE_URL` and reset the known Careero schema in that test database.
