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
9. Manual opportunity intake works at `http://127.0.0.1:5173/opportunities/new`.

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
CAREERO_MAX_AI_EVALUATIONS_PER_SESSION=25
```

AI opportunity parsing is separately controlled. To enable the Add opportunity parser, set:

```dotenv
CAREERO_ENABLE_AI_ROLE_PARSING=true
CAREERO_OPENAI_DEFAULT_ROLE_PARSING_MODEL=gpt-5-mini
```

Do not commit real API keys. If AI is disabled, missing, times out, or returns invalid structured output, role evaluation falls back to the deterministic baseline and records `ai_status` in `raw_evaluation_json`.

STRIDE evaluations are cached by an input hash built from role content, active resume/profile source content, request notes/context, prompt version, ruleset version, AI enabled state, and model name. Reposting the same inputs returns the cached completed evaluation with HTTP `200`; send `"force": true` to create a new evaluation. The backend stores model, prompt/ruleset versions, token estimates when available, latency, AI status, sanitized errors, and content hashes for auditability.

`CAREERO_MAX_AI_EVALUATIONS_PER_SESSION` limits OpenAI-backed attempts per backend process and resets on backend restart. Cached evaluations and AI-disabled or missing-key skipped runs do not consume the counter. Logs should include IDs/status/latency only, not prompts, API keys, raw role descriptions, or resume/profile source text.

Health check:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/database
```

Manual opportunity intake API:

```text
POST   http://127.0.0.1:8000/api/opportunities
POST   http://127.0.0.1:8000/api/opportunities/parse
GET    http://127.0.0.1:8000/api/opportunities
GET    http://127.0.0.1:8000/api/opportunities/{opportunity_id}
PATCH  http://127.0.0.1:8000/api/opportunities/{opportunity_id}
DELETE http://127.0.0.1:8000/api/opportunities/{opportunity_id}
```

The older `/api/roles` endpoints remain available as compatibility aliases. LinkedIn opportunities are manually pasted into the API. Careero does not scrape LinkedIn or poll job boards in Layer 2.

The AI parse endpoint accepts `rawText`, optional `source`, and optional `jobUrl`, then returns structured fields for review. It does not save data. The Add Opportunity UI fills empty fields only and requires the user to click `Create opportunity`. Parsing failures do not clear manually entered content.

Resume/profile source API:

```text
POST http://127.0.0.1:8000/api/resume-sources
POST http://127.0.0.1:8000/api/resume-sources/import
GET  http://127.0.0.1:8000/api/resume-sources
GET  http://127.0.0.1:8000/api/resume-sources/active
PATCH http://127.0.0.1:8000/api/resume-sources/{source_id}
POST http://127.0.0.1:8000/api/resume-sources/{source_id}/versions
POST http://127.0.0.1:8000/api/resume-sources/{source_id}/versions/{version_id}/activate
```

Create an active local master resume/profile source by manually pasting text:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/resume-sources `
  -ContentType "application/json" `
  -Body '{
    "name": "Master Resume",
    "source_type": "master_resume",
    "version_label": "v1",
    "raw_text": "Paste the master resume or profile text here.",
    "normalized_summary": "Optional concise summary.",
    "is_active": true
  }'
```

You can also import local `.txt`, `.md`, `.docx`, and text-based `.pdf` files from the Settings page or with `POST /api/resume-sources/import`. Imports are limited to `5 MB`, extract text for preview only, and do not save uploaded files or create sources. The extracted text remains editable before saving. PDFs must contain embedded selectable text; OCR for scanned PDFs is not included.

Only one source version is active for the default local user. STRIDE evaluations run without an active source, but OpenAI enrichment includes the active source when present and must identify gaps rather than inventing experience. Resume and cover letter artifact generation can also use the active source when enabled. This source API does not extract profile facts or import external profiles.

Future Google Docs import is tracked as a backlog item and requires Google OAuth, Drive/Docs scopes, document export, token handling, permission review, and a security design.

STRIDE evaluation flow:

```text
POST http://127.0.0.1:8000/api/roles/{role_id}/evaluations
GET  http://127.0.0.1:8000/api/roles/{role_id}/evaluations/latest
GET  http://127.0.0.1:8000/api/stride-evaluations
GET  http://127.0.0.1:8000/api/activity-log?entity_type=stride_evaluation&entity_id={evaluation_id}
```

Posting the same opportunity/source/context inputs reuses a cached completed evaluation. Send `"force": true` to create a new run. Evaluation activity entries include `stride_evaluation.started`, `stride_evaluation.completed`, `stride_evaluation.failed`, and `stride_evaluation.cached_result_reused`.

Manual browser smoke flow:

1. Open `http://127.0.0.1:5173/opportunities/new` and create an opportunity.
2. Open `http://127.0.0.1:5173/settings` and create an active resume/profile source.
3. Open the opportunity detail page and run STRIDE evaluation.
4. Confirm the evaluation shows score, recommendation, confidence, alignments, keyword gaps, and AI fallback/enrichment status.
5. Re-run the evaluation and confirm a forced new run succeeds.

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

The Vite dev server proxies `/api` requests to `http://127.0.0.1:8000`, so start the backend first for opportunity intake.

Manual opportunity intake:

```text
http://127.0.0.1:5173/opportunities/new
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

## Canonical Contracts

The executable platform contracts live in `packages/contracts`. They are additive and do not change current backend or frontend runtime behavior.

```powershell
cd packages/contracts
npm install
npm run validate
```

`npm run validate` builds the TypeScript package, generates JSON Schema files under `generated/json-schema/`, and runs the contract tests. See `docs/canonical-domain-model.md` for entity responsibilities, AI orchestration boundaries, versioning, and migration guidance.

## Current Boundaries

Layer 2 is local-first and evaluation-focused only. Later layers add workspace-aware artifact generation, but the app still does not include authentication, tenants, frontend workspace switching, billing, cloud deployment, automated discovery, application packets, or automated application submission.

## Layer 2 Completion

Layer 2 is considered locally stable when the backend, frontend, and PostgreSQL all pass readiness checks and the role-to-resume-to-STRIDE workflow can create, display, cache, force re-run, and audit evaluations.
