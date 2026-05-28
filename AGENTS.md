# Master Repo AGENTS.md — LEAP Local Trial Template

Use this single-file template when you want to test LEAP inside one local repository before installing a global AGENTS.md system-wide.

This file intentionally combines two scopes:

1. **Locked Global Section** — reusable LEAP operating behavior copied from the global AGENTS.md template.
2. **Editable Repository Section** — project-specific AGENTS.md content that should be populated from the current repository.

When this file is placed at the root of a repository as `AGENTS.md`, the code assistant should treat the locked global section as global LEAP behavior and the editable repository section as the repository-level AGENTS.md content.

## Local-Trial Editing Rules

- Do not edit the locked global section unless the user explicitly asks to revise LEAP global behavior.
- Do not remove or rename the section boundary markers.
- Populate only the editable repository section during repo onboarding.
- Preserve the overall two-section structure.
- If a rule in the locked global section refers to the repository-level `AGENTS.md`, interpret that as the editable repository section in this same file.
- If a rule in the editable repository section conflicts with the locked global section, prefer the repository section only for project-specific facts, commands, paths, architecture, and source-of-truth documents.
- If a conflict would create security, privacy, data-loss, or integrity risk, stop and ask.

---

<!-- LEAP_MASTER_GLOBAL_SECTION_START: DO NOT EDIT DURING REPO POPULATION -->

# Global AGENTS.md — LEAP Operating Template

## Purpose

Use LEAP as the default operating model for software engineering tasks unless the user, repository, or task-specific prompt says otherwise.

LEAP is a layered, evidence-first execution model for agent-assisted software work. Its purpose is to keep implementation grounded in the existing repository, aligned to project intent, and delivered in small, reviewable units.

This global file defines reusable behavior across repositories. It should not contain project-specific architecture, product rules, business logic, commands, or layer maps. Those belong in the repository-level `AGENTS.md` and project documentation.

---

## Instruction Priority

When working in a repository, follow instructions in this order:

1. System/developer/tool instructions.
2. Explicit user instructions for the current task.
3. Repository-level `AGENTS.md` and closer scoped agent instruction files.
4. This global `AGENTS.md`.
5. Existing source code, tests, documentation, and conventions.

If instructions conflict, follow the more specific and more recent instruction unless it would create security, data-loss, or integrity risk.

---

## Default LEAP Work Pattern

For non-trivial implementation tasks, use this sequence:

1. Understand the task.
2. Perform repository reconnaissance before editing.
3. Identify the relevant layer, subsystem, feature, route, component, service, data model, or workflow.
4. Locate existing patterns and contracts.
5. Make a concise implementation plan.
6. Implement the smallest coherent change.
7. Add or update relevant tests.
8. Run practical validation checks.
9. Summarize changes, validation, risks, and follow-ups.

Do not treat the task as greenfield unless the repository clearly lacks an existing implementation path.

---

## Reconnaissance Expectations

Before editing code, inspect the repository enough to understand:

- Existing project structure.
- Relevant docs and architecture notes.
- Similar implemented features.
- Naming conventions.
- Data contracts and validation patterns.
- Test structure.
- Build, lint, typecheck, and test commands.
- Known TODOs or roadmap notes related to the task.

Prefer evidence from the repository over assumptions.

---

## LEAP Command Shortcuts

When the user says:

```text
Run LEAP Recon for the following functionality:
[feature, layer, bugfix, workflow, or functional area]
```

treat that as a request to run the current LEAP Recon standard.

Default behavior:

1. Use the repository-level `AGENTS.md` first.
2. Inspect the current repository state.
3. Use the current LEAP Recon Standard Operational Prompt from the LEAP framework repository:
   `https://github.com/mjcataldi/leap_framework/blob/main/prompts/leap-recon-standard.md`
4. Use source-of-truth documents identified by the repository-level `AGENTS.md`.
5. Return Recon only.
6. Do not implement code changes.
7. Do not generate the final LEAP implementation prompt unless the user asks after Recon.

If the LEAP Recon standard or repository-level `AGENTS.md` cannot be read, stop and explain what source is unavailable.

The user should not need to paste the full Recon rules when using standard AGENTS.md behavior. The shortcut above exists so the user can launch Recon with only the functionality description.

