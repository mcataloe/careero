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

When the user invokes a LEAP command, route it to current LEAP Framework behavior instead of responding generically. Use `docs/leap.md` as the lifecycle reference and the current prompt files when available.

| Command | Route and behavior |
| --- | --- |
| `Run LEAP Charter` | Use `prompts/leap-charter-standard.md` to establish or reconcile project direction, source truth, roadmap, baseline assumptions, and implementation posture. |
| `Run LEAP Recon` | Use `prompts/leap-recon-standard.md` to investigate a focused feature, risk, layer, dependency, contract, repo area, or architecture question before implementation planning. |
| `Generate LEAP Prompt` | Use `prompts/leap-prompt-standard.md` only after source truth, repo reality, scope, validation, stop conditions, and execution configuration are clear enough. |
| `Run LEAP Prompt` | Execute or apply an already-approved LEAP Prompt according to its stated scope, constraints, validation, and stop conditions. |
| `Generate LEAP LHS` | Generate a staged LEAP Prompt format only when implementation gravity warrants Build Units; LHS is not a mandatory lifecycle phase. |
| `Run LEAP LHS` | Execute or apply an approved LHS prompt in Build Unit sequence with its validation and stop conditions. |
| `Run LEAP Governance` | Use `prompts/leap-governance-pass-standard.md` for source-truth, framework, prompt-library, adoption, terminology, or docs drift. |
| `Run LEAP Validation` | Verify completed work against scope, tests/checks, docs, acceptance criteria, and stop conditions. |
| `Run LEAP Handoff` | Summarize completed work, unresolved risks, validation status, deviations, and recommended follow-up. |

Default Recon behavior:

1. Use the repository-level `AGENTS.md` first.
2. Inspect the current repository state.
3. Use the current LEAP Recon Standard Operational Prompt from the LEAP framework repository:
   `/prompts/leap-recon-standard.md`
4. Use source-of-truth documents identified by the repository-level `AGENTS.md`.
5. Perform the Recon Baseline Freshness Check using repository AGENTS.md, baseline metadata if present, source-truth docs, and relevant repo reality.
6. Return Recon only.
7. Do not implement code changes.
8. Do not generate the final LEAP implementation prompt unless the user asks after Recon.

LEAP Charter is not required before every Recon. If the baseline is fresh enough, continue Recon. If minor drift exists, continue and disclose the limitation. If material drift exists, ask whether to run Brownfield Charter or LEAP Governance, continue with limited scope, or defer reconciliation. If source-truth conflict would make Recon unsafe or misleading, stop and recommend reconciliation.

If the LEAP standard prompt, `docs/leap.md`, or repository-level `AGENTS.md` cannot be read, stop and explain what source is unavailable.

The user should not need to paste full framework prompt standards when using standard AGENTS.md behavior.

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

# Repository AGENTS.md - Careero

## Project Identity

Careero is a local-first career operations application for managing a personal job search, evaluating opportunity fit, preparing grounded application materials, and tracking application workflow. It is organized around LEAP layers and a COMPASS-powered evaluation model.

Current maturity: local MVP / local-first product foundation. The repository is beyond the original Layer 2 prototype and includes local platform, intake, COMPASS, artifact-generation foundations, application workflow, insight surfaces, local auth, local data export/readiness surfaces, and local-only advisor packet preview. It is not production-ready.

Primary users/use cases: job seekers managing one or more search tracks/workspaces, manually saving opportunities, grounding evaluations in resume/profile sources, reviewing COMPASS fit/risk/priority signals, preparing resume and cover-letter drafts, and tracking applications through local workflow records.

## LEAP Baseline State

| Item | Value |
| --- | --- |
| Baseline record | Inline in `AGENTS.md` |
| Last full reconcile | `Never` |
| Last reconcile mode | `Never` |
| Current source-truth entry point | `docs/00_start-here.md` |
| Canonical docs location | `docs/` |
| Archive location | `docs/99_archive/` |
| Gap register / known drift | `docs/06_operations/execution-drift-ledger.md`; `docs/08_reports-and-audits/repo-reconciliation-recon.md` is audit evidence, not canonical strategy |
| Baseline confidence | `Medium` |
| Reconcile triggers | Major roadmap change; architecture pivot; source-truth conflict; stale `AGENTS.md`; large new layer; production auth/deployment/billing work; destructive Role-to-Opportunity migration; external integrations; hosted collaboration; employer-side features |

`leap.baseline.yaml` is not present. Do not create it unless the owner explicitly authorizes a baseline setup pass. Optional follow-up: add `leap.baseline.yaml` if machine-readable baseline tracking becomes useful.

Primary product/architecture docs:

