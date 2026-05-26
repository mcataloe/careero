# Careero Application Plan and Layer Status

## Purpose

This document is the Careero-specific source of truth for:

- What has already been built in the Careero application.
- What remains to be built.
- The recommended execution order for upcoming work.
- The layer status used to drive Careero-specific LEAP Recon work and LEAP implementation prompts.

This document is intentionally specific to the `mjcataldi/careero` application.

General LEAP framework guidance, reusable LEAP prompt patterns, and application-buildout methodology should live in the separate GitHub `leap` repository, not in this Careero repo.

Careero-specific product strategy, implementation status, domain model decisions, and layer planning belong here.

---

## Current Planning Hierarchy

1. `README.md` - short project entry point and pointer to canonical planning docs.
2. `docs/careero-application-plan-and-layer-status.md` - canonical Careero-specific layer status and build order.
3. Active layer-specific docs, including `docs/opportunity-model-strategy.md`, `docs/productization-readiness.md`, `docs/advisor-collaboration-mode.md`, and `docs/careero-layer-14-strategic-plan-section.md`.
4. `docs/archive/*` - historical context only.
5. LEAP repo - reusable LEAP framework methodology, not Careero-specific product truth.

Archived roadmap material must not be used for current LEAP Recon or Codex implementation prompts unless a task explicitly asks for historical comparison.

---

## Strategic Context

Careero is no longer just a local job tracker or COMPASS evaluation prototype. The repo now contains meaningful parts of a career operations platform:

- local-first backend and frontend foundation
- PostgreSQL persistence
- workspace/search-track persistence
- Opportunity-facing intake backed by current Role persistence
- resume/profile source grounding
- COMPASS evaluation
- artifact generation foundations
- application workflow tracking
- state history
- notes
- external links
- structured interview tracking
- analytics and dashboard intelligence surfaces

However, the implementation is not yet fully stabilized. Some roadmap claims are ahead of current product completeness, and any private remote branch or PR work still needs validation before it should be treated as complete.

The current strategic move is to stabilize existing workflow and intelligence reality while keeping Layer 10 as derived, read-only career strategy synthesis. A later strategic expansion now belongs after Layer 13: user-selected model routing, credit economics, API-only job-posting ingestion, and source-governed company research memory. Layer 14 is planning-only in `main`; none of its model catalog, credit wallet, job-posting ingestion, or company research cache has been implemented.

---

## Repository Ownership Boundary

### Careero repo

The Careero repo should contain:

- Careero application roadmap
- Careero layer status
- Careero product decisions
- Careero domain model strategy
- Careero-specific LEAP Recon outputs
- Careero-specific LEAP implementation prompts
- Careero-specific implementation notes
- Careero-specific architecture decisions

### LEAP repo

The separate `leap` repo should contain:

- generic LEAP framework methodology
- generic LEAP Recon structure
- generic LEAP Prompt / implementation prompt templates
- reusable layer-buildout methodology
- reusable app-development orchestration guidance
- methodology that applies to applications beyond Careero

Rule of thumb:

> If the content describes how to build Careero, store it in Careero. If the content describes how LEAP should work for any application, store it in LEAP.

---

## Current Repo Reality Summary

### Strongly present / already built

The current repo already includes meaningful implementation for:

- FastAPI backend
- React + Vite frontend
- Mantine-based UI
- PostgreSQL persistence
- Alembic migrations
- local development scripts
- local health checks
- default local user seed model
- workspace persistence
- manual role intake
- optional AI-assisted role parsing
- role listing/detail/update/archive
- resume/profile source storage
- resume/profile source versions
- active resume/profile source grounding
- COMPASS evaluation generation
- deterministic COMPASS scoring
- optional OpenAI COMPASS enrichment
- evaluation caching/reuse
- evaluation metadata and input hashing
- canonical TypeScript/Zod contracts package
- generated JSON Schema contracts
- resume artifact generation service
- cover-letter artifact generation service
- GeneratedArtifact persistence
- artifact truthfulness checks
- artifact performance records
- application persistence
- application state machine
- application state history
- application list/detail APIs
- application pipeline APIs
- application notes
- application external links
- structured application interview tracking
- application timeline aggregation
- activity log
- local integration adapter boundary
- backend local Markdown/DOCX/PDF artifact export
- automation suggestion persistence and API
- automation approval log persistence and API
- workspace automation preferences
- search analytics endpoint
- artifact performance analytics endpoint
- COMPASS insights endpoint
- source intelligence endpoint
- compensation intelligence endpoint
- search health endpoint
- recommendations endpoint
- historical learning endpoint
- dashboard surfaces for analytics and recommendations

### Partially built / needs reconciliation or validation

The current repo also has partially completed or not-yet-fully-validated work for:

- local application reminders: current `main` has reminder tables, service methods, counts, next-action synchronization, activity-log events, analytics inputs, and timeline events, but no FastAPI reminder routes, frontend reminder API wrapper, or frontend reminder panel.
- external-link workflow summaries: external-link CRUD API routes, frontend panel, activity-log events, timeline update/delete events, and tests exist in `main`; application list/detail summary counts still include notes, reminders, and interviews only, not links.
- private remote branch or PR drift, if any, is outside the current local clone; this clone currently exposes only `main` and `origin/main`.
- Layer 4 workflow completion, especially reminder API/UI completion and final summary-count decisions.
- Layer 5 insight stabilization.

These should not be treated as cleanly complete until implemented or validated in `main` and reflected in documentation. During this documentation refresh, repo files and local git state were inspected; full DB-backed test validation was not completed.

### Not yet built / still future

The repo does not yet fully include:

- production authentication
- real multi-user tenant behavior
- production authorization hardening
- billing/subscriptions
- production deployment architecture
- runtime workspace switching UX
- mature workspace management UX
- dedicated artifact list/detail UX
- artifact review/edit/approve/archive flow
- submitted artifact tracking
- dedicated frontend artifact export workflow
- destructive persistence migration from Role table/model/foreign-key naming
- Google Docs import
- Gmail/Outlook integration
- calendar interview sync
- LinkedIn/job-board save helpers
- browser extension or share-sheet intake
- external review-before-send workflows
- hosted coach/advisor collaboration mode
- marketplace or employer-side capabilities
- user-selected model routing and a provider/model catalog
- modular prompt compiler architecture beyond the current artifact-generation prompt foundations
- credit wallet, durable credit ledger, usage metering, credit reservation/debit/refund, rollover, top-ups, or billing-linked credits
- API-only job posting ingestion from official ATS/job-data providers
- API-only company research ingestion, source record caching, fact extraction, summary regeneration, and freshness tracking
- external source licensing/compliance governance for company research and review/salary/culture data
- scraping or restricted-source extraction; this is explicitly deferred for later legal/product/technical review

---

## Revised Layer Status Table

| Layer | Revised name | Revised status | Notes |
| --- | --- | --- | --- |
| Layer 0 | Product Foundation | Built / defined | Product mission, user-first posture, search-track concept, AI governance, UX philosophy, monetization caution, and risk boundaries are defined. |
| Layer 1 | Local Platform Foundation | Built locally / production incomplete | Local backend, frontend, database, migrations, config, and seed model exist. Production auth, multi-user identity, tenancy, and authorization hardening remain future. |
| Layer 2 | Intake, Parsing & Grounding | Mostly built | Manual role intake, AI-assisted parsing, resume/profile source storage, active source grounding, and local imports exist. Parser confidence UX and richer source normalization remain. |
| Layer 3 | COMPASS + Artifact Foundation | Mostly built / lifecycle incomplete | COMPASS and artifact generation foundations exist. Artifact review, edit, approval, export, submitted tracking, and retrieval UX remain. |
| Layer 4 | Application Workflow | Substantially built / reminders still partial | Applications, state transitions, timeline, notes, external links, and structured interview tracking exist. Reminder persistence/service/count/timeline support exists, but reminder API routes and frontend reminder UX are not in `main`. External-link CRUD/UI exists; summary counts still omit links. |
| Layer 5 | Workflow Intelligence / Insights | Partially built | Analytics and dashboard surfaces exist. Needs validation, workspace filtering, confidence calibration, and cohesive insight behavior. |
| Layer 6 | Advanced COMPASS + Artifact Lifecycle | Partially built / next lifecycle layer | Build artifact lifecycle UX, COMPASS history, evidence mapping, submitted artifacts, and export flow. |
| Layer 7 | Opportunity Model Strategy | In progress / compatibility surface started | Opportunity-facing API and UX aliases have started while persistence remains Role-backed. Destructive rename remains future. |
| Layer 8 | Integrations | Partially built / local export started | Local integration adapter boundary and backend Markdown/DOCX/PDF artifact export exist. Frontend export workflow, Google Docs, Gmail/Outlook, calendar, browser/share, and cloud sync remain future. |
| Layer 9 | Automation Guardrails | Partially built / local guardrail foundation started | Durable suggestions, approval logs, workspace preferences, and review surfaces exist. External actions, batch approvals, and state-changing automation remain prohibited/future. |
| Layer 10 | Advanced Search Tracks / Career Strategy | Partially built / derived strategy synthesis MVP started | Read-only workspace strategy summary and internal cross-track comparison exist. No durable strategy tables, external market data, AI strategy memory, or automation mutation. |
| Layer 11 | Productization / Deployment / Monetization | Future / readiness documentation started | Productization, privacy/data governance, account lifecycle, AI usage/cost controls, monetization boundaries, and deployment gates are documented. Production deployment, auth hardening, billing, tenant isolation, export/delete, retention enforcement, and usage metering implementation remain future. |
| Layer 12 | Advisor / Collaboration Mode | Future / local-only packet preview started | Advisor collaboration readiness is documented in [`docs/advisor-collaboration-mode.md`](advisor-collaboration-mode.md). Local-only redacted advisor packet preview/Markdown export and redaction metadata exist for application detail. Hosted collaboration, advisor accounts, invitations, comments, public links, external sharing, and employer/recruiter visibility remain future. |
| Layer 13 | Marketplace / Employer-Side Exploration | Future / last employer-facing layer | Recruiter-facing workflows, ethical matching, user-controlled visibility, employer partnerships, strict disclosure rules. |
| Layer 14 | Model Choice, Credits & API-First Intelligence | Future / appended strategic layer | Planning source exists in [`docs/careero-layer-14-strategic-plan-section.md`](careero-layer-14-strategic-plan-section.md). No model catalog, prompt compiler gateway, credit ledger, API job ingestion, company research cache, or scraping capability exists in `main`. 14A/14B may be pulled forward with Layer 11; 14C/14D wait on Opportunity and integration boundaries. |