---

## Planning Standard

For meaningful work, produce a short plan before implementation.

A useful plan should identify:

- The likely files or modules to inspect/change.
- The implementation sequence.
- Tests or checks to run.
- Compatibility concerns.
- Documentation updates.
- Stop conditions or decisions that require the user.

Avoid excessive planning for small, obvious changes.

---

## Implementation Standard

When changing code:

- Reuse existing patterns before introducing new ones.
- Keep changes scoped to the requested task.
- Prefer small, reviewable units.
- Preserve backward compatibility unless explicitly told otherwise.
- Do not rename public interfaces without a clear reason.
- Do not introduce new dependencies without justification.
- Do not mix unrelated refactors into feature work.
- Do not duplicate business logic, schemas, or validation rules.
- Prefer clear, boring, maintainable code over clever code.
- Keep behavior deterministic where practical.
- Handle errors explicitly.
- Preserve existing security, privacy, and auditability boundaries.

---

## LEAP Layer Discipline

When a task references a layer, phase, milestone, or subsection:

- Treat that boundary as the implementation scope.
- Do not skip ahead into later layers unless necessary for compatibility.
- Do not silently implement adjacent layers.
- Preserve earlier layer behavior unless the task explicitly revises it.
- Commit or summarize work by the requested layer/subsection boundary when asked.

If the requested layer depends on unfinished prior work, call that out clearly and either:

- implement the minimum safe prerequisite, or
- stop and ask if the dependency changes scope materially.

---

## House Standard Prompt Behavior

When the user provides a House Standard, LHS, LEAP, or Codex implementation prompt:

- Treat it as the task contract.
- Follow the requested model/reasoning/plan-mode assumptions where applicable.
- Reconcile the prompt against the repository before editing.
- Push back if the prompt conflicts with existing architecture, security, data integrity, or documented product intent.
- Prefer staged implementation over broad rewrites.
- Keep changes modular, testable, and documented.

---

## Questions and Stop Conditions

Ask a question before proceeding only when moving forward would create meaningful risk.

Stop and ask before:

- Destructive production-like data changes.
- Dropping or overwriting user data.
- Weakening authentication or authorization.
- Exposing secrets or credentials.
- Adding paid external services.
- Adding major production dependencies.
- Changing public API contracts without migration.
- Replacing major architecture instead of extending it.
- Guessing business rules that materially affect user-facing behavior.
- Implementing a security-sensitive shortcut.
- Committing large unrelated changes.
- Making irreversible git operations.

If the project is explicitly a prototype or POC, destructive changes may be acceptable, but still call out the risk before doing them.

---

## Testing and Validation

After implementation:

- Run the most relevant available tests/checks.
- Prefer targeted tests first, then broader checks when practical.
- Add or update tests when behavior changes.
- Do not claim tests passed if they were not run.
- If tests cannot be run, explain why.
- If tests fail, investigate and report the failure honestly.
- Do not hide known regressions.

Common validation categories:

- Unit tests.
- Integration/API tests.
- Typecheck.
- Lint.
- Build.
- Formatting.
- Migration checks.
- Manual smoke test notes.

Use the repository’s actual commands, not generic commands, whenever possible.

---

## Documentation Standard

Update documentation when a change affects:

- Setup or local development.
- Public behavior.
- User workflows.
- API contracts.
- Data models.
- Environment variables.
- Security assumptions.
- Architecture.
- Layer strategy.
- Operational commands.

Keep docs concise and close to the changed behavior.

---

## Git and Commit Standard

When asked to commit:

- Commit only coherent, reviewable units.
- Use the requested layer/subsection title when provided.
- Do not bundle unrelated work.
- Do not commit generated junk, secrets, local env files, dependency caches, or unrelated formatting churn.
- Check `git status` before committing.
- Include a clear commit message.

Preferred LEAP commit message shape:

`Layer X — Short Descriptive Title`

Examples:

`Layer 6C — Versioning, Review, and Submitted-State Workflow`

`Layer 8A — Integration Provider Contracts`

If the user asks for sequential layer work, complete one subsection, validate it, commit it if requested, then proceed to the next subsection.

---

## Final Response Standard

