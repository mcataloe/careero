# Careero

Careero is a local-first career operations application for managing a personal job search and preparing strong applications. It is designed around a STRIDE-powered workflow for evaluating role fit, risk, positioning, and application priority.

Layer 1 is the local development foundation: a FastAPI backend, PostgreSQL persistence, a React + Vite + TypeScript frontend, manual role intake, and basic validation commands.

## Layer 1 Includes

- Local FastAPI backend with a health check endpoint.
- Local PostgreSQL persistence with Alembic migrations.
- Local React + Vite frontend for manual role intake.
- Manual create, list, view, update, and archive role workflow.
- Basic backend test coverage for `GET /health`.
- Database-backed integration tests for role intake when PostgreSQL is configured.
- Frontend component tests and production build validation.
- Frontend production build validation.
- Local development documentation.
- Reserved directories for future modular growth.

## Out of Scope

Layer 1 does not include:

- Authentication.
- Tenants, workspaces, or multi-user behavior.
- Billing or subscriptions.
- AWS or other cloud deployment logic.
- Background job execution.
- Automated job application submission.

## Repository Structure

```text
backend/   FastAPI application and backend tests
frontend/  React + Vite + TypeScript application
workers/   Reserved for future local worker processes
shared/    Reserved for future shared schemas and utilities
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

Known current blocker on this machine: PostgreSQL is running, but the configured `careero` database credentials are rejected. Until that is fixed, `/health/database` returns `503`, `/api/roles` fails, and database-backed tests fail with `OperationalError`.

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

These checks validate the initial backend health endpoint and frontend production build.

## Layer 1 Status

Layer 1 is complete when local PostgreSQL credentials are valid, migrations and seed data have been applied, and the manual role workflow works end to end: create, list, view, update, and archive.

## Known Next Steps

- Enrich STRIDE evaluation with AI-assisted structured analysis.
- Add application workflow features on top of captured roles.
- Add source polling only after manual intake is stable.
- Keep AWS deployment, auth, billing, tenants, and workspaces out of Layer 1.