---

# Layer Details

## Layer 0 — Product Foundation

### Status

Built / defined.

### Purpose

Layer 0 defines the product conscience for Careero.

Careero should remain job-seeker-first, AI-grounded, source-traceable, emotionally humane, and search-track-aware.

### Already accomplished

- Mission and product principles defined.
- Target users defined.
- MVP boundary defined.
- Workspace/search-track concept defined.
- AI governance posture defined.
- UX philosophy defined.
- Monetization caution defined.
- Risk boundaries defined.

### Remaining work

- Keep docs updated as implementation reality changes.
- Ensure future features do not drift into employer-first, marketplace-first, or automation-first behavior.

---

## Layer 1 — Local Platform Foundation

### Status

Built locally / production incomplete.

### Purpose

Provide the local-first technical foundation for Careero.

### Already accomplished

- FastAPI backend.
- React + Vite frontend.
- PostgreSQL persistence.
- Alembic migrations.
- Local development scripts.
- Backend and frontend health checks.
- Default local user seed model.
- Environment/config structure.
- Workspace persistence.
- Core repository structure.

### Remaining work

- Real authentication.
- User registration/login.
- Multi-user account support.
- Production authorization model.
- Runtime tenant isolation.
- Secrets/config hardening.
- Deployment-ready environment model.

### Guidance

Do not block local product iteration on production auth yet, but do not call Layer 1 fully complete until identity and authorization are production-grade.

---

## Layer 2 — Intake, Parsing & Grounding

### Status

Mostly built.

### Purpose

Turn raw job/opportunity and source-material input into structured, reviewable, grounded system data.

### Already accomplished

- Manual role intake.
- Role creation/list/detail/update/archive.
- Optional AI-assisted role parsing.
- Editable review-before-save behavior.
- Resume/profile source storage.
- Resume/profile source versions.
- Active source grounding.
- Supported local document imports.
- COMPASS grounding flow.

### Remaining work

- Better parser confidence UX.
- Field-level parse warnings.
- Source deduplication.
- Company/source/recruiter normalization.
- Google Docs import later under integrations.

### Guidance

Treat Layer 2 as stable enough to build on. Improve opportunistically, but do not restart the architecture here.

---

## Layer 3 — COMPASS + Artifact Foundation

### Status

Mostly built / lifecycle incomplete.

### Purpose

Evaluate opportunities and generate grounded application artifacts.

### Already accomplished

- COMPASS evaluation persistence.
- Deterministic scoring.
- Optional AI enrichment.
- Evaluation metadata.
- Prompt/ruleset versioning.
- Input hashing.
- Evaluation caching/reuse.
- Canonical contracts package.
- Generated JSON Schema contracts.
- Resume artifact generation service.
- Cover-letter artifact generation service.
- GeneratedArtifact persistence.
- Contract validation.
- Truthfulness checks.
- Artifact performance recording.
- Backend local Markdown/DOCX/PDF artifact export through the Layer 8 local export boundary.

### Remaining work

- Artifact list page.
- Artifact detail page.
- Review/edit/approve/archive flow.
- Submitted artifact tracking.
- Dedicated frontend artifact export workflow for the existing backend export API.
- Artifact comparison/diff.
- Better artifact visibility from role/application pages.
- Explicit UI separation of draft, reviewed, approved, exported, submitted, and archived artifacts.

### Guidance

Do not focus next on adding more generation logic. Focus on lifecycle, reviewability, retrieval, frontend export workflow, and submitted-artifact clarity.

---

## Layer 4 — Application Workflow

### Status

Substantially built / reminders still partial.

### Purpose

Manage the day-to-day job-search workflow around saved opportunities.

### Already accomplished