At completion, summarize:

- What changed.
- Files or areas touched.
- Tests/checks run.
- Any tests/checks not run.
- Risks or follow-ups.
- Whether the work stayed within the requested layer/scope.

Be direct. Do not oversell the result.

---

## Do Not Do

Do not:

- Invent project requirements.
- Fabricate test results.
- Ignore existing docs.
- Replace established architecture without cause.
- Add dependencies casually.
- Hide uncertainty.
- Implement broad refactors under a narrow task.
- Weaken security to make tests pass.
- Commit secrets or `.env` files.
- Treat AI-generated assumptions as source of truth.
- Continue past a serious unresolved ambiguity.


<!-- LEAP_MASTER_GLOBAL_SECTION_END -->

---

<!-- LEAP_MASTER_REPO_SECTION_START: EDIT THIS SECTION ONLY DURING REPO POPULATION -->

# Repository AGENTS.md - Careero Project Context

## Project Identity

This repository uses LEAP for agent-assisted software delivery.

LEAP work must be grounded in the repository's actual code, tests, documentation, architecture, and product intent. Do not treat prompts as permission to bypass established project rules.

Project name:

`Careero`

Project summary:

Careero is a local-first career operations application for managing a personal job search, evaluating opportunity fit with COMPASS, preparing grounded application materials, and tracking application workflow. The repository is beyond the original Layer 2 prototype and includes local platform, intake, COMPASS, artifact-generation foundations, application workflow, early intelligence surfaces, local auth, local data export, and local-only advisor packet scaffolding. It is not production-ready or hosted-beta-ready.

Application type and maturity:

- Local-first full-stack web application.
- Current implementation is a local MVP/product prototype with substantial implemented layers.
- Production auth hardening, tenant isolation, billing, hosted deployment, real account lifecycle enforcement, and external integrations remain future.

Primary users/use cases:

- Individual job seekers managing focused career searches/workspaces.
- Local opportunity intake, role fit evaluation, resume/profile grounding, artifact drafting, application workflow tracking, and reviewable strategy/insight surfaces.
- Advisor/collaboration use is local-only packet preview/export; hosted collaboration is not implemented.

Primary product/architecture docs:

- `README.md` - project entry point and current capabilities/out-of-scope summary.
- `docs/00_start-here.md` - documentation map and contributor reading order.
- `docs/01_strategy/00_product-strategy.md` - canonical Careero-specific layer status and high-level build order.
- `docs/01_strategy/07_revised-build-order-execution-plan.md` - operational LEAP/LHS prompt sequence, readiness gates, pull-forward rules, and scope discipline.
- `docs/02_layers/00_layer-index.md` - canonical LEAP layer specs.
- `docs/03_domain-design/00_domain-index.md` - domain design entry point.
- `docs/04_ai-and-compass/00_ai-compass-index.md` - COMPASS and AI guidance.
- `docs/05_security-privacy-governance/00_security-privacy-index.md` - auth, privacy, data governance, and contract boundaries.
- `docs/05_security-privacy-governance/canonical-domain-model.md` - canonical contract and entity responsibilities.
- `docs/06_operations/local-deployment.md` - local setup and validation.
- `docs/06_operations/execution-drift-ledger.md` - known drift, decisions, and risk memory.
- `packages/contracts/README.md` - executable TypeScript/Zod contract package.

Read the relevant docs before implementing layer, architecture, workflow, data model, AI, privacy, or user-facing changes.

---

## Repository Layout

- `backend/` - FastAPI backend, SQLAlchemy models, Alembic migrations, Pydantic schemas, API routes, services, repositories, seed script, and pytest tests under `backend/tests/`.
- `frontend/` - React + Vite + TypeScript frontend using Mantine, React Router, Vitest, and Testing Library.
- `packages/contracts/` - canonical TypeScript/Zod contracts, generated JSON Schema, provider-neutral COMPASS helpers, and contract tests.
- `docs/` - active strategy, layers, domain design, AI/COMPASS, security/privacy/governance, operations, prompts, reports/audits, and archive documentation.
- `scripts/` - PowerShell developer automation for starting/stopping services, migrations, seed, tests, and local readiness checks.
- `infra/` - reserved for future infrastructure documentation/configuration; no cloud deployment logic is implemented.
- `shared/` - reserved for future runtime-agnostic shared utilities; canonical contracts currently live in `packages/contracts`.
- `workers/` - reserved for future local worker processes; no background job engine is implemented.
- `.gitlab-ci.yml` - GitLab SAST and secret-detection templates only.