- `README.md` - short project entry point, local capabilities, out-of-scope list, and planning hierarchy.
- `docs/00_start-here.md` - documentation map and source-of-truth rules.
- `docs/01_strategy/00_product-strategy.md` - canonical Careero-specific layer status and high-level build order.
- `docs/01_strategy/07_revised-build-order-execution-plan.md` - actionable LEAP/LHS prompt sequence, readiness gates, pull-forward rules, and scope discipline.
- `docs/02_layers/00_layer-index.md` - canonical layer specs.
- `docs/03_domain-design/00_domain-index.md` - domain model design references.
- `docs/04_ai-and-compass/00_ai-compass-index.md` - COMPASS, AI governance, and prompt/cost-control references.
- `docs/05_security-privacy-governance/00_security-privacy-index.md` - privacy, auth, account lifecycle, and canonical contract boundaries.
- `docs/06_operations/local-deployment.md` - local setup, run, and validation guidance.
- `docs/06_operations/execution-drift-ledger.md` - current drift/risk memory.
- `packages/contracts/README.md` and `docs/05_security-privacy-governance/canonical-domain-model.md` - canonical contracts and migration guidance.

Generated prompts under `docs/07_prompts/` are execution artifacts and are not source-of-truth design docs. `docs/99_archive/` is historical only unless a task explicitly asks for historical comparison.

## Repository Layout

- `backend/` - FastAPI backend, SQLAlchemy models/services/schemas/routes, Alembic migrations, backend tests, and local `.env.example`.
- `frontend/` - React 19 + Vite + TypeScript app, Mantine UI, Vitest component tests, and Vite `/api` proxy to the backend.
- `packages/contracts/` - TypeScript/Zod canonical contracts, generated JSON Schema files, fixtures, contract tests, and provider-neutral COMPASS helpers.
- `docs/` - active strategy, layer specs, domain design, AI/COMPASS, security/privacy/governance, operations, prompts, reports, and archive docs.
- `scripts/` - PowerShell local dev helpers for starting/stopping services, migrations, seed, tests, and readiness checks.
- `infra/` - reserved for future infrastructure documentation/configuration; no production cloud deployment logic currently exists.
- `shared/` - reserved for future shared schemas/utilities.
- `workers/` - reserved for future local worker processes; no background job execution is implemented.
- `.gitlab-ci.yml` - GitLab SAST and secret-detection templates.

## Technology Stack

- Frontend: React 19, TypeScript 5.8, Vite 7, Mantine 9, React Router 7, Tabler icons, Vitest, Testing Library, jsdom.
- Backend/API: Python 3.11+, FastAPI, SQLAlchemy, Alembic, Pydantic Settings, Uvicorn, httpx/pytest tests.
- Database: local PostgreSQL with Alembic migrations; test database uses `CAREERO_TEST_DATABASE_URL`.
- Contracts: TypeScript/Zod package `@careero/contracts`, generated JSON Schema for backend/AI validation, Vitest tests.
- AI/provider dependencies: optional OpenAI Responses API use through backend services; AI features are disabled by default and require local env flags plus `CAREERO_OPENAI_API_KEY`.
- Auth: first-party local email/password auth using Argon2id hashes, server-side sessions, and HttpOnly `SameSite=Lax` cookies; not production-hardened.
- Infrastructure: local scripts only; no Docker, Terraform, Kubernetes, AWS, or hosted deployment implementation is documented in repo evidence.
- Package managers: npm for `frontend/` and `packages/contracts/`; Python `venv` + `pip` requirements files for `backend/`.
- Runtime versions: Python 3.11+, Node.js 20+, npm, PostgreSQL.

## Setup And Development Commands

Run from repository root in PowerShell unless noted.

Backend setup:

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

Create local PostgreSQL role/databases before migrations if needed:

```sql
CREATE ROLE careero WITH LOGIN PASSWORD 'careero';
CREATE DATABASE careero OWNER careero;
CREATE DATABASE careero_test OWNER careero;
```

Frontend setup:

```powershell
cd frontend
npm install
npm run dev
```

Contracts setup:

```powershell
cd packages/contracts
npm install
npm run validate
```

Root helper scripts:

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

If PowerShell blocks scripts, use `powershell -ExecutionPolicy Bypass -File .\scripts\check-local.ps1`. If PowerShell blocks `npm.ps1`, use `npm.cmd`.

## Validation Commands

Use targeted checks first, then broader checks when practical.

Backend targeted tests:

```powershell
cd backend
$env:CAREERO_TEST_DATABASE_URL="postgresql://careero:careero@localhost:5432/careero_test"
pytest
```

Root test helper:

```powershell
.\scripts\test.ps1
```