- Application persistence.
- Ensure/create application for role.
- Application list.
- Workspace-scoped application list.
- Application pipeline grouping.
- Application detail.
- Application timeline.
- State transition endpoint.
- Backend-enforced state machine.
- State history.
- Notes CRUD.
- External links CRUD.
- Structured interview tracking APIs.
- Structured interview tracking frontend panel.
- Interview-stage timeline events and state-transition suggestion.
- Reminder persistence tables.
- Reminder service logic.
- Reminder counts, analytics input, and timeline events.
- Metadata updates.
- ActivityLog integration.

### Partially accomplished

- Reminder persistence, service methods, next-action synchronization, counts, activity logs, analytics inputs, and timeline events exist in `main`.
- External-link CRUD API routes, frontend panel, activity logs, timeline update/delete events, and tests exist in `main`.

### Remaining work

- Add reminder FastAPI routes.
- Add frontend reminder API wrapper and reminder panel.
- Ensure application detail page surfaces all first-class workflow records.
- Confirm timeline includes notes, links, reminders, interviews, COMPASS, artifacts, and state changes.
- Decide whether application summary counts should include external links, then update backend/frontend/tests if needed.
- Confirm pipeline/dashboard counts align with backend records after reminder API/UI completion and external-link count decisions.
- Validate migrations after reminder API/UI completion.
- Confirm backend, frontend, and contracts tests pass.

### Guidance

Layer 4 should be stabilized before deeper Opportunity intelligence. Otherwise later analytics and model strategy will inherit incomplete workflow data.

---

## Layer 5 — Workflow Intelligence / Insights

### Status

Partially built.

### Purpose

Turn accumulated workflow activity into useful guidance.

### Already accomplished

- Search analytics endpoint.
- Artifact performance endpoint.
- COMPASS insights endpoint.
- Source intelligence endpoint.
- Compensation intelligence endpoint.
- Search health endpoint.
- Recommendations endpoint.
- Historical learning endpoint.
- Dashboard panels for analytics and insight summaries.

### Remaining work

- Validate analytics against deterministic fixture data.
- Add workspace selector/filtering to dashboard UX.
- Improve insufficient-data handling.
- Improve signal explainability.
- Calibrate confidence levels.
- Ensure all insights use current workflow records consistently.
- Tie insight generation to Opportunity model strategy.

### Guidance

Layer 5 is no longer merely “next.” It exists. The work now is stabilization, accuracy, and cohesion.

---

## Layer 6 — Advanced COMPASS + Artifact Lifecycle

### Status

Partially built / next lifecycle layer.

### Purpose

Make COMPASS evaluations and generated artifacts more trustworthy, traceable, comparable, and useful.

### Already accomplished

- COMPASS evaluation records.
- COMPASS metadata/versioning.
- Artifact generation services.
- TruthGuard-style checks.
- Artifact performance data foundation.
- Missing keyword/alignment concepts.

### Remaining work

- JD-to-resume evidence mapping.
- Missing requirement explanations.
- COMPASS history and comparison.
- Cross-opportunity COMPASS comparison.
- Artifact lifecycle states.
- Submitted version tracking.
- Resume/cover-letter variant comparison.
- Review/edit/export flow.
- Strict internal strategy vs employer-facing artifact separation in UI.

### Guidance

Layer 6 should turn generated output from “AI result” into durable, inspectable, user-approved product records.

---

## Layer 7 - Opportunity Model Strategy

### Status

In progress / compatibility surface started.

### Purpose

Define Opportunity as the central durable intelligence object in Careero.

Layer 7A design source of truth: [Opportunity model strategy](opportunity-model-strategy.md).

Layer 7B has started by adding Opportunity-facing API and frontend compatibility surfaces while preserving the current `Role` model, `roles` table, `role_id` foreign keys, and `/roles` compatibility behavior.

### Why this layer moves ahead of integrations

The app already has workflow, artifact, evaluation, analytics, and dashboard infrastructure. The next bottleneck is not external data ingestion. The next bottleneck is semantic clarity around the core object.

Current backend naming still uses `Role`, but Careero needs `Opportunity` as the canonical object that can represent:

- job posting
- recruiter lead
- contract possibility
- consulting engagement
- referral
- role being watched
- archived historical lead
- strategic comparison target

### Core goals

- Define Opportunity as the canonical successor to Role.
- Separate opportunity status from application workflow state.
- Preserve raw/source/parsed/normalized/provenance data.
- Link Opportunity to workspace, company, recruiter/source, COMPASS, artifacts, applications, notes, reminders, interviews, outcomes, and analytics.
- Support deduplication and similarity detection.
- Support opportunity lineage/history.
- Support historical analytics such as response rate by source, compensation fit, role category, artifact variant, and search-track strategy.

### Required LEAP Recon questions