If the repository structure changes, update this section.

---

## Technology Stack

- Frontend: React 19, Vite 7, TypeScript 5.8, Mantine 9, React Router 7, Tabler icons, Vitest, Testing Library, jsdom.
- Backend/API: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic settings, psycopg, jsonschema, python-docx, pypdf, python-multipart.
- AI provider integration: optional OpenAI SDK usage behind local feature flags; deterministic COMPASS fallback works without an API key.
- Authentication: local first-party email/password auth with Argon2id password hashing and server-side HttpOnly cookie sessions. Production auth hardening is incomplete.
- Database: local PostgreSQL for development and tests.
- Contracts: TypeScript/Zod package in `packages/contracts`, with generated JSON Schema for backend/AI validation.
- Infrastructure: local-first only; `infra/` is reserved and `.gitlab-ci.yml` enables GitLab SAST/secret detection.
- Package managers: `pip` for backend dependencies, `npm` for frontend and contracts packages.
- Test frameworks: `pytest` for backend, `vitest` for frontend and contracts.
- Runtime versions: Python 3.11+ and Node.js 20+ are documented requirements.

Use the existing stack unless the user explicitly requests evaluation or migration.

---

## Setup Commands

Use the repository's existing setup process. Commands are documented for Windows PowerShell.

Create PostgreSQL role/databases:

```sql
CREATE ROLE careero WITH LOGIN PASSWORD 'careero';
CREATE DATABASE careero OWNER careero;
CREATE DATABASE careero_test OWNER careero;
```

Backend setup:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edit `backend/.env` for local PostgreSQL and optional AI flags. Do not commit real secrets.

Frontend setup:

```powershell
cd frontend
npm install
```

Contracts setup:

```powershell
cd packages/contracts
npm install
```

Database migration and seed from the repository root:

```powershell
.\scripts\migrate.ps1
.\scripts\seed.ps1
```

Local development from the repository root:

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
```

or:

```powershell
.\scripts\start-all.ps1
```

Expected local URLs:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`
- Health checks: `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/health/database`

If PowerShell blocks scripts, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-local.ps1
```

---

## Validation Commands

Use the most relevant validation commands for the changed area. Prefer targeted checks first, then broader checks when practical.

Root local readiness:

```powershell
.\scripts\check-local.ps1
```

Root scripted test pass:

```powershell
.\scripts\test.ps1
```

Backend targeted tests:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests\test_config.py tests\test_health.py
```

Backend full tests when `CAREERO_TEST_DATABASE_URL` is configured and reachable:

```powershell
cd backend
$env:CAREERO_TEST_DATABASE_URL="postgresql://careero:careero@localhost:5432/careero_test"
.\.venv\Scripts\python.exe -m pytest
```

Frontend tests and build/typecheck:

```powershell
cd frontend
npm run test
npm run build
```

Contracts validation:

```powershell
cd packages/contracts
npm run validate
```

Format command:

`TBD - What formatter should be canonical for Python, frontend TypeScript, contracts, and docs? No repository-level format script was discovered.`

Lint command:

`TBD - What lint command should be canonical? No ruff/black/mypy/eslint/prettier lint script was discovered in the inspected package/config files.`

Typecheck command:

- Frontend typecheck is included in `frontend` `npm run build` via `tsc -b && vite build`.
- Contracts typecheck is included in `packages/contracts` `npm run build` via `tsc -p tsconfig.json`.
- `TBD - Should backend static typing be checked with mypy, pyright, or no Python typecheck command?`

If a command is missing, broken, environment-dependent, or too expensive to run, explain that in the final response.

---

## External Services and Runtime Dependencies

