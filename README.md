# Careero

Careero is a local-first career operations application for managing a personal job search and preparing strong applications. It is designed around a STRIDE-powered workflow for evaluating role fit, risk, positioning, and application priority.

The current repository is beyond the original Layer 2 prototype: it includes local platform, intake, STRIDE, artifact-generation foundations, application workflow, and early intelligence surfaces. It is still a local-first application and should not be treated as production-ready.

## Strategic Plan and Layer Status

The canonical Careero strategic plan, current layer status, and recommended build sequence are tracked in [`docs/careero-application-plan-and-layer-status.md`](docs/careero-application-plan-and-layer-status.md).

Use that document as the source of truth for Careero-specific LEAP Recon, layer planning, and Codex implementation prompts.

Older roadmap material is retained only under `docs/archive/` for historical context and should not be used as current planning input.

Current planning hierarchy:

1. `README.md` - short project entry point and pointer to canonical planning docs.
2. [`docs/careero-application-plan-and-layer-status.md`](docs/careero-application-plan-and-layer-status.md) - canonical Careero-specific layer status and build order.
3. `docs/archive/*` - historical context only.
4. LEAP repo - reusable LEAP framework methodology, not Careero-specific product truth.

## Current Local Capabilities

- Local FastAPI backend with a health check endpoint.
- Local PostgreSQL persistence with Alembic migrations.
- Local React + Vite frontend.
- Workspace/search-track persistence and seeded default local workspace.
- Manual role/opportunity intake, list, detail, update, and archive workflow.
- Optional AI-assisted role parsing for pasted job posts, with user review before save.
- Local resume/profile source storage for STRIDE grounding, with paste or local file import.
- Deterministic STRIDE scoring for stored roles.
- Optional OpenAI STRIDE enrichment grounded in stored role and active resume/profile source data.
- Evaluation caching, prompt/ruleset versioning, audit metadata, and activity-log inspection.
- Backend artifact-generation foundations for resume and cover-letter drafts, with truthfulness checks and generated-artifact persistence.
- Application workflow tracking with state machine, state history, notes, external links, timeline, pipeline views, and structured interview tracking.
- Local reminder persistence/count/timeline support, while the fuller reminder API/UI branch still needs reconciliation into `main`.
- Analytics and dashboard surfaces for search analytics, STRIDE insights, source intelligence, compensation intelligence, search health, recommendations, historical learning, and artifact performance.
- Backend integration tests when PostgreSQL is configured.
- Frontend component tests and production build validation.
- Local development documentation.
- Reserved directories for future modular growth.

## Out of Scope

Careero does not yet include:

- Production authentication.
- Real multi-user tenant behavior.
- Production authorization hardening.
- Billing or subscriptions.
- Production deployment architecture.
- Background job execution.
- Canonical Opportunity API or migration from current `Role` naming.
- Mature workspace switching and management UX.
- Dedicated artifact list/detail/review/edit/approve/archive UX.
- Submitted artifact tracking.
- DOCX/PDF/Markdown artifact export workflow.
- Google Docs import.
- Gmail/Outlook integration.
- Calendar sync.
- LinkedIn/job-board helpers.
- Browser extension or share-sheet intake.
- Automated source discovery or polling.
- Automated job application submission.
- Automation approval logs and review-before-send workflows.
- Coach/advisor collaboration.
- Marketplace or employer-side capabilities.

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

| Command                        | Purpose                                                                              |
| ------------------------------ | ------------------------------------------------------------------------------------ |
| `.\scripts\start-backend.ps1`  | Start FastAPI on `127.0.0.1:8000`.                                                   |
| `.\scripts\start-frontend.ps1` | Start Vite on `127.0.0.1:5173`.                                                      |
| `.\scripts\migrate.ps1`        | Apply Alembic migrations.                                                            |
| `.\scripts\seed.ps1`           | Seed the default local user and canonical job sources.                               |
| `.\scripts\test.ps1`           | Run backend unit tests, DB tests when reachable, frontend tests, and frontend build. |
| `.\scripts\check-local.ps1`    | Check backend, database, frontend, and role API proxy health.                        |

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