- What is an Opportunity in Careero?
- What belongs on Opportunity vs Application?
- What belongs on Opportunity vs Artifact?
- What belongs on Opportunity vs Workspace/Search Track?
- Should `roles` be renamed to `opportunities`, aliased, or migrated gradually?
- How should source/provenance/recruiter intelligence work?
- How should opportunity similarity/deduplication work?
- What historical intelligence should opportunities accumulate?

### Recommended deliverables / current status

1. Layer 7A Opportunity strategy document: [Opportunity model strategy](opportunity-model-strategy.md). Done.
2. Current-state Role-to-Opportunity mapping. Done in the Layer 7A artifact.
3. Schema migration plan. Defined as hybrid compatibility first, destructive persistence rename later if still justified.
4. API transition plan. Started with `/api/opportunities` aliases while `/api/roles` remains compatible.
5. Frontend naming and route plan. Started with `/opportunities` canonical routes and `/roles` redirects.
6. Analytics integration plan. Defined in the Layer 7A artifact; implementation remains Role-backed.
7. LEAP Prompt/LHS implementation slices for any later destructive migration. Still future.

### Guidance

Use the Layer 7A strategy artifact before further implementation prompts. Layer 7B compatibility work has started; Layer 7C destructive persistence rename remains a separate future decision.

---

## Layer 8 — Integrations

### Status

Partially built / local export started.

### Purpose

Reduce manual entry by connecting Careero to tools job seekers already use.

### Candidate capabilities

- Google Docs import.
- Gmail/Outlook linkage.
- Calendar interview sync.
- LinkedIn/job-board save helpers.
- Browser extension or share-sheet intake.
- Resume source sync.
- DOCX/PDF/Markdown export.
- Optional cloud storage sync.

### Guidance

Layer 8 begins with Layer 7 compatibility cleanup. Integration-facing APIs should target Opportunity-facing routes and contracts while persistence remains Role-backed until a separate Layer 7C destructive rename is explicitly approved.

For the first Layer 8 MVP/prototype build, OAuth and account-linked sync are intentionally deferred. Do not implement Gmail/Outlook account linking, Google Docs account import, cloud sync, background polling, or external account token storage in this build. Local/manual integration paths come first: paste, local file import/export, generated files, manual links, and reviewable captured payloads.

Markdown, DOCX, and PDF artifact export belong in the Layer 8 local export boundary. Backend export is now present; the dedicated frontend export workflow remains future work.

Current `main` includes backend local Markdown, DOCX, and PDF artifact export
through the local integration adapter boundary. A dedicated frontend artifact
export workflow remains future work.

All integrations must preserve review-before-save, review-before-send, no-auto-apply, and TruthGuard boundaries. Imported content should remain reviewable and source/provenance-aware before it becomes durable Opportunity/Application/Artifact data.

---

## Layer 9 — Automation Guardrails

### Status

Partially built / local guardrail foundation started.

### Purpose

Automate repetitive actions safely while preserving user control.

### Candidate capabilities

- Suggested follow-ups.
- Draft-only application material generation.
- Reminder automation.
- Review-before-send workflows.
- Approval logs.
- No-auto-apply boundaries.
- Workspace-level automation preferences.
- TruthGuard checks before artifact generation/submission.

### Guidance

Automation should suggest or draft before it acts. User-visible state changes and external communication must remain reviewable and auditable.

Current `main` includes durable automation suggestions, approval logs, workspace
automation preferences, dashboard/application review surfaces, and settings for
local guardrails. Approving a suggestion records an audit decision only; it does
not send externally, sync externally, auto-apply, batch-approve, or silently
mutate application state. Communication drafts remain local previews.

Layer 9 details are tracked in [Automation guardrails](automation-guardrails.md).

---

## Layer 10 — Advanced Search Tracks / Career Strategy

### Status

Partially built / derived strategy synthesis MVP started.

### Purpose

Make Careero more strategic than tactical by helping users evaluate whether their overall search strategy is working.

### Already accomplished

- Read-only strategy synthesis contracts.
- Workspace-scoped career strategy backend service.
- `GET /api/strategy/workspaces/{workspace_id}` endpoint.
- `GET /api/strategy/workspaces?include_cross_track=true` endpoint for internal cross-track comparison.
- Frontend career strategy surface with workspace selection.
- Insufficient-data, confidence, sample-size, source-input, warning, retrospective, compensation, role-positioning, skill-gap, narrative, and action-candidate sections.
- No durable strategy tables.
- No external market data.
- No state mutation or automation suggestion creation.

### Candidate capabilities / remaining work

- Full-time vs contract strategy comparison.
- Compensation target modeling.
- Skill-gap planning.
- Role-market positioning.
- Career narrative refinement.
- Search-track retrospectives.
- Strategic category adjustments.
- Search-track archival retrospectives.
- Durable user-reviewed retrospectives if explicitly scoped later.
- Optional source-grounded AI summarization after deterministic synthesis is mature.
- Explicit user-selected strategy-to-automation handoff through Layer 9 approval logs.

