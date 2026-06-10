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
   `/prompts/leap-recon-standard.md`
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

# Repository AGENTS.md - Careero LEAP Project Context

## Project Identity

Project name:

`Careero`

Project summary:

Careero is a local-first career operations application for managing a personal job search, evaluating opportunity fit with COMPASS, preparing grounded application materials, and tracking application workflow. The repository is beyond the original Layer 2 prototype and includes local platform, intake/parsing, COMPASS, artifact-generation foundations, application workflow, analytics/intelligence surfaces, local auth, local exports, and local-only advisor packet preview. It is still local-first and must not be treated as production-ready.

Application type and maturity:

- Local-first full-stack web application.
- Current repo status: local MVP / layered implementation, not production hardened.
- Layer 4 is complete for current local MVP workflow scope, Layer 5 is stabilized for current local MVP insight behavior, Layer 6 artifact lifecycle is complete for current local MVP lifecycle scope, and Layer 7 Opportunity compatibility is the next immediate implementation focus.
- Layers 14, 15, and 16 are planning-only in `main` except for adjacent local foundations explicitly documented in strategy docs.

Primary users and use cases:

- Primary user: an individual job seeker managing focused search tracks/workspaces.
- Core use cases: manually capture opportunities, store resume/profile source material, run COMPASS fit evaluations, generate/review local application artifacts, track application states/notes/links/interviews/reminders, inspect local analytics, export local data/artifacts, and preview redacted advisor packets.
- Careero is job-seeker-first. Employer-side, marketplace, sponsored placement, recruiter-facing, and pay-to-rank behavior is future scope and must not distort MVP decisions.

Primary product/architecture docs:

- `README.md` - short project entry point, current capabilities, out-of-scope list, and planning hierarchy.
- `docs/00_start-here.md` - active source-of-truth documentation map and contributor reading order.
- `docs/01_strategy/00_product-strategy.md` - canonical Careero-specific layer status and high-level build order.
- `docs/01_strategy/07_revised-build-order-execution-plan.md` - operational LEAP/LHS prompt sequence, readiness gates, pull-forward rules, and scope discipline.
- `docs/02_layers/00_layer-index.md` and `docs/02_layers/*.md` - canonical LEAP layer specs and capsules.
- `docs/03_domain-design/00_domain-index.md` and linked domain docs - opportunity, workspace, application workflow, artifact, automation, and advisor collaboration models.
- `docs/04_ai-and-compass/00_ai-compass-index.md` - COMPASS, AI governance, usage controls, and prompt-management guidance.
- `docs/05_security-privacy-governance/00_security-privacy-index.md` - auth, account lifecycle, privacy/data governance, and canonical contract boundaries.
- `docs/06_operations/local-deployment.md` - local setup, runtime, migration, seed, smoke, and validation guidance.
- `packages/contracts/README.md` and `packages/contracts/src/*` - executable future-facing canonical platform contracts.

Read the relevant docs before implementing layer, architecture, workflow, data model, or user-facing changes.

Documentation status:

- Active source-of-truth docs carry front matter fields such as `Status: Active`, `Doc Type`, `Layer`, `Source of Truth`, and `Last Reviewed`.
- `docs/07_prompts/*` contains generated LEAP Recon requests, LHS prompts, and Codex execution artifacts. These are not canonical product specs.
- `docs/08_reports-and-audits/*` contains audit evidence and reports. Use as supporting evidence, not primary product truth.
- `docs/99_archive/*` is historical or superseded context only. Do not use it for current planning unless the task explicitly asks for historical comparison.
- Active terminology is COMPASS. STRIDE is legacy terminology and should only appear as historical context unless explicitly explained.

---

## Repository Layout

