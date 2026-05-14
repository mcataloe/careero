# Careero

Careero is a local-first career operations application for managing a personal job search and preparing strong applications. It is designed around a STRIDE-powered workflow for evaluating role fit, risk, positioning, and application priority.

Layer 2 completes the local STRIDE evaluation loop: manual role intake, resume/profile grounding, deterministic scoring, optional OpenAI enrichment, audit metadata, cache reuse, and frontend review.

## Current Layer Includes

- Local FastAPI backend with a health check endpoint.
- Local PostgreSQL persistence with Alembic migrations.
- Local React + Vite frontend for manual role intake.
- Manual create, list, view, update, and archive role workflow.
- Optional AI-assisted role parsing for pasted job posts, with user review before save.
- Local resume/profile source storage for STRIDE grounding, with paste or local file import.
- Deterministic STRIDE scoring for stored roles.
- Optional OpenAI STRIDE enrichment grounded in stored role and active resume/profile source data.
- Evaluation caching, prompt/ruleset versioning, audit metadata, and activity-log inspection.
- Backend integration tests for the full Layer 2 flow when PostgreSQL is configured.
- Frontend component tests and production build validation.
- Local development documentation.
- Reserved directories for future modular growth.

## Out of Scope

Careero does not yet include:

- Authentication.
- Tenant behavior, workspace persistence/runtime switching, or multi-user behavior.
- Billing or subscriptions.
- AWS or other cloud deployment logic.
- Background job execution.
- Automated source discovery or polling.
- Automated job application submission.
- Tailored resume or cover letter generation.

## Repository Structure

```text
backend/   FastAPI application and backend tests
frontend/  React + Vite + TypeScript application
workers/   Reserved for future local worker processes
shared/    Reserved for future shared schemas and utilities
packages/  Standalone shared packages, including canonical contracts
docs/      Project and local development documentation
infra/     Reserved for future infrastructure notes and config
scripts/   Reserved for future developer automation
```

## Requirements

- Python 3.11+
- Node.js 20+
- npm
- PostgreSQL

On Windows PowerShell, if `npm` is blocked by script execution policy, use `npm.cmd` in the commands below.

## Developer Commands

Run these from the repository root:

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
.\scripts\migrate.ps1
.\scripts\seed.ps1
.\scripts\test.ps1
.\scripts\check-local.ps1
```

If PowerShell blocks local scripts, run them with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-local.ps1
```

| Command | Purpose |
| --- | --- |
| `.\scripts\start-backend.ps1` | Start FastAPI on `127.0.0.1:8000`. |
| `.\scripts\start-frontend.ps1` | Start Vite on `127.0.0.1:5173`. |
| `.\scripts\migrate.ps1` | Apply Alembic migrations. |
| `.\scripts\seed.ps1` | Seed the default local user and canonical job sources. |
| `.\scripts\test.ps1` | Run backend unit tests, DB tests when reachable, frontend tests, and frontend build. |
| `.\scripts\check-local.ps1` | Check backend, database, frontend, and role API proxy health. |

## Local Readiness Checklist

1. PostgreSQL is running.
2. `backend/.env` points to reachable `CAREERO_DATABASE_URL` and `CAREERO_TEST_DATABASE_URL`.
3. Backend dependencies are installed in `backend/.venv`.
4. Frontend dependencies are installed in `frontend/node_modules`.
5. Run `.\scripts\migrate.ps1`.
6. Run `.\scripts\seed.ps1`.
7. Start backend and frontend in separate terminals.
8. Run `.\scripts\check-local.ps1`.
9. Open `http://127.0.0.1:5173/roles/new` and create a role.
10. Open `http://127.0.0.1:5173/settings` and add an active resume/profile source.
11. Open the role detail page and run a STRIDE evaluation.

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m app.seed
```

Create the local PostgreSQL databases first, then edit `backend/.env` for your local connection URLs. See `backend/README.md` for database creation and all backend configuration variables.

Run the backend:

```powershell
uvicorn app.main:app --reload
```

The health check is available at:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/database
```

Run backend tests:

```powershell
pytest
```

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

The Vite dev server prints the local frontend URL when it starts.

Build the frontend:

```powershell
npm run build
```

Preview the production build:

```powershell
npm run preview
```

## Local Validation

From `backend`:

```powershell
pytest
```

From `frontend`:

```powershell
npm run build
```

These checks validate the backend API, database-backed Layer 2 flow, frontend components, and frontend production build.

## Layer 2 Status

Layer 2 is complete when local PostgreSQL credentials are valid, migrations and seed data have been applied, and the evaluation workflow works end to end: create a role, configure an active resume/profile source, run STRIDE evaluation, view it in the frontend, reuse the cached result, force a re-run, and inspect activity-log entries.

## STRIDE Architecture

- Role intake stores manually pasted role details. Careero does not scrape LinkedIn or poll job boards.
- Resume/profile source storage keeps one active local grounding source for the seeded local user and supports preview-only local imports for `.txt`, `.md`, `.docx`, and text-based `.pdf` files up to 5 MB.
- Deterministic rules produce the canonical score, recommendation, confidence, concerns, and keyword gaps.
- Optional OpenAI enrichment adds grounded structured analysis when enabled, but fallback deterministic results are always preserved.
- Evaluation metadata records model, prompt/ruleset versions, token estimates, latency, AI status, content hashes, and sanitized errors.
- Activity log entries record role, resume-source, and evaluation lifecycle events.
- AI-assisted role parsing is staged before persistence: parse pasted content, fill editable fields, and store parse metadata only when the reviewed role is created.

## Canonical Platform Contracts

Careero now includes an additive canonical contracts package at `packages/contracts`.

The package defines versioned Zod/TypeScript contracts and generated JSON Schema for:

- Workspace
- Opportunity
- STRIDE Evaluation
- Resume Artifact
- Cover Letter Artifact
- Application State

These contracts are future-facing platform definitions for backend persistence, frontend rendering, AI orchestration, workflow tracking, and export generation. Current role/evaluation APIs remain unchanged until a later migration phase.

See `docs/canonical-domain-model.md` for lifecycle guidance, AI boundaries, versioning strategy, and migration mapping from current `Role`, `StrideEvaluation`, `Application`, `GeneratedArtifact`, and `ResumeSource` models.

## Known Next Steps

- Migrate current role-centered data toward canonical workspace/opportunity contracts after Layer 2 workflows remain stable.
- Add application tracking workflows on top of evaluated roles.
- Add artifact generation preparation for resumes and cover letters.
- Add source discovery connectors only after manual intake and evaluation remain stable.
- Add Google Docs resume/profile import after OAuth, Drive/Docs scopes, document export, token handling, permission review, and security design are specified.
- Keep AWS deployment, auth, billing, tenants, workspaces, automated discovery, and application submission out of Layer 2.
