# Careero

Careero is a local-first career operations application for managing a personal job search and preparing strong applications. It is designed around a STRIDE-powered workflow, but this initial foundation only names that direction and does not define the STRIDE model yet.

Layer 1 is the local development foundation: a FastAPI backend, a React + Vite + TypeScript frontend, reserved monorepo areas for future workers/shared code/infrastructure/scripts, and basic validation commands.

## Layer 1 Includes

- Local FastAPI backend with a health check endpoint.
- Local PostgreSQL persistence with Alembic migrations.
- Local React + Vite frontend shell.
- Basic backend test coverage for `GET /health`.
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

On Windows PowerShell, if `npm` is blocked by script execution policy, use `npm.cmd` in the commands below.

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