- PostgreSQL is required for normal local development and database-backed tests.
- OpenAI calls are optional and disabled by default through `backend/.env` feature flags. AI role parsing, COMPASS enrichment, resume generation, and cover-letter generation require explicit local enablement and `CAREERO_OPENAI_API_KEY`.
- No queue, cache, background job engine, cloud scheduler, calendar sync, email delivery, billing provider, OAuth/SSO provider, hosted storage, scraping engine, or browser extension is implemented.
- Local artifact export supports Markdown, DOCX, and PDF from backend APIs. Export does not upload to cloud storage or mutate external systems.

---

## LEAP Project Rules

This repository should be implemented in bounded LEAP units.

When a task references a layer, phase, subsection, milestone, or roadmap item:

1. Read `docs/00_start-here.md`, then the relevant strategy/layer/domain docs.
2. Check `docs/06_operations/execution-drift-ledger.md` for known drift and blockers.
3. Confirm the existing implementation state in code, tests, migrations, and UI/API surfaces.
4. Identify affected models, routes, services, schemas, frontend components, contract files, tests, and docs.
5. Implement only the requested layer/subsection unless a prerequisite is required.
6. Preserve compatibility with completed prior layers and current local-first behavior.
7. Update relevant tests and docs.
8. Summarize remaining gaps and explicitly call out future-only capabilities.

Do not skip ahead into later layers unless the user explicitly asks.

Current layer posture from active docs:

- Layers 0-4 are built for current local MVP scope, with production hardening incomplete.
- Layer 5 is stabilized for current local MVP insight behavior.
- Layer 6 is complete for current local MVP artifact lifecycle scope; comparison, standalone workspace artifact browsing, and frontend export convenience remain future.
- Layer 7 opportunity compatibility is the next immediate implementation sequence.
- Layers 8-10 are partially built or in local-first evolution.
- Layers 11-12 have local foundations/readiness work but hosted blockers remain.
- Layers 13-16 are future or appended strategic layers.

---

## Project Source of Truth

Use this order of truth when making decisions:

1. Explicit user instruction for the current task.
2. Current repository code, tests, migrations, package files, and scripts.
3. This editable repository section of root `AGENTS.md` and any closer scoped agent instruction files.
4. `docs/00_start-here.md`.
5. `docs/01_strategy/00_product-strategy.md`.
6. `docs/01_strategy/07_revised-build-order-execution-plan.md`.
7. Active layer specs under `docs/02_layers/`.
8. Active domain, AI/COMPASS, security/privacy/governance, and operations docs.
9. `docs/06_operations/execution-drift-ledger.md`.
10. README/setup docs.
11. Reports/audits under `docs/08_reports-and-audits/` as non-canonical evidence.
12. Existing issue/task text and reasonable inference from nearby patterns.

Known document status:

- `docs/07_prompts/` contains execution artifacts and is not source-of-truth product design.
- `docs/08_reports-and-audits/` contains audits/findings and is not canonical product truth unless promoted into active strategy/layer docs.
- `docs/99_archive/` is historical/superseded and must not be used as current planning input unless explicitly requested for historical comparison.
- Active Careero terminology uses COMPASS. STRIDE is legacy terminology except when explicitly historical.

If sources conflict, call out the conflict and prefer the more specific, more recent, and safer source.

---

## Architecture Rules

Follow the project's existing architecture.

Project-specific architecture constraints:

- Backend routing lives under `backend/app/api/`, schemas under `backend/app/schemas/`, domain/service logic under `backend/app/services/`, persistence models in `backend/app/models.py`, database setup in `backend/app/database.py`, and migrations under `backend/alembic/versions/`.
- Frontend API clients live under `frontend/src/api/`, types under `frontend/src/types/`, page-level surfaces under `frontend/src/pages/`, shared components under `frontend/src/components/`, and auth context under `frontend/src/auth/`.
- Canonical long-term contracts live in `packages/contracts`; backend consumers should use generated JSON Schema rather than importing TypeScript directly.
- Current persistence remains Role-backed for Opportunity-facing compatibility. Do not perform destructive Role-to-Opportunity renames or foreign-key churn without explicit approval.
- Workspace/user ownership boundaries must be preserved. Seeded local-user fallback exists only for seed, direct-service, and auth-disabled test paths.
- Application workflow state is the authority for workflow state; `Role.status` remains a lightweight opportunity status compatibility surface.
- Timeline rendering is an aggregation over typed workflow persistence; do not make timeline rows the source persistence model.
- Local-first integration adapter/export boundaries must not become external sync, cloud upload, or state-changing automation without fresh approval.
- Prefer incremental extension over replacement and preserve backward-compatible API aliases where docs identify compatibility surfaces.

