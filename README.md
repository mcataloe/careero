# Careero

Careero is a local-first career operations application for managing a personal job search and preparing strong applications. It is designed around a COMPASS-powered workflow for evaluating role fit, risk, positioning, and application priority.

The current repository is beyond the original Layer 2 prototype: it includes local platform, intake, COMPASS, artifact-generation foundations, application workflow, and early intelligence surfaces. It is still a local-first application and should not be treated as production-ready.

## Strategic Plan and Layer Status

The canonical Careero strategic plan, current layer status, and recommended build sequence are tracked in [`docs/careero-application-plan-and-layer-status.md`](docs/careero-application-plan-and-layer-status.md).

Use that document as the source of truth for Careero-specific LEAP Recon, layer planning, and Codex implementation prompts.

Layer 7 Opportunity model strategy is captured in [`docs/opportunity-model-strategy.md`](docs/opportunity-model-strategy.md).

Layer 11 productization readiness is captured in [`docs/productization-readiness.md`](docs/productization-readiness.md), with supporting privacy/data governance, account lifecycle, AI usage/cost control, monetization-boundary, and deployment-readiness docs. A local-first readiness endpoint and Settings panel now report the current gates honestly. These are readiness surfaces only; production auth, billing, tenant isolation, and hosted deployment remain future.

Layer 12 advisor collaboration readiness is captured in [`docs/advisor-collaboration-mode.md`](docs/advisor-collaboration-mode.md). Local-only advisor packet preview/export scaffolding exists; hosted collaboration, advisor accounts, invitations, comments, and external sharing remain future.

Layer 14 model choice, credits, and API-first intelligence strategy is captured in [`docs/careero-layer-14-strategic-plan-section.md`](docs/careero-layer-14-strategic-plan-section.md) and summarized in the canonical layer plan. This is strategic planning only; model catalogs, credit wallets, usage ledgers, API job ingestion, company research caching, and scraping are not implemented in `main`.

Older roadmap material is retained only under `docs/archive/` for historical context and should not be used as current planning input.

Current planning hierarchy:

1. `README.md` - short project entry point and pointer to canonical planning docs.
2. [`docs/careero-application-plan-and-layer-status.md`](docs/careero-application-plan-and-layer-status.md) - canonical Careero-specific layer status and build order.
3. Active layer-specific docs, including [`docs/opportunity-model-strategy.md`](docs/opportunity-model-strategy.md), [`docs/productization-readiness.md`](docs/productization-readiness.md), [`docs/advisor-collaboration-mode.md`](docs/advisor-collaboration-mode.md), and [`docs/careero-layer-14-strategic-plan-section.md`](docs/careero-layer-14-strategic-plan-section.md).
4. `docs/archive/*` - historical context only.
5. LEAP repo - reusable LEAP framework methodology, not Careero-specific product truth.

## Current Local Capabilities

- Local FastAPI backend with a health check endpoint.
- Local PostgreSQL persistence with Alembic migrations.
- Local React + Vite frontend.
- Workspace/search-track persistence and seeded default local workspace.
- Opportunity-facing intake, list, detail, update, and archive workflow backed by current `Role` persistence.
- Optional AI-assisted role parsing for pasted job posts, with user review before save.
- Local resume/profile source storage for COMPASS grounding, with paste or local file import.
- Deterministic COMPASS scoring for stored opportunities.
- Optional OpenAI COMPASS enrichment grounded in stored role and active resume/profile source data.
- Evaluation caching, prompt/ruleset versioning, audit metadata, and activity-log inspection.
- Backend artifact-generation foundations for resume and cover-letter drafts, with truthfulness checks and generated-artifact persistence.
- Backend local Markdown/DOCX/PDF export for stored generated artifacts.
- Application workflow tracking with state machine, state history, notes, external links, local reminders, timeline, pipeline views, and structured interview tracking.
- Local reminder API routes and application-detail reminder UX for listing, creating, editing, and completing reminders. No cloud scheduling, calendar sync, email notifications, or external reminder delivery exists.
- Analytics and dashboard surfaces for search analytics, COMPASS insights, source intelligence, compensation intelligence, search health, recommendations, historical learning, and artifact performance.
- Local automation suggestion, approval-log, and workspace preference guardrails with external actions disabled.
- Read-only career strategy synthesis for workspace/search-track retrospectives and internal cross-track comparison based only on stored Careero data.
- Local-first productization readiness reporting through `GET /api/productization/readiness` and the Settings page. This reports current blockers and does not implement production deployment.
- Local-first JSON data export for the current seeded local user through `GET /api/data-export/local` and the Settings page. This creates no cloud download link, backup, hosted account export, or production account support.
- Local-first account lifecycle request tracking through `GET/POST /api/account/lifecycle-requests` and the Settings page. This records audit requests only and does not delete or anonymize data.
- Local-first provider-agnostic AI usage metering through `GET /api/usage/ai` and the Settings page. This records safe metadata for local visibility only and does not implement credits, billing, or paid quotas.
- Local-only advisor packet preview and Markdown export with deterministic redaction metadata, explicit local include options, and redacted defaults for private notes, COMPASS rationale, ATS risk, compensation strategy, recruiter/contact details, raw sources, and artifact content.
- Backend integration tests when PostgreSQL is configured.
- Frontend component tests and production build validation.
- Local development documentation.
- Reserved directories for future modular growth.
- Local-first current-user context and service-level ownership-boundary prep for
  workspace, role/opportunity, and application workflow services. This preserves
  seeded local-user operation and is not production authentication.

## Out of Scope

Careero does not yet include:

- Production authentication.
- Real multi-user tenant behavior.
- Production authorization hardening.
- Billing or subscriptions.
- Model catalog, credit wallet, credit-based billing controls, or paid usage enforcement.
- Production deployment architecture.
- Hosted account export, destructive account deletion, anonymization, retention enforcement, or production account lifecycle support.
- Background job execution.
- Destructive persistence migration from current `Role` table/model/foreign-key naming.
- Mature workspace switching and management UX.
- Durable strategy tables, hidden strategy memory, or user-unreviewed saved retrospectives.
- Dedicated artifact list/detail/review/edit/approve/archive UX.
- Submitted artifact tracking.
- Dedicated frontend artifact export workflow.
- Google Docs import.
- Gmail/Outlook integration.
- Calendar sync.
- LinkedIn/job-board helpers.
- Browser extension or share-sheet intake.
- Automated source discovery or polling.
- API-only ATS/job-posting ingestion and company research caching.
- Scraping, restricted-source extraction, or browser-driven external collection.
- Automated job application submission.
- External review-before-send workflows.
- State-changing or externally mutating automation.
- Hosted coach/advisor collaboration.
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
| `.\scripts\check-local.ps1`    | Check backend, database, frontend, and API proxy health.                             |

## Local Readiness Checklist

1. PostgreSQL is running.
2. `backend/.env` points to reachable `CAREERO_DATABASE_URL` and `CAREERO_TEST_DATABASE_URL`.
3. Backend dependencies are installed in `backend/.venv`.
4. Frontend dependencies are installed in `frontend/node_modules`.
5. Run `.\scripts\migrate.ps1`.
6. Run `.\scripts\seed.ps1`.
7. Start backend and frontend in separate terminals.
8. Run `.\scripts\check-local.ps1`.
9. Open `http://127.0.0.1:5173/opportunities/new` and create an opportunity.
10. Open `http://127.0.0.1:5173/settings` and add an active resume/profile source.
11. Open the opportunity detail page and run a COMPASS evaluation.

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