### Guidance

Layer 10 remains stronger as Layer 7, Layer 5, and artifact lifecycle data mature. Strategy synthesis must remain advisory, source-visible, and based on stored Careero evidence only.

---

## Layer 11 — Productization / Deployment / Monetization

### Status

Future / readiness documentation started.

### Purpose

Turn Careero into a sustainable product without compromising user trust.

### Candidate capabilities

- Production deployment plan.
- Authentication hardening.
- Authorization hardening.
- Privacy model.
- Billing/subscription model.
- Free tier.
- Paid AI/artifact usage.
- Power-user tier.
- Cost controls.
- Account deletion/export.
- Data retention policy.

### Readiness docs

Layer 11 readiness docs now define productization, privacy, account lifecycle,
AI usage/cost, monetization, and deployment gates:

- [Productization readiness](productization-readiness.md)
- [Privacy and data governance](privacy-data-governance.md)
- [Account lifecycle](account-lifecycle.md)
- [AI usage and cost controls](ai-usage-cost-controls.md)
- [Monetization boundary](monetization-boundary.md)
- [Deployment readiness](deployment-readiness.md)
- [Cross-layer impact map](cross-layer-impact-map.md)
- [Execution drift ledger](execution-drift-ledger.md)

These documents are readiness and boundary design only. They do not implement
production auth, billing, tenant isolation, hosted deployment, data export/delete,
retention enforcement, or AI usage metering.

Layer 14 extends the productization strategy for model choice, credits, and
API-first intelligence, but those capabilities are not implemented in `main`.
Layer 14A/14B should only be pulled forward when Layer 11 billing, metering,
and model-usage controls are actively scoped.

### Guidance

Do not productize until the user-side workflow has proven durable value locally.
Layer 11 implementation should not proceed until local workflow value,
privacy/account lifecycle, AI usage/cost controls, deployment readiness, and
production blockers are resolved through a fresh LEAP Recon.

---

## Layer 12 — Advisor / Collaboration Mode

### Status

Future / local-only packet preview started.

### Purpose

Allow trusted external help while preserving privacy boundaries.

Active readiness/design source: [`docs/advisor-collaboration-mode.md`](advisor-collaboration-mode.md).

Current implementation is limited to local-only owner-visible advisor packet
preview, deterministic redaction metadata, explicit local include options, and
Markdown export from application detail. It does not create hosted access,
advisor accounts, invitations, comments, public links, external sharing, or
employer/recruiter visibility.

### Candidate capabilities

- Career coach access.
- Resume reviewer access.
- Spouse/advisor review mode.
- Comment-only permissions.
- Shared opportunity packets.
- Privacy-scoped collaboration.

### Guidance

Hosted collaboration should wait until artifacts, opportunities, and application records are cleanly separated and until production auth, authorization, tenant isolation, privacy controls, revocation, audit, and account lifecycle are implemented. Current Layer 12 implementation is local-only packet preview/export scaffolding and does not start hosted collaboration implementation.

---

## Layer 13 — Marketplace / Employer-Side Exploration

### Status

Future / last employer-facing layer.

### Purpose

Explore employer-side or marketplace capabilities only after user-side value is strong.

### Candidate capabilities

- Recruiter-facing opportunity intake.
- Ethical matching.
- User-controlled visibility.
- Optional employer partnerships.
- Strict disclosure rules.
- No pay-to-rank distortion.

### Guidance

This layer should remain the last employer-facing/marketplace expansion. Careero should not compromise user trust by becoming employer-first too early.

---

## Layer 14 - Model Choice, Credits & API-First Intelligence

### Status

Future / appended strategic layer.

Active planning source: [`docs/careero-layer-14-strategic-plan-section.md`](careero-layer-14-strategic-plan-section.md).

Layer 14 is appended after the existing layer list to preserve roadmap continuity. It does not mean every Layer 14 capability must wait until after Marketplace/Employer-Side Exploration.

Execution split:

- Layer 14A Prompt Compiler & Model Gateway and Layer 14B Credit Wallet, Usage Metering & Cost Controls can be pulled forward with Layer 11 productization when billing, metering, and model usage controls are actively implemented.
- Layer 14C API-Only Job Posting Ingestion and Layer 14D Company Research Memory should wait until Opportunity semantics, integration boundaries, source governance, and productization controls are stable.
- Layer 13 remains the last employer-facing/trust-sensitive expansion.

### Purpose

Give Careero a flexible but controlled system for user-selected AI models, credit-based usage, API-only job-posting ingestion, and reusable company research intelligence.

The strategic goal:

> Careero owns the workflow, prompt compiler, source grounding, quality checks, credit ledger, and research memory. Users can choose model, budget, and research depth inside those guardrails.

### Current `main` reality