Default expectations:

- Keep domain logic out of presentation-only code when possible.
- Keep API contracts explicit.
- Keep validation close to data boundaries.
- Reuse existing schema, type, DTO, service, and component patterns.
- Avoid duplicating model definitions.
- Preserve ownership, authorization, audit, and privacy boundaries.
- Keep persistence concerns isolated according to existing repository patterns.
- Avoid broad rewrites unless the user requested a refactor.

---

## Data and Migration Rules

Before changing schemas, migrations, seed data, or persistence behavior:

- Inspect `backend/app/models.py`, `backend/alembic/versions/`, affected services, API schemas, and tests.
- Treat the project as local-first but data-preserving. Do not assume destructive migration is acceptable because production deployment is incomplete.
- Preserve existing data unless destructive changes are explicitly allowed.
- Keep migrations reversible where practical.
- Update tests and docs for data model changes.
- Do not silently change identifiers, ownership semantics, workspace scoping, lifecycle states, or compatibility aliases.

Project-specific data rules:

- PostgreSQL is the local persistence target.
- Alembic migrations are the schema-change path.
- `python -m app.seed` is idempotent and creates/updates seeded local compatibility data, including the seeded local user, canonical job sources, and default active workspace.
- Registered users receive their own workspace and job sources; the fixed seeded default workspace remains reserved for seeded local compatibility paths.
- Account lifecycle request tracking is audit/request-only today; it does not delete, anonymize, recover, or enforce retention.
- Local JSON export must never include environment variables, API keys, database URLs, provider credentials, or unrelated users' records.

---

## API and Contract Rules

When changing APIs, contracts, schemas, or shared types:

- Preserve backward compatibility unless explicitly told otherwise.
- Update backend schemas, frontend types/API clients, and contract schemas together when a shared contract changes.
- Update API/service tests and frontend tests near the changed behavior.
- Update docs or examples when behavior changes.
- Keep error responses consistent with existing patterns.
- Avoid creating parallel contract definitions.

Project-specific contract rules:

- `packages/contracts` is additive and future-facing but is the canonical long-term platform contract source.
- Current contract version is `careero.contracts.v1`; breaking schema changes should introduce a new version rather than silently changing semantics.
- Generated JSON Schema files live under `packages/contracts/generated/json-schema/`.
- Python/backend consumers should use generated JSON Schema files; TypeScript consumers should import from `@careero/contracts`.
- Raw AI outputs, validated normalized outputs, persisted outputs, and rendered outputs must remain separate.

---

## UI/UX Rules

When changing UI:

- Follow existing React, Mantine, route, API-client, and component patterns.
- Keep user flows calm, clear, accessible, and local-first.
- Prefer progressive disclosure over dumping every workflow section onto one screen.
- Preserve user-entered data, especially in intake, parsing, source, and artifact workflows.
- Make loading, success, error, disabled, and empty states explicit.
- Avoid large visual rewrites unless requested.
- Keep forms and validation behavior consistent.

Project-specific UX rules:

- Authenticated pages use the compact app shell/navigation pattern documented in `frontend/README.md`.
- Dashboard, Settings, Career Strategy, Opportunity detail, and Application detail use deep-linkable subsection routes with one focused panel visible at a time.
- Long COMPASS, resume/profile, opportunity description, and structured text should use existing expandable/preview patterns and safe React text rendering.
- AI parsing must populate fields for review and never auto-save.
- Advisor packet surfaces must remain clearly local-only and owner-visible unless hosted collaboration is explicitly approved.
- Google/LinkedIn SSO UI is disabled placeholder behavior only.

---

## AI / Automation Rules

If the project uses AI-assisted parsing, evaluation, generation, recommendations, or automation:

- Keep AI outputs reviewable by the user.
- Do not fabricate user facts, credentials, claims, experience, metrics, compensation, company facts, external research, or decisions.
- Preserve traceability to source material where applicable.
- Distinguish generated drafts from reviewed or submitted artifacts.
- Make uncertainty, missing data, assumptions, warnings, and confidence visible.
- Do not automate irreversible user-facing actions without review.

