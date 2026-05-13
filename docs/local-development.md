# Local Development

Careero Layer 1 runs locally with a FastAPI backend and a React + Vite frontend.

## Root Commands

Run these from the repository root:

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
.\scripts\migrate.ps1
.\scripts\seed.ps1
.\scripts\test.ps1
.\scripts\check-local.ps1
```

If PowerShell blocks local scripts, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-local.ps1
```

## Readiness Checklist

1. PostgreSQL is running.
2. `backend/.env` has working `CAREERO_DATABASE_URL` and `CAREERO_TEST_DATABASE_URL` values.
3. Backend dependencies are installed.
4. Frontend dependencies are installed.
5. Migrations are applied with `.\scripts\migrate.ps1`.
6. Local data is seeded with `.\scripts\seed.ps1`.
7. Backend and frontend are running.
8. `.\scripts\check-local.ps1` passes.
9. Manual role intake works at `http://127.0.0.1:5173/roles/new`.

If database health fails, fix PostgreSQL credentials or update `backend/.env`, then rerun migrations and seed.

## Backend

Create PostgreSQL databases for local development and tests:

```sql
CREATE ROLE careero WITH LOGIN PASSWORD 'careero';
CREATE DATABASE careero OWNER careero;
CREATE DATABASE careero_test OWNER careero;
```

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Edit `backend/.env` so `CAREERO_DATABASE_URL` and `CAREERO_TEST_DATABASE_URL` point at your local PostgreSQL databases.
Run `python -m app.seed` after migrations so the default local user and canonical manual job sources are available for role intake.

OpenAI STRIDE enrichment is optional and disabled by default. Deterministic STRIDE scoring works without an API key. To enable AI enrichment locally, set these in `backend/.env`:

```dotenv
CAREERO_ENABLE_AI_EVALUATIONS=true
CAREERO_OPENAI_API_KEY=sk-...
CAREERO_OPENAI_DEFAULT_EVALUATION_MODEL=gpt-5-mini
CAREERO_OPENAI_TIMEOUT_SECONDS=30
CAREERO_OPENAI_MAX_OUTPUT_TOKENS=2500
```

Do not commit real API keys. If AI is disabled, missing, times out, or returns invalid structured output, role evaluation falls back to the deterministic baseline and records `ai_status` in `raw_evaluation_json`.

Health check:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/database
```

Manual role intake API:

```text
POST   http://127.0.0.1:8000/api/roles
GET    http://127.0.0.1:8000/api/roles
GET    http://127.0.0.1:8000/api/roles/{role_id}
PATCH  http://127.0.0.1:8000/api/roles/{role_id}
DELETE http://127.0.0.1:8000/api/roles/{role_id}
```

LinkedIn roles are manually pasted into the API. Careero does not scrape LinkedIn or poll job boards in Layer 1.

Run tests:

```powershell
$env:CAREERO_TEST_DATABASE_URL="postgresql://careero:careero@localhost:5432/careero_test"
pytest
```

## Frontend

From the repository root:

```powershell
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `http://127.0.0.1:8000`, so start the backend first for role intake.

Manual role intake:

```text
http://127.0.0.1:5173/roles/new
```

Run frontend tests:

```powershell
npm run test
```

Build validation:

```powershell
npm run build
```

Preview a production build:

```powershell
npm run preview
```

If PowerShell blocks `npm.ps1`, run the same commands with `npm.cmd`, for example:

```powershell
npm.cmd install
npm.cmd run build
```

## Current Boundaries

Layer 1 is local-first only. It does not include authentication, tenants, workspaces, billing, cloud deployment, background job execution, or automated application submission.

## Layer 1 Completion

Layer 1 is considered locally stable when the backend, frontend, and PostgreSQL all pass readiness checks and the role workflow can create, list, view, update, and archive records.