Layer 14 is not implemented in the codebase. Current `main` has optional OpenAI-backed parsing/COMPASS/artifact-generation foundations and readiness docs for AI cost controls, but it does not have:

- model catalog tables or provider price snapshots
- user-selectable model defaults
- a general prompt compiler/gateway
- prompt-only export mode
- credit wallet, credit transactions, usage events, or artifact-linked usage records
- billing-linked credit grants, rollover, top-ups, reservations, debits, or refunds
- API job posting ingestion records or ATS/job-data provider integrations
- company research source records, facts, summaries, refresh runs, TTLs, or freshness UI
- scraping, restricted-source extraction, browser-driven collection, or background polling

### Hard boundary

Layer 14 is API-only for external data acquisition.

Do not implement scraping, restricted-source extraction, browser-driven collection, or terms-sensitive data collection in this layer. Scraping can be revisited later only through an explicit legal/product/technical review.

### Candidate sublayers

- Layer 14A: Prompt Compiler & Model Gateway.
- Layer 14B: Credit Wallet, Usage Metering & Cost Controls.
- Layer 14C: API-Only Job Posting Ingestion.
- Layer 14D: Company Research Memory & Source-Governed Caching.
- Layer 14E: Future Scraping Review Backlog Item.

### Guidance

Layer 14 should make Careero flexible without making it chaotic. The user may choose the model and budget; Careero should control prompt structure, source grounding, no-fabrication policy, quality checks, cost estimates, credit ledger, source provenance, research freshness, and API/licensing boundaries.

---

# Recommended Immediate Execution Plan

## Step 1 — Repo Reality Reconciliation

### Goal

Keep `main` in a clean, truthful state as new feature work lands.

### Tasks

- Review private remote branch/PR drift when external GitHub/PR access is available.
- Confirm reminder implementation gaps against `main`: service/model/timeline exist; API routes and frontend UX do not.
- Confirm structured interview tracking remains clean in `main`.
- Confirm whether external links should be included in application summary counts.
- Reconcile migrations carefully.
- Run backend compile/tests.
- Run frontend tests/build.
- Run contracts tests.
- Update README and roadmap docs to match actual implementation.

### Suggested commit theme

```text
Update roadmap to current main reality
```

---

## Step 2 — Layer 4 Completion Pass

### Goal

Finish the workflow records users expect before modeling Opportunity more deeply.

### Tasks

- Add reminder API routes.
- Add frontend reminder API wrapper and application detail reminder panel.
- Validate structured interview tracking across backend, frontend, timeline, and tests.
- Confirm notes, links, reminders, interviews, and timeline work consistently.
- Ensure application detail page surfaces all first-class workflow records.
- Confirm pipeline, dashboard, and workflow summary counts are accurate, including the explicit decision on whether links should be counted.
- Ensure all workflow events appear in timeline/activity where appropriate.

### Exit criteria

- Application detail page shows notes, links, reminders, interviews, and timeline.
- Application list/pipeline counts match backend records.
- All workflow state transitions are tested.
- Current local clone exposes no unmerged branches; private remote PR state may still need external verification.

---

## Step 3 — Layer 5 Insight Stabilization

### Goal

Make current analytics trustworthy before expanding the intelligence model.

### Tasks

- Validate each dashboard panel against deterministic fixture data.
- Add workspace filtering in the dashboard.
- Calibrate insufficient-data behavior.
- Improve explainability for each recommendation/signal.
- Ensure analytics use current workflow records consistently.
- Confirm artifact performance records are created and readable.

### Exit criteria

- Dashboard panels are believable.
- Signals explain their basis.
- Empty states are helpful.
- Workspace-scoped analytics work.

---

## Step 4 — Layer 6 Artifact Lifecycle Completion

### Goal

Turn generated artifacts into usable product objects.

### Tasks

- Add artifact list/detail page.
- Add review/edit/approve/archive lifecycle.
- Add submitted artifact tracking.
- Add dedicated frontend export workflow for existing backend Markdown/DOCX/PDF export.
- Add artifact retrieval from application and opportunity pages.
- Add artifact lineage/revision display.
- Add basic diff/compare if feasible.

### Exit criteria

- User can generate, review, retrieve, and mark a resume/cover letter as submitted.
- Artifact records are tied to opportunity/application/workspace.
- Internal strategy stays out of employer-facing artifacts.

---

## Step 5 - Layer 7 LEAP Recon: Opportunity Model Strategy

### Goal

Design the durable Opportunity model before integrations.

### Tasks

- Define Opportunity semantics.
- Define Role-to-Opportunity migration or compatibility plan.
- Define Opportunity vs Application boundaries.
- Define Opportunity vs Artifact boundaries.
- Define Opportunity vs Workspace/Search Track boundaries.
- Define source/provenance/recruiter intelligence.
- Define deduplication/similarity strategy.
- Define historical intelligence requirements.
- Produce LEAP Prompt/LHS slices for implementation.