`tests.ps1` requires `backend/.venv`, always runs selected backend unit tests, runs database-backed backend tests only when `CAREERO_TEST_DATABASE_URL` is set and reachable, then runs frontend tests and build.

Frontend checks:

```powershell
cd frontend
npm run test
npm run build
```

Contracts checks:

```powershell
cd packages/contracts
npm run build
npm run generate:json-schema
npm run test
npm run validate
```

Local smoke/readiness check, with backend/frontend already running:

```powershell
.\scripts\check-local.ps1
```

No repo-level lint or format command was found. Do not invent one; use local formatter conventions only when evident in touched files.

## Local Services And Dependencies

- PostgreSQL must be running locally and reachable from `CAREERO_DATABASE_URL` and `CAREERO_TEST_DATABASE_URL`.
- Backend defaults are in `backend/app/config.py` and `backend/.env.example`; real `backend/.env` is local-only and must not be committed.
- Backend health checks: `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/health/database`.
- Frontend dev server: `http://localhost:5173`; Vite proxies `/api` to `http://127.0.0.1:8000`.
- OpenAI-backed parsing/evaluation/artifact generation is optional and disabled by default. Deterministic COMPASS evaluation must continue to work without an API key.
- No queue, cache, background worker, cloud storage, OAuth provider, billing provider, email provider, calendar provider, ATS/job-source provider, or hosted collaboration service is implemented.

## Source-Truth And Drift Rules

Use this order for Careero-specific decisions:

1. Current user task.
2. Current code, tests, and migrations.
3. This editable repository section of `AGENTS.md`.
4. `README.md` and `docs/00_start-here.md`.
5. `docs/01_strategy/00_product-strategy.md` and `docs/01_strategy/07_revised-build-order-execution-plan.md`.
6. Active layer specs under `docs/02_layers/` and active domain/security/AI/operations docs.
7. `docs/06_operations/execution-drift-ledger.md` and active reports/audits as supporting evidence.
8. Generated prompts under `docs/07_prompts/` only as execution history, not canonical design.
9. `docs/99_archive/` only for historical comparison.

Known drift/stale-document risks:

- `docs/08_reports-and-audits/repo-reconciliation-recon.md` and older layer recon summaries contain earlier findings and may conflict with active strategy docs after later implementation. Treat them as audit history unless current docs reference them for evidence.
- Some docs distinguish product-facing `Opportunity` from current Role-backed persistence. Do not perform destructive Role-to-Opportunity renames without separate approval.
- Layer 11 readiness/auth docs describe local foundations only. Do not treat local auth/readiness/entitlement/export surfaces as hosted production readiness.
- Layer 12 advisor packet work is local-only and owner-visible. Do not treat preview/export as hosted sharing or collaborator permissions.

## Architecture Rules

- Preserve the local-first architecture unless the owner explicitly approves hosted/productization work.
- Keep backend domain behavior in services/repositories/schemas/routes following existing FastAPI patterns; do not move business rules into frontend-only code.
- Keep frontend API types and clients aligned with backend response shapes; prefer existing component/page patterns and routed subsection workspaces.
- Treat `packages/contracts` as canonical future-facing platform contracts. TypeScript consumers import from `@careero/contracts`; Python/backend consumers use generated JSON Schema files and must not import TypeScript directly.
- Preserve Role-backed persistence while using Opportunity-facing API/product language until a separate migration is approved.
- Keep `ActivityLog` as audit/event support, not the source of truth for typed workflow persistence.
- Keep application timeline as an aggregate view over typed records unless a documented need justifies a durable timeline model.
- Avoid adding production dependencies, external services, or architectural rewrites without explicit approval.

## Data And Migration Rules

- Inspect `backend/app/models.py`, services/repositories, and `backend/alembic/versions/` before changing persistence.
- Prefer additive Alembic migrations. Destructive migrations, identifier changes, and Role-to-Opportunity table/model/foreign-key renames require explicit human approval.
- Preserve user-owned data, source lineage, hashes, lifecycle metadata, audit metadata, and workspace/user ownership boundaries.
- Test database-backed changes against `CAREERO_TEST_DATABASE_URL` when possible.
- Seed behavior must remain idempotent. The seeded local user is compatibility support only and is not a public login path.

## API And Contract Rules

- Preserve backward compatibility for existing `/api/roles` compatibility routes while Opportunity-facing APIs are staged.
- Keep API validation and schemas explicit in backend schema modules and service boundaries.
- Update frontend API clients/types, backend tests, frontend tests, and contracts docs/tests when response contracts change.
- AI outputs must validate against structured schemas/contracts before persistence or completed-state use.
- Breaking contract changes in `packages/contracts` require versioning consideration; do not silently change `careero.contracts.v1` semantics.