- `backend/` - FastAPI application, SQLAlchemy models, Alembic migrations, service/API/schema layers, seed command, and backend pytest suite.
- `frontend/` - React + Vite + TypeScript application, Mantine UI, React Router pages, API clients, components, and Vitest component/page tests.
- `packages/contracts/` - TypeScript/Zod canonical contracts, provider-neutral COMPASS helpers, generated JSON Schema, and contract tests.
- `shared/` - reserved for runtime-agnostic shared utilities that do not belong to a package yet. Current canonical contracts live in `packages/contracts`.
- `workers/` - reserved for future local worker processes. No background job engine is implemented.
- `docs/` - product strategy, LEAP layers, domain design, AI/COMPASS, security/privacy/governance, operations, prompts, reports, and archive.
- `scripts/` - PowerShell developer automation for backend/frontend start/stop, migrations, seed, tests, and local readiness checks.
- `infra/` - reserved for future infrastructure documentation/configuration. No cloud deployment logic is implemented.
- `.gitlab-ci.yml` - GitLab security templates for SAST and secret detection.

If the repository structure changes, update this section.

---

## Technology Stack

- Frontend: React 19, Vite 7, TypeScript 5.8, Mantine 9, React Router 7, Tabler icons, Testing Library, jsdom, Vitest.
- Backend/API: Python FastAPI, SQLAlchemy, Pydantic Settings, Alembic, Uvicorn, psycopg, Argon2 password hashing, OpenAI SDK for optional local AI features.
- Database: PostgreSQL with Alembic migrations. Local dev uses `careero`; tests use `careero_test`.
- Contracts: TypeScript, Zod, zod-to-json-schema, generated JSON Schema under `packages/contracts/generated/json-schema/`.
- Document/file handling: `python-docx`, `pypdf`, and FastAPI multipart uploads for local resume/profile source import; backend artifact export supports Markdown/DOCX/PDF.
- Infrastructure: local-first only. `infra/` says no AWS or other cloud deployment logic exists.
- Package managers: `pip` for backend dependencies; `npm` for frontend and contracts.
- Test frameworks: `pytest` for backend, `vitest` for frontend and contracts.
- Runtime versions: README requires Python 3.11+, Node.js 20+, npm, and PostgreSQL. No pinned `.python-version`, `.nvmrc`, or Docker runtime file was found.

Use the existing stack unless the user explicitly requests evaluation or migration.

---

## Setup Commands

Use the repository's existing setup process. Commands below are evidence-backed by README and operations docs.

Create local PostgreSQL role/databases:

```sql
CREATE ROLE careero WITH LOGIN PASSWORD 'careero';
CREATE DATABASE careero OWNER careero;
CREATE DATABASE careero_test OWNER careero;
```

Backend setup from repo root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edit `backend/.env` for local PostgreSQL and optional AI settings. Do not commit real secrets.

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

Do not invent setup commands. If the command is unclear, inspect the repo first.

---

## Development Commands

Root PowerShell scripts:

```powershell
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
.\scripts\start-all.ps1
.\scripts\stop-all.ps1
.\scripts\migrate.ps1
.\scripts\seed.ps1
.\scripts\test.ps1
.\scripts\check-local.ps1
```