### Exit criteria

- Canonical Opportunity strategy is documented.
- Migration plan exists.
- API transition plan exists.
- Frontend language/route plan exists.
- Analytics integration plan exists.
- LEAP implementation slices are ready.

---

## Step 6 - Layer 14 Strategic Recon

### Goal

Plan model choice, credits, API-only job ingestion, and company research caching without destabilizing the existing workflow roadmap.

### Tasks

- Define the Prompt Compiler module model.
- Define the model provider/catalog/price snapshot architecture.
- Define default model selection UX by artifact type.
- Define prompt-only export behavior.
- Define credit wallet, reservation, debit, refund, rollover, and top-up rules.
- Define provider/tool/API cost tracking.
- Validate official API access for target job posting sources.
- Define normalized `job_posting` ingestion records.
- Define company research source categories, source records, facts, summaries, and TTLs.
- Define source licensing/compliance review workflow.
- Add a backlog item to revisit scraping later; do not implement scraping in this pass.

### Exit criteria

- Layer 14 implementation slices are ready.
- API-only boundary is clear.
- Scraping revisit is tracked as a future TODO only.
- Credit economics are transparent and ledger-backed.
- Source freshness and source governance rules are explicit.

---

# Revised Build Order

Recommended order from here:

1. Repo reconciliation and roadmap correction.
2. Layer 4 workflow completion.
3. Layer 5 insight stabilization.
4. Layer 6 artifact lifecycle completion.
5. Layer 7 Opportunity Model Strategy and compatibility surface.
6. Layer 8 integrations.
7. Layer 9 automation guardrails.
8. Layer 10 advanced search-track strategy stabilization.
9. Layer 11 productization implementation only after readiness gates are satisfied.
10. Layer 12 advisor/collaboration mode.
11. Layer 13 marketplace/employer-side exploration.
12. Layer 14 model choice, credits, and API-first intelligence. Pull 14A/14B forward during Layer 11 if billing/model usage requires it; keep 14C/14D API-only and after Opportunity/integration boundaries are stable; keep Layer 13 as the last employer-side expansion.

---

# Preserved Value From Original Plan

The original roadmap still contains valuable direction and should not be discarded.

Preserve:

- User-first strategy.
- Search tracks/workspaces.
- AI as advisor, not fabricator.
- Evidence-based tailoring.
- Application workflow state machine.
- Notes/reminders/interviews/timeline.
- Artifact traceability.
- Integrations, but later.
- Automation guardrails, but later.
- Career strategy layer.
- Monetization caution.
- Advisor/collaboration mode.
- Marketplace/employer-side work last among employer-facing capabilities.
- User-selected model flexibility under a Careero-owned prompt framework.
- Credit transparency, usage metering, capped rollover, and top-up economics.
- API-first job and company intelligence with source freshness and no scraping in current scope.

Revise:

- Do not call Layer 1 fully complete until production auth/identity exists.
- Do not call Layer 4 complete until reminder API/UI work is implemented in `main` and workflow counts/timeline behavior are validated.
- Do not call Layer 5 merely next; it is already partially implemented.
- Move Integrations from Layer 7 to Layer 8.
- Introduce Opportunity Model Strategy as Layer 7.
- Add Layer 14 as an appended model-choice, credit-economy, API-first intelligence layer. Parts of 14A/14B may execute with Layer 11 productization even though the layer is documented after Layer 13.

Delay:

- External integration work before Opportunity semantics are stable.
- Automation that mutates state without user-visible approval/audit.
- Marketplace/employer-side work until user-side trust is strong.
- Any scraping strategy until official APIs, licensed providers, source terms, privacy risks, and retention rules have been reviewed.

---

# Strategic Conclusion

Careero has crossed from job tracker into career operations platform.

The next architectural center should be:

> Opportunity as the durable, strategic, historical intelligence object.

Everything else should orbit that:

- COMPASS evaluates the opportunity.
- Artifacts target the opportunity.
- Applications track pursuit of the opportunity.
- Notes, reminders, and interviews describe activity around the opportunity.
- Analytics learn from opportunity outcomes.
- Integrations import/export opportunity-related data.
- Automation suggests actions around opportunity lifecycle.

Layer 14 adds a second strategic center for productization-scale intelligence:

> Careero should let users choose the model and budget while Careero controls prompts, source grounding, quality, cost exposure, and API-only research memory.

The long-term strategic system is not merely an AI resume generator. It is a career application intelligence platform where users can generate, compare, and improve job-search materials using the model, research depth, and budget they choose while Careero protects source truth, freshness, and user control.

This document should be updated whenever implementation reality changes, especially after private PR reconciliation, Layer 4 completion, Layer 7 LEAP Recon output, and Layer 14 source/provider validation.