## UI/UX Rules

- Follow existing React/Mantine patterns, routed feature workspaces, compact app shell navigation, and deep-linkable subsection routes.
- Keep UI local-first and honest about disabled/future functionality such as OAuth, hosted sharing, notifications, integrations, billing, and support workflows.
- Preserve user-entered form data, make loading/error/empty states explicit, and use existing expandable text/section navigation patterns for long structured content.
- Do not add marketing/landing-page behavior unless explicitly requested; build product workflow surfaces.

## AI, Automation, Security, And Privacy Rules

- AI provider calls are opt-in through local env flags and API keys. Deterministic fallbacks must remain available where documented.
- Do not fabricate user facts, resume facts, experience, credentials, compensation, company facts, external research, or application decisions.
- Do not log or persist raw prompts, raw resumes/profile sources, raw job descriptions, private notes, API keys, provider credentials, database URLs, plaintext passwords, password hashes, raw session tokens, or cookie values outside approved storage paths.
- Employer-facing artifacts must not include internal COMPASS notes, ATS risk notes, compensation strategy, private decision rationale, source resume text, or other internal strategy material.
- Automation remains suggestion/review-first. Do not add external actions, auto-apply behavior, state-changing automation, email/calendar mutation, or batch approvals without fresh approval.
- Local data export must not include environment variables, secrets, database URLs, provider credentials, or unrelated users' records.
- Production auth hardening, account recovery, SSO/OAuth, tenant isolation, retention enforcement, billing, credits, hosted deployment, and support workflows are future work requiring explicit approval.

## LEAP Recon Expectations

For any LEAP Recon in this repo:

1. Read `docs/00_start-here.md`, `docs/01_strategy/00_product-strategy.md`, `docs/01_strategy/07_revised-build-order-execution-plan.md`, `docs/06_operations/execution-drift-ledger.md`, and the relevant layer/domain/security/AI docs.
2. Inspect current code, tests, migrations, package manifests, and local scripts for the touched area.
3. Perform the Baseline Freshness Check using the table above and note that no `leap.baseline.yaml` exists.
4. Inspect dependency/contract evidence when touching APIs, contracts, AI providers, generated clients/schemas, auth, integrations, infrastructure, events, billing, or external services. `leap.dependencies.yaml` is not present.
5. Return Recon only unless the user explicitly asks to generate or run an implementation prompt.

Recommended next LEAP Recon target from current docs: Layer 7 Opportunity model compatibility / Role-backed Opportunity transition.

## LEAP Prompt And Handoff Expectations

Implementation prompts should state the layer/subsection, source docs consulted, exact files/modules expected to change, compatibility constraints, validation commands, stop conditions, and whether docs need updates. Keep prompts scoped to one bounded LEAP unit.

Handoffs should report files changed, behavior changed, tests/checks run, tests/checks not run, source-truth deviations, known drift, and whether the work stayed within layer scope.

## Commit, Branch, And Worktree Expectations

- Current local branch observed during AGENTS population: `main`.
- Remotes observed: `origin`/`github` on GitHub and `gitlab` on GitLab.
- No project-specific branch naming convention was found. `TBD`: What branch naming and PR target rules should agents follow?
- Check `git status` before committing. Do not commit untracked/local files such as `.env`, virtual environments, `node_modules`, build outputs, logs, caches, or unrelated generated files.
- When asked to commit LEAP work, use the relevant layer/subsection in the commit message when available, for example `Layer 7 - Opportunity Compatibility`.

## Stop Conditions Requiring Human Review

Stop and ask before:

- Destructive schema/data changes, including Role-to-Opportunity persistence renames or foreign-key churn.
- Hosted deployment, production auth hardening, OAuth/SSO, account recovery, tenant isolation, billing, credits, paid quotas, or external service setup.
- Adding or changing OpenAI/provider usage beyond existing optional local feature flags.
- Adding scraping, restricted-source extraction, browser-driven external collection, ATS/job-board provider ingestion, or API-source polling.
- Implementing hosted advisor collaboration, public links, invitations, comments, external sharing, employer/recruiter visibility, marketplace, sponsored placement, or pay-to-rank features.
- Automating external actions, application submission, email/calendar mutation, or state changes without explicit user review.
- Weakening privacy, traceability, auditability, auth/session handling, or source-grounding rules.
- Changing canonical contracts in a breaking way or replacing established architecture.

## Completion Requirements

A task is complete when the requested behavior is implemented within the requested LEAP scope, follows existing repo patterns, preserves local-first/security/privacy boundaries, updates tests/docs when needed, runs relevant validation or explains why not, and reports known risks/follow-ups clearly.
<!-- LEAP_MASTER_REPO_SECTION_END -->