If PowerShell blocks local scripts:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-local.ps1
```

Manual backend runtime:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Manual frontend runtime:

```powershell
cd frontend
npm run dev
```

Local URLs:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173` or `http://localhost:5173`
- Health: `http://127.0.0.1:8000/health`
- Database health: `http://127.0.0.1:8000/health/database`
- Registration: `http://127.0.0.1:5173/register`

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`, so start the backend first for authenticated workflows.

---

## Validation Commands

Use the most relevant validation commands for the changed area.

Backend tests:

```powershell
cd backend
$env:CAREERO_TEST_DATABASE_URL="postgresql://careero:careero@localhost:5432/careero_test"
pytest
```

Frontend tests:

```powershell
cd frontend
npm run test
```

Frontend build/typecheck:

```powershell
cd frontend
npm run build
```

Contracts validation:

```powershell
cd packages/contracts
npm run validate
```

Contracts targeted commands:

```powershell
cd packages/contracts
npm run build
npm run generate:json-schema
npm run test
```

Root local readiness:

```powershell
.\scripts\check-local.ps1
```

Formatting/linting:

- No repo-level formatter command was found.
- No frontend lint script or ESLint/Prettier config was found.
- No Python formatting/lint config such as `pyproject.toml`, `ruff`, `black`, `pytest.ini`, `tox.ini`, or `setup.cfg` was found.

If only part of the repo changed, prefer targeted checks first. Run broader checks when practical. If a command is missing, broken, blocked by PostgreSQL, or too expensive to run, explain that in the final response.

---

## LEAP Project Rules

This repository should be implemented in bounded LEAP units.

When a task references a layer, phase, subsection, milestone, or roadmap item:

1. Locate the corresponding documentation.
2. Confirm the existing implementation state.
3. Identify affected models, routes, services, components, tests, and docs.
4. Implement only the requested layer/subsection unless a prerequisite is required.
5. Preserve compatibility with completed prior layers.
6. Update relevant tests and docs.
7. Summarize remaining gaps.

Do not skip ahead into later layers unless the user explicitly asks.

Repo-specific LEAP Recon expectations:

- Start with `AGENTS.md`, `README.md`, `docs/00_start-here.md`, `docs/01_strategy/00_product-strategy.md`, `docs/01_strategy/07_revised-build-order-execution-plan.md`, the relevant `docs/02_layers/*` layer doc, relevant domain/AI/security docs, and existing implementation/tests.
- Read `docs/06_operations/execution-drift-ledger.md` before planning implementation work.
- Treat `docs/07_prompts/*` as prompt history/templates only, not canonical product truth.
- Treat `docs/08_reports-and-audits/*` as supporting audit evidence only.
- Return Recon only when the user asks for LEAP Recon. Do not implement or generate a final implementation prompt unless asked.
- For Layer 7, explicitly distinguish product-facing `Opportunity` terminology from current Role-backed persistence.
- For Layers 14, 15, and 16, confirm that the requested work is not planning-only before implementing.

LEAP Prompt / implementation handoff expectations:

- Reconcile any House Standard, LHS, LEAP, or Codex implementation prompt against current repo reality before editing.
- Identify affected backend services/API/schema/models/migrations, frontend API/types/pages/components, contracts, tests, and docs.
- Keep implementation slices aligned to one layer/subsection unless a minimal prerequisite is required.
- Preserve local-first behavior and document any production-readiness gap instead of silently solving it through broad scope expansion.
- Update docs only when the user asks or when behavior/contracts/setup actually change.

---

## Project Source of Truth

Use this order of truth when making decisions:

1. Explicit user instruction for the current task.
2. Current repository code and tests.
3. Repository `AGENTS.md` and scoped `AGENTS.md` / `AGENTS.override.md` files.
4. Product strategy and architecture docs.
5. Layer/roadmap docs.
6. README and setup docs.
7. Existing issue/task text.
8. Reasonable inference from nearby patterns.

If these conflict, call out the conflict and prefer the more specific, more recent, and safer source.

Careero-specific truth notes:

- Product strategy and layer status: `docs/01_strategy/00_product-strategy.md`.
- Execution order and readiness gates: `docs/01_strategy/07_revised-build-order-execution-plan.md`.
- Canonical layer specs: `docs/02_layers/*`.
- Local dev operations: `docs/06_operations/local-deployment.md` and `scripts/README.md`.
- Current capability and out-of-scope summary: `README.md`.
- Future-facing executable contracts: `packages/contracts`.
- Archived roadmap material under `docs/99_archive/*` must not drive current implementation.

---

## Architecture Rules

Follow the project's existing architecture.

Default expectations:

- Keep domain logic out of presentation-only code when possible.
- Keep API contracts explicit.
- Keep validation close to data boundaries.
- Reuse existing schema, type, and DTO patterns.
- Avoid duplicating model definitions.
- Preserve ownership and authorization boundaries.
- Keep persistence concerns isolated according to existing repository patterns.
- Prefer incremental extension over replacement.
- Avoid broad rewrites unless the user requested a refactor.

Project-specific architecture constraints:

- Backend uses a layered FastAPI structure: `app/api` routes, `app/schemas` request/response models, `app/services` domain logic, `app/repositories` where present, `app/models.py` SQLAlchemy persistence, and Alembic migrations.
- Frontend uses typed API clients under `frontend/src/api`, frontend DTO/types under `frontend/src/types`, pages under `frontend/src/pages`, reusable components under `frontend/src/components`, and route-driven subsection UX.
- Contract evolution should prefer `packages/contracts` and generated JSON Schema for cross-runtime canonical shapes. Python should consume generated JSON Schema where needed; it should not import TypeScript directly.
- Current persistence remains Role-backed for opportunities. Do not perform a destructive Role-to-Opportunity rename without explicit approval and migration scope.
- Keep strategy synthesis read-only and based on stored Careero evidence only. Do not create durable hidden strategy memory or external-market-data behavior unless explicitly scoped.
- Keep automation suggestion-first, review-first, and audit-first. Do not add external or state-changing automation without explicit approval.
- Keep local advisor packet behavior owner-visible and local-only unless hosted collaboration is explicitly scoped.

---

## Data and Migration Rules

Before changing schemas, migrations, seed data, or persistence behavior:

- Inspect existing models and migrations.
- Determine whether the project is prototype, staging, or production-like.
- Preserve existing data unless destructive changes are explicitly allowed.
- Keep migrations reversible where practical.
- Update tests and docs for data model changes.
- Do not silently change identifiers, ownership semantics, or lifecycle states.

Project-specific data rules:

- PostgreSQL is the local persistence backend. Alembic migrations live under `backend/alembic/versions`.
- Tests run migrations against `CAREERO_TEST_DATABASE_URL` and reset the known Careero schema in that test database.
- Seed is idempotent and creates/updates `local-user@careero.local`, canonical job sources, and the seeded default workspace for seed/direct-service compatibility. The seeded user has no password and is not a public login path.
- Registered users receive their own workspace. Preserve current-user ownership boundaries and seeded-user compatibility paths where documented.
- Resume/profile file import extracts text for preview only; it must not persist uploaded files until the user saves source text. Supported imports are `.txt`, `.md`, `.docx`, and text-based `.pdf` up to 5 MB. OCR is not implemented.
- Local data export and account lifecycle request tracking are local-first. Lifecycle requests record audit requests only and do not delete or anonymize data.
- Source snapshots, managed deltas, durable strategy tables, hosted export/delete, retention enforcement, and destructive account deletion are future unless explicitly scoped.

---

## API and Contract Rules

When changing APIs, contracts, schemas, or shared types:

- Preserve backward compatibility unless explicitly told otherwise.
- Update shared types and validation together.
- Update API tests.
- Update docs or examples.
- Keep error responses consistent with existing patterns.
- Avoid creating parallel contract definitions.

Project-specific contract rules:

- Preserve compatibility aliases such as older `/api/roles` paths while Opportunity-facing compatibility is in progress, unless a task explicitly approves breaking changes.
- Application workflow authority is `Application.current_state`; `Role.status` remains a lightweight opportunity status for existing role lists.
- Artifact lifecycle transitions are `draft -> reviewed -> submitted`, with `draft`, `reviewed`, and `submitted` each allowed to move to `archived`. Submitted artifact edits create a new draft revision instead of mutating the submitted record.
- API responses must not expose raw prompts, API keys, full raw role descriptions, full resume/profile source text, generated document content, or raw model payloads unless an endpoint is explicitly designed for that local owner-visible purpose.
- Breaking contract changes in `packages/contracts` should introduce a new contract version rather than silently changing existing semantics.

---

## UI/UX Rules

When changing UI:

- Follow existing component and styling patterns.
- Keep user flows calm, clear, and accessible.
- Prefer progressive disclosure over clutter.
- Preserve user-entered data.
- Make loading, success, error, and empty states explicit.
- Avoid large visual rewrites unless requested.
- Keep forms and validation behavior consistent.

Project-specific UX rules:

- Frontend uses Mantine and existing component/page patterns. Keep global navigation limited to implemented destinations.
- Authenticated app sections use route-driven, deep-linkable subsections and one focused detail panel at a time for dashboard, strategy, settings, opportunity detail, and application detail.
- Long read-only resume/profile, opportunity description, COMPASS, and structured text should use existing expandable/Markdown-safe preview patterns where appropriate.
- Parsing and AI generation must be review-before-save. The Add Opportunity parser fills empty fields only, never auto-saves, and must preserve manual edits.
- Local reminders, interviews, advisor packets, and exports must present their local-only nature honestly. Do not imply cloud scheduling, email delivery, hosted sharing, advisor accounts, or external sync unless implemented.

---

## AI / Automation Rules

If the project uses AI-assisted parsing, evaluation, generation, recommendations, or automation:

- Keep AI outputs reviewable by the user.
- Do not fabricate user facts, credentials, claims, experience, metrics, or decisions.
- Preserve traceability to source material where applicable.
- Distinguish generated drafts from reviewed or submitted artifacts.
- Make uncertainty visible.
- Do not automate irreversible user-facing actions without review.

Project-specific AI rules:

- AI features are optional and disabled by default through backend env flags.
- Deterministic COMPASS scoring is the canonical baseline. Optional OpenAI enrichment may add grounded analysis but must not replace baseline scoring.
- AI prompts must be grounded in stored role/opportunity fields, deterministic baseline, COMPASS rules, request context, and active resume/profile source when available.
- AI outputs must distinguish evidence matches, evidence gaps, unsupported claim warnings, and insufficient data. Missing experience or facts must not be fabricated.
- AI role parsing returns structured fields for user review and never creates an opportunity by itself.
- Resume and cover-letter generation must pass canonical schema and truthfulness validation. Employers, roles, technologies, metrics, credentials, and experience must come from supplied source material or explicit user input.
- Usage and cost controls are local-first metadata only today. No credit wallet, billing, paid quotas, durable credit ledger, model catalog, prompt gateway, or prompt-only export exists in `main`.
- Automation suggestions, approval logs, and preferences exist locally. External actions, batch approvals, automated application submission, and silent workflow state mutation remain prohibited/future.

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

- `backend/.env` is local configuration and must not be committed with real secrets. `CAREERO_OPENAI_API_KEY` is intentionally empty in local setup.
- Local password auth uses Argon2id and HttpOnly SameSite=Lax session cookies backed by server-side SHA-256 session-token hashes. `CAREERO_AUTH_COOKIE_SECURE=false` is a local default only; production-like environments must use HTTPS and harden cookie/session settings first.
- Google/LinkedIn SSO buttons are disabled placeholders. OAuth, email verification, MFA, account recovery, hosted auth provider selection, and tenant isolation remain future.
- Logs should include IDs/status/latency only where possible and must not include prompts, API keys, raw job descriptions, full resume/profile text, compensation strategy, generated artifacts, or raw model payloads.
- Advisor packet preview/export is redacted by default and local-only. Private notes, raw job descriptions, COMPASS rationale, ATS risk, compensation strategy, recruiter/contact details, source resume/profile material, career strategy synthesis, activity logs, automation logs, and generated artifact content are excluded by default.
- CI currently includes GitLab SAST and secret-detection templates. Do not weaken secret-detection or commit local secrets.

---

## Testing Expectations

When behavior changes:

- Add or update tests.
- Prefer tests near the changed behavior.
- Cover success, failure, and edge cases where practical.
- Use existing test helpers and factories.
- Do not rewrite test infrastructure unless requested.
- Do not delete failing tests without explaining why.

Testing priorities:

1. Contract/schema tests.
2. Service/domain logic tests.
3. API route tests.
4. UI behavior tests.
5. Regression tests for bugs.
6. Smoke tests for critical workflows.

Repo-specific test guidance:

- Backend behavior changes should usually add/update tests under `backend/tests`.
- Frontend behavior changes should usually add/update colocated or nearby `*.test.tsx` tests under `frontend/src`.
- Contract/schema changes should update `packages/contracts` tests and regenerate JSON Schema.
- Database behavior changes should include migration coverage, usually via existing migration tests.
- Auth, ownership, export, lifecycle, advisor packet, AI, automation, and data-boundary changes require negative/edge-case coverage, not just success paths.

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

Project-specific docs to keep aligned:

- `README.md`
- `docs/00_start-here.md`
- `docs/01_strategy/00_product-strategy.md`
- `docs/01_strategy/07_revised-build-order-execution-plan.md`
- Relevant `docs/02_layers/*` layer docs.
- Relevant `docs/03_domain-design/*`, `docs/04_ai-and-compass/*`, `docs/05_security-privacy-governance/*`, and `docs/06_operations/*` docs.
- `backend/README.md`, `frontend/README.md`, `scripts/README.md`, and `packages/contracts/README.md` when setup/API/package behavior changes.

---

## Commit and Branch Expectations

When the user asks for commits:

- Keep commits scoped and reviewable.
- Use the layer/subsection name in the commit message when available.
- Do not combine unrelated layers.
- Check `git status` before committing.
- Include tests/docs in the same commit when they belong to the change.

Preferred LEAP commit message:

`Layer X - Short Descriptive Title`

Examples:

`Layer 4B - Application Timeline and Notes Workflow`

`Layer 6C - Versioning, Review, and Submitted-State Workflow`

Repo-specific status:

- No project-specific branch naming convention was found.
- No PR template or review checklist was found.
- `.gitlab-ci.yml` exists for SAST and secret detection only; no test/build CI jobs were found.

---

## Stop Conditions

Stop and ask before:

- Destructive schema or data changes unless the project explicitly allows them.
- Changing auth/session/ownership rules.
- Changing public API contracts in a breaking way.
- Adding paid services or external integrations.
- Introducing new production dependencies.
- Removing major existing functionality.
- Replacing established architecture.
- Implementing unclear business rules with material product impact.
- Weakening privacy, traceability, auditability, or security controls.

Project-specific stop conditions:

- Any destructive Role-to-Opportunity persistence rename or foreign-key migration.
- Hosted auth, OAuth/SSO, account recovery, MFA, tenant isolation, or production authorization hardening.
- Billing, subscriptions, credit wallets, paid quotas, or model-cost enforcement.
- Production deployment architecture, cloud infrastructure, external storage, backup/restore, monitoring, or support operations.
- External integrations requiring OAuth, credentials, provider terms review, or external token storage.
- Scraping, restricted-source extraction, browser-driven collection, or terms-sensitive job-source ingestion.
- Automated job application submission, external communication, calendar/email delivery, or state-changing automation.
- Hosted advisor collaboration, public links, advisor accounts, invitations, comments, revocation, or external sharing.
- Account deletion/anonymization/retention enforcement beyond local lifecycle request tracking.
- Business rules that affect user-facing career advice, scoring, monetization, privacy, or employer-side incentives and are not documented.

---

## External Services and Environment

- Required local service: PostgreSQL.
- Optional external service: OpenAI, controlled by backend environment flags and API key.
- Not implemented: Google Docs import, Gmail/Outlook integration, calendar sync, LinkedIn/job-board helpers, browser extension/share-sheet intake, official ATS/job-source provider adapters, hosted collaboration, billing, cloud deployment, queues, background jobs, caches, or cloud object storage.
- `workers/` is reserved; no queue or background job runtime exists.
- `infra/` is reserved; no deployment infrastructure exists.

---

## Known Unknowns / TBD

- `TBD: What branch naming convention should agents use for LEAP work?`
- `TBD: What PR template, review checklist, or merge criteria should agents follow?`
- `TBD: Should the repo standardize Python and frontend formatting/linting commands? None were found.`
- `TBD: Should runtime versions be pinned in files such as .python-version or .nvmrc? README currently states Python 3.11+ and Node.js 20+.`
- `TBD: What hosted deployment target, if any, is intended after Layer 11 readiness gates pass?`
- `TBD: Are Alembic migrations expected to be fully reversible for all future production-like changes?`

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

<!-- LEAP_MASTER_REPO_SECTION_END -->