Project-specific AI rules:

- Deterministic COMPASS scoring is the canonical baseline. Optional OpenAI enrichment must not replace it.
- AI features are disabled by default and require explicit local feature flags plus `CAREERO_OPENAI_API_KEY`.
- OpenAI failures, timeouts, disabled flags, or invalid structured output should produce deterministic fallback/skipped/failed behavior without corrupting persisted records.
- AI prompts must use stored Careero data and user-provided source material; no scraping or external research is implied.
- Prompt/ruleset/model metadata, input hashes, latency, token estimates when available, and sanitized errors support auditability.
- AI usage events must remain metadata-only and must not persist raw prompts, raw resumes, private notes, raw job descriptions, API keys, provider credentials, database URLs, or full exception messages.
- Automation is suggestion-first, review-first, audit-first. External actions, batch approvals, auto-apply, email/calendar mutations, and state-changing automation remain prohibited/future.

---

## Security and Privacy Rules

Never:

- Commit secrets, tokens, credentials, private keys, or `.env` files.
- Log sensitive user data unnecessarily.
- Weaken authentication or authorization.
- Bypass validation to make a test pass.
- Store sensitive data in client-visible locations.
- Add third-party services without approval.
- Change security-sensitive behavior without calling it out.

Project-specific security/privacy rules:

- `backend/.env` may contain local database URLs and API keys; do not print or commit it.
- Passwords use Argon2id via `argon2-cffi`; sessions store server-side token hashes and return raw tokens only in HttpOnly `SameSite=Lax` cookies.
- `CAREERO_AUTH_COOKIE_SECURE=false` is local default only. Production-like environments require HTTPS and hardened cookie/session settings before hosted use.
- Logs must avoid raw resumes, raw job descriptions, raw prompts, private notes, API keys, database URLs, provider credentials, raw session tokens, and password hashes.
- Employer-facing artifacts must never include internal COMPASS notes, ATS risk notes, compensation strategy, company commentary, private decision rationale, or source resume/profile material unless explicitly designed and approved.
- No employer-side, recruiter-side, advisor-side, or public visibility exists without future explicit sharing, revocation, audit, and disclosure design.
- Monetization must not use private job-search data for hidden sponsored recommendations, pay-to-rank behavior, or selling user attention.
- GitLab CI includes SAST and secret detection; do not weaken those checks without approval.

---

## Testing Expectations

When behavior changes:

- Add or update tests.
- Prefer tests near the changed behavior.
- Cover success, failure, edge cases, permission/ownership boundaries, privacy non-leakage, and compatibility aliases where practical.
- Use existing test helpers and fixtures.
- Do not rewrite test infrastructure unless requested.
- Do not delete failing tests without explaining why.

Testing priorities:

1. Contract/schema tests in `packages/contracts`.
2. Backend service/domain logic tests in `backend/tests/`.
3. Backend API route tests in `backend/tests/`.
4. Frontend component/page behavior tests in `frontend/src/**/*.test.tsx`.
5. Migration tests for persistence changes.
6. Regression tests for bugs.
7. Smoke checks through `.\scripts\check-local.ps1` for local readiness.

Database-backed backend tests require `CAREERO_TEST_DATABASE_URL` and a reachable PostgreSQL test database.

---

## Documentation Expectations

Update docs when changes affect:

- Product behavior.
- User workflows.
- API contracts.
- Data models.
- Setup.
- Commands.
- Environment variables.
- Architecture.
- Layer status.
- Roadmap assumptions.
- Security, privacy, AI, automation, or ownership boundaries.

Project-specific docs to keep aligned:

- `README.md`
- `docs/00_start-here.md`
- `docs/01_strategy/00_product-strategy.md`
- `docs/01_strategy/07_revised-build-order-execution-plan.md`
- Relevant layer docs under `docs/02_layers/`
- Relevant domain docs under `docs/03_domain-design/`
- Relevant AI/COMPASS docs under `docs/04_ai-and-compass/`
- Relevant security/privacy/governance docs under `docs/05_security-privacy-governance/`
- `docs/06_operations/local-deployment.md`
- `docs/06_operations/execution-drift-ledger.md`
- `backend/README.md`, `frontend/README.md`, `packages/contracts/README.md`, and `scripts/README.md` when setup/usage changes affect those areas.

