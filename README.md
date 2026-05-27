# Careero

Careero is a local-first career operations application for managing a personal job search and preparing strong applications. It is designed around a COMPASS-powered workflow for evaluating role fit, risk, positioning, and application priority.

The current repository is beyond the original Layer 2 prototype: it includes local platform, intake, COMPASS, artifact-generation foundations, application workflow, and early intelligence surfaces. It is still a local-first application and should not be treated as production-ready.

## Strategic Plan and Layer Status

The canonical Careero strategic plan, current layer status, and recommended build sequence are tracked in [`docs/careero-application-plan-and-layer-status.md`](docs/careero-application-plan-and-layer-status.md).

Use that document as the source of truth for Careero-specific LEAP Recon, layer planning, and Codex implementation prompts.

Layer 7 Opportunity model strategy is captured in [`docs/opportunity-model-strategy.md`](docs/opportunity-model-strategy.md).

Layer 11 productization readiness is captured in [`docs/productization-readiness.md`](docs/productization-readiness.md), with supporting privacy/data governance, account lifecycle, AI usage/cost control, monetization-boundary, and deployment-readiness docs. A local-first readiness endpoint and Settings panel now report the current gates honestly. First-party local email/password login now exists, while Google/LinkedIn SSO, account recovery, production auth hardening, billing, tenant isolation, and hosted deployment remain future.

Auth-provider and hosted-beta direction is evaluated in [`docs/auth-provider-and-hosted-beta-evaluation.md`](docs/auth-provider-and-hosted-beta-evaluation.md). It is evaluation only and does not select or implement auth.

Layer 12 advisor collaboration readiness is captured in [`docs/advisor-collaboration-mode.md`](docs/advisor-collaboration-mode.md). Local-only advisor packet preview/export scaffolding exists; hosted collaboration, advisor accounts, invitations, comments, and external sharing remain future.

Layer 14 model catalog, Careero Prompt Architecture, model choice, usage accounting, and credit-control strategy is captured in [`docs/careero-layer-14-model-catalog-and-prompt-architecture.md`](docs/careero-layer-14-model-catalog-and-prompt-architecture.md). This is strategic planning only; model catalogs, prompt gateways, prompt-only export, credit wallets, usage ledgers, and paid model-cost controls are not implemented in `main`.

Layer 15 API job sources, import pipelines, source snapshots, and managed-delta strategy is captured in [`docs/careero-layer-15-api-job-sources-and-managed-deltas.md`](docs/careero-layer-15-api-job-sources-and-managed-deltas.md). This is strategic planning only; ATS/job-data provider adapters, job posting snapshots, import candidates, managed deltas, and API source governance are not implemented in `main`.

Layer 16 guided onboarding, first-search activation, contextual help, and support/feedback strategy is captured in [`docs/careero-layer-16-guided-onboarding-and-first-search-activation.md`](docs/careero-layer-16-guided-onboarding-and-first-search-activation.md). This is strategic planning only; persisted onboarding state, guided first-run flow, tour skip/resume/replay behavior, contextual onboarding empty states, and support/feedback capture are not implemented in `main`.

Older roadmap material is retained only under `docs/archive/` for historical context and should not be used as current planning input.

Current planning hierarchy:

1. `README.md` - short project entry point and pointer to canonical planning docs.
2. [`docs/careero-application-plan-and-layer-status.md`](docs/careero-application-plan-and-layer-status.md) - canonical Careero-specific layer status and build order.
3. Active layer-specific docs, including [`docs/opportunity-model-strategy.md`](docs/opportunity-model-strategy.md), [`docs/productization-readiness.md`](docs/productization-readiness.md), [`docs/advisor-collaboration-mode.md`](docs/advisor-collaboration-mode.md), [`docs/careero-layer-14-model-catalog-and-prompt-architecture.md`](docs/careero-layer-14-model-catalog-and-prompt-architecture.md), [`docs/careero-layer-15-api-job-sources-and-managed-deltas.md`](docs/careero-layer-15-api-job-sources-and-managed-deltas.md), and [`docs/careero-layer-16-guided-onboarding-and-first-search-activation.md`](docs/careero-layer-16-guided-onboarding-and-first-search-activation.md).
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
- First-party local email/password account registration and login with HttpOnly cookie-backed sessions, current-user lookup, logout, and route protection.
- Disabled Google and LinkedIn SSO placeholders on the login page. OAuth is not implemented.
- Local-first JSON data export for the authenticated local user through `GET /api/data-export/local` and the Settings page. This creates no cloud download link, backup, hosted account export, or production account support.
- Local-first account lifecycle request tracking through `GET/POST /api/account/lifecycle-requests` and the Settings page. This records audit requests only and does not delete or anonymize data.
- Local-first provider-agnostic AI usage metering through `GET /api/usage/ai` and the Settings page. This records safe metadata for local visibility only and does not implement credits, billing, or paid quotas.
- Local-first entitlement boundary reporting through `GET /api/entitlements/current` and the Settings page. This models the `local_free` plan without payments, checkout, subscriptions, or invoices.
- Local-only advisor packet preview and Markdown export with deterministic redaction metadata, explicit local include options, and redacted defaults for private notes, COMPASS rationale, ATS risk, compensation strategy, recruiter/contact details, raw sources, and artifact content.
- Backend integration tests when PostgreSQL is configured.
- Frontend component tests and production build validation.
- Local development documentation.
- Reserved directories for future modular growth.
- Local-first current-user context and service-level ownership-boundary prep for user-data services. Seeded local-user operation is preserved only for seed, direct service, and test paths where password auth is disabled.

## Out of Scope

Careero does not yet include:

- Production authentication hardening and account recovery.
- Real multi-user tenant behavior.
- Production authorization hardening and hosted tenant isolation certification.
- Billing or subscriptions.
- Model catalog, prompt gateway, prompt-only export, credit wallet, credit-based billing controls, or paid model-cost enforcement.
- Production deployment architecture.
- Hosted account export, destructive account deletion, anonymization, retention enforcement, or production account lifecycle support.
- Background job execution.
- Destructive persistence migration from current `Role` table/model/foreign-key naming.
- Mature workspace switching and management UX.
- First-run guided onboarding workflow.
- Persisted per-user onboarding state.
- Tour skip/resume/replay behavior.
- Contextual onboarding empty states.
- Support/help/bug/suggestion feedback capture.
- Privacy-safe support payload governance.
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
- API-only ATS/job-source ingestion, imported job snapshots, import candidates, managed deltas, or API source governance.
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