Do not treat generated prompts under `docs/07_prompts/` as canonical product docs.

---

## LEAP Recon Expectations

For Careero LEAP Recon:

- Start with this repo section, `docs/00_start-here.md`, `docs/01_strategy/00_product-strategy.md`, `docs/01_strategy/07_revised-build-order-execution-plan.md`, and `docs/06_operations/execution-drift-ledger.md`.
- Read the relevant layer spec under `docs/02_layers/` and related domain/security/AI/operations docs.
- Inspect current code, tests, migrations, package scripts, and README files for actual implementation state.
- Identify implemented, partial, future, stale, conflicting, and archived evidence separately.
- Return Recon only when asked for Recon. Do not implement code changes or generate a final implementation prompt unless the user asks.
- Preserve local-first, review-before-save, review-before-send, no-auto-apply, no-scraping, and user-first boundaries.

Recommended next Recon target from active docs:

`Layer 7 - Opportunity model compatibility and Role-backed persistence boundary`

---

## LEAP Prompt / Implementation Handoff Expectations

When producing or executing an implementation handoff:

- Tie the prompt to one layer/subsection or one explicitly bounded feature.
- Include source-of-truth docs, affected files/modules, current implementation state, compatibility constraints, stop conditions, and validation commands.
- State future-only capabilities that must not be implemented in the slice.
- Include tests and documentation updates in the scope when behavior changes.
- Keep destructive migrations, public API breaks, production auth, billing, hosted collaboration, external integrations, scraping, and state-changing automation out of scope unless explicitly approved.

---

## Commit and Branch Expectations

When the user asks for commits:

- Keep commits scoped and reviewable.
- Use the layer/subsection name in the commit message when available.
- Do not combine unrelated layers.
- Check `git status` before committing.
- Include tests/docs in the same commit when they belong to the change.
- Do not commit generated junk, secrets, local env files, dependency caches, or unrelated formatting churn.

Preferred LEAP commit message:

`Layer X - Short Descriptive Title`

Examples:

`Layer 4D - Workflow Tests and Docs Hardening`

`Layer 7 - Opportunity Model Compatibility`

Branch and PR conventions:

`TBD - What branch naming, PR template, target branch, review, and merge conventions should agents follow? No repository-specific branch/PR convention was discovered.`

---

## Stop Conditions

Stop and ask before:

- Destructive schema or data changes unless explicitly allowed.
- Role-to-Opportunity destructive persistence renames or broad foreign-key churn.
- Changing auth/session/current-user/ownership rules.
- Changing public API contracts in a breaking way.
- Adding paid services, billing, subscriptions, checkout, credits, or external integrations.
- Introducing new production dependencies.
- Removing major existing functionality or compatibility aliases.
- Replacing established architecture.
- Implementing unclear business rules with material product impact.
- Weakening privacy, traceability, auditability, or security controls.
- Enabling scraping, restricted-source extraction, browser-driven collection, automated source polling, or external data collection.
- Implementing hosted collaboration, advisor accounts, invitations, comments, public links, external sharing, or employer/recruiter visibility.
- Implementing production deployment, hosted beta, OAuth/SSO, account recovery, tenant isolation, or production auth hardening without explicit scope.
- Implementing destructive account deletion, anonymization, retention enforcement, or compliance claims.
- Automating job applications, emails, calendar actions, workflow state changes, or externally mutating actions without review and approval.

---

## Completion Requirements

A task is complete when:

- The requested behavior is implemented.
- The change follows existing project patterns.
- Relevant tests/checks were run or clearly explained.
- Docs were updated if needed.
- Risks and follow-ups are called out.
- The implementation stays within the requested LEAP layer/scope.

Final response should include:

- Summary of changes.
- Files/areas changed.
- Tests/checks run.
- Tests/checks not run.
- Known risks or follow-ups.
- Confirmation that the work stayed within the requested LEAP layer/scope.


<!-- LEAP_MASTER_REPO_SECTION_END -->
