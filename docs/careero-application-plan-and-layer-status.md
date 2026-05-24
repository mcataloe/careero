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
3. `docs/archive/*` - historical context only.
4. LEAP repo - reusable LEAP framework methodology, not Careero-specific product truth.

Archived roadmap material must not be used for current LEAP Recon or Codex implementation prompts unless a task explicitly asks for historical comparison.

---

## Strategic Context

Careero is no longer just a local job tracker or STRIDE evaluation prototype. The repo now contains meaningful parts of a career operations platform:

- local-first backend and frontend foundation
- PostgreSQL persistence
- workspace/search-track persistence
- Opportunity-facing intake backed by current Role persistence
- resume/profile source grounding
- STRIDE evaluation
- artifact generation foundations
- application workflow tracking
- state history
- notes
- external links
- structured interview tracking
- analytics and dashboard intelligence surfaces

However, the implementation is not yet fully stabilized. Some roadmap claims are ahead of current product completeness, and some branch work still needs reconciliation before it should be treated as complete.

The next strategic move is to stabilize current workflow reality and then introduce a deliberate **Layer 7 - Opportunity Model Strategy** before deeper integrations.

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
- STRIDE evaluation generation
- deterministic STRIDE scoring
- optional OpenAI STRIDE enrichment
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
- STRIDE insights endpoint
- source intelligence endpoint
- compensation intelligence endpoint
- search health endpoint
- recommendations endpoint
- historical learning endpoint
- dashboard surfaces for analytics and recommendations

### Partially built / needs reconciliation or validation

The current repo also has partially completed, branch-diverged, or not-yet-fully-validated work for:

- local application reminders: current `main` has reminder tables, service logic, counts, analytics inputs, and timeline events, but the fuller reminder API routes, frontend panel, and `docs/application-reminders.md` remain on an unmerged branch.
- external-link summary/count refinements: external-link CRUD is present, but the separate summary/count refinement commit is not an ancestor of `main`.
- branch drift from Codex-generated feature work
- Layer 4 workflow completion, especially reminder UX and final count validation
- Layer 5 insight stabilization

These should not be treated as cleanly complete until reconciled into `main`, validated, and reflected in documentation. During this documentation refresh, repo history and file presence were inspected; full DB-backed test validation was not completed.

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
- coach/advisor collaboration mode
- marketplace or employer-side capabilities

---

## Revised Layer Status Table

| Layer | Revised name | Revised status | Notes |
| --- | --- | --- | --- |
| Layer 0 | Product Foundation | Built / defined | Product mission, user-first posture, search-track concept, AI governance, UX philosophy, monetization caution, and risk boundaries are defined. |
| Layer 1 | Local Platform Foundation | Built locally / production incomplete | Local backend, frontend, database, migrations, config, and seed model exist. Production auth, multi-user identity, tenancy, and authorization hardening remain future. |
| Layer 2 | Intake, Parsing & Grounding | Mostly built | Manual role intake, AI-assisted parsing, resume/profile source storage, active source grounding, and local imports exist. Parser confidence UX and richer source normalization remain. |
| Layer 3 | STRIDE + Artifact Foundation | Mostly built / lifecycle incomplete | STRIDE and artifact generation foundations exist. Artifact review, edit, approval, export, submitted tracking, and retrieval UX remain. |
| Layer 4 | Application Workflow | Substantially built / reminders still partial | Applications, state transitions, timeline, notes, external links, and structured interview tracking exist. Reminder persistence/count/timeline support exists, but the fuller reminder API/UI branch still needs reconciliation. External-link summary/count refinements also need validation before being called complete. |
| Layer 5 | Workflow Intelligence / Insights | Partially built | Analytics and dashboard surfaces exist. Needs validation, workspace filtering, confidence calibration, and cohesive insight behavior. |
| Layer 6 | Advanced STRIDE + Artifact Lifecycle | Partially built / next lifecycle layer | Build artifact lifecycle UX, STRIDE history, evidence mapping, submitted artifacts, and export flow. |
| Layer 7 | Opportunity Model Strategy | In progress / compatibility surface started | Opportunity-facing API and UX aliases have started while persistence remains Role-backed. Destructive rename remains future. |
| Layer 8 | Integrations | Partially built / local export started | Local integration adapter boundary and backend Markdown/DOCX/PDF artifact export exist. Frontend export workflow, Google Docs, Gmail/Outlook, calendar, browser/share, and cloud sync remain future. |
| Layer 9 | Automation Guardrails | Partially built / local guardrail foundation started | Durable suggestions, approval logs, workspace preferences, and review surfaces exist. External actions, batch approvals, and state-changing automation remain prohibited/future. |
| Layer 10 | Advanced Search Tracks / Career Strategy | Planned | Full-time vs contract strategy, compensation modeling, skill gaps, career narrative, search retrospectives, and role-market positioning. |
| Layer 11 | Productization / Deployment / Monetization | Future | Production deployment, auth hardening, privacy model, billing, cost controls, paid AI/artifact tiers, account lifecycle. |
| Layer 12 | Advisor / Collaboration Mode | Future | Coach, reviewer, spouse/advisor review, scoped sharing, comments, shared opportunity packets. |
| Layer 13 | Marketplace / Employer-Side Exploration | Future / last | Recruiter-facing workflows, ethical matching, user-controlled visibility, employer partnerships, strict disclosure rules. |

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
- STRIDE grounding flow.

### Remaining work

- Better parser confidence UX.
- Field-level parse warnings.
- Source deduplication.
- Company/source/recruiter normalization.
- Google Docs import later under integrations.

### Guidance

Treat Layer 2 as stable enough to build on. Improve opportunistically, but do not restart the architecture here.

---

## Layer 3 — STRIDE + Artifact Foundation

### Status

Mostly built / lifecycle incomplete.

### Purpose

Evaluate opportunities and generate grounded application artifacts.

### Already accomplished

- STRIDE evaluation persistence.
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

### Remaining work

- Artifact list page.
- Artifact detail page.
- Review/edit/approve/archive flow.
- Submitted artifact tracking.
- Markdown/DOCX/PDF export.
- Artifact comparison/diff.
- Better artifact visibility from role/application pages.
- Explicit UI separation of draft, reviewed, approved, exported, submitted, and archived artifacts.

### Guidance

Do not focus next on adding more generation logic. Focus on lifecycle, reviewability, retrieval, and export.

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

- Reminder API routes and frontend panel remain on an unmerged branch.
- External-link summary/count refinements remain on an unmerged branch and need validation before being treated as current.

### Remaining work

- Reconcile local reminders branch/work into `main`.
- Add or restore frontend reminder panel.
- Ensure application detail page surfaces all first-class workflow records.
- Confirm timeline includes notes, links, reminders, interviews, STRIDE, artifacts, and state changes.
- Confirm pipeline/dashboard counts align with backend records after reminder and external-link count reconciliation.
- Validate migrations after reminder branch reconciliation.
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
- STRIDE insights endpoint.
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

## Layer 6 — Advanced STRIDE + Artifact Lifecycle

### Status

Partially built / next lifecycle layer.

### Purpose

Make STRIDE evaluations and generated artifacts more trustworthy, traceable, comparable, and useful.

### Already accomplished

- STRIDE evaluation records.
- STRIDE metadata/versioning.
- Artifact generation services.
- TruthGuard-style checks.
- Artifact performance data foundation.
- Missing keyword/alignment concepts.

### Remaining work

- JD-to-resume evidence mapping.
- Missing requirement explanations.
- STRIDE history and comparison.
- Cross-opportunity STRIDE comparison.
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
- Link Opportunity to workspace, company, recruiter/source, STRIDE, artifacts, applications, notes, reminders, interviews, outcomes, and analytics.
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

Markdown, DOCX, and PDF artifact export belong in this Layer 8 prototype build. Export should be generated from stored, validated artifact content and should record local export metadata without requiring cloud storage.

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

Planned.

### Purpose

Make Careero more strategic than tactical by helping users evaluate whether their overall search strategy is working.

### Candidate capabilities

- Full-time vs contract strategy comparison.
- Compensation target modeling.
- Skill-gap planning.
- Role-market positioning.
- Career narrative refinement.
- Search-track retrospectives.
- Strategic category adjustments.
- Search-track archival retrospectives.

### Guidance

This layer becomes stronger after Layer 7 because strategic planning depends on clean historical Opportunity data.

---

## Layer 11 — Productization / Deployment / Monetization

### Status

Future.

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

### Guidance

Do not productize until the user-side workflow has proven durable value locally.

---

## Layer 12 — Advisor / Collaboration Mode

### Status

Future.

### Purpose

Allow trusted external help while preserving privacy boundaries.

### Candidate capabilities

- Career coach access.
- Resume reviewer access.
- Spouse/advisor review mode.
- Comment-only permissions.
- Shared opportunity packets.
- Privacy-scoped collaboration.

### Guidance

This should wait until artifacts, opportunities, and application records are cleanly separated.

---

## Layer 13 — Marketplace / Employer-Side Exploration

### Status

Future / last.

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

This layer should be last. Careero should not compromise user trust by becoming employer-first too early.

---

# Recommended Immediate Execution Plan

## Step 1 — Repo Reality Reconciliation

### Goal

Get `main` into a clean, truthful state before new feature work.

### Tasks

- Review diverged Codex branches.
- Recover reminder work that belongs in `main`.
- Confirm structured interview tracking remains clean after merge.
- Recover external-link count refinements if still relevant.
- Reconcile migrations carefully.
- Run backend compile/tests.
- Run frontend tests/build.
- Run contracts tests.
- Update README and roadmap docs to match actual implementation.

### Suggested commit theme

```text
Reconcile workflow branch drift and roadmap status
```

---

## Step 2 — Layer 4 Completion Pass

### Goal

Finish the workflow records users expect before modeling Opportunity more deeply.

### Tasks

- Fully integrate reminders.
- Validate structured interview tracking across backend, frontend, timeline, and tests.
- Confirm notes, links, reminders, interviews, and timeline work consistently.
- Ensure application detail page surfaces all first-class workflow records.
- Confirm pipeline and dashboard counts are accurate.
- Ensure all workflow events appear in timeline/activity where appropriate.

### Exit criteria

- Application detail page shows notes, links, reminders, interviews, and timeline.
- Application list/pipeline counts match backend records.
- All workflow state transitions are tested.
- Branches no longer contain unmerged Layer 4 work that should be part of `main`.

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
- Add export to Markdown first, then DOCX/PDF.
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

# Revised Build Order

Recommended order from here:

1. Repo reconciliation and roadmap correction.
2. Layer 4 workflow completion.
3. Layer 5 insight stabilization.
4. Layer 6 artifact lifecycle completion.
5. Layer 7 Opportunity Model Strategy and compatibility surface.
6. Layer 8 integrations.
7. Layer 9 automation guardrails.
8. Layer 10 advanced search-track strategy.
9. Layer 11 productization/deployment/monetization.
10. Layer 12 advisor/collaboration mode.
11. Layer 13 marketplace/employer-side exploration.

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
- Marketplace last.

Revise:

- Do not call Layer 1 fully complete until production auth/identity exists.
- Do not call Layer 4 complete until reminders are fully reconciled into `main` and workflow counts/timeline behavior are validated.
- Do not call Layer 5 merely next; it is already partially implemented.
- Move Integrations from Layer 7 to Layer 8.
- Introduce Opportunity Model Strategy as Layer 7.

Delay:

- External integration work before Opportunity semantics are stable.
- Automation that mutates state without user-visible approval/audit.
- Marketplace/employer-side work until user-side trust is strong.

---

# Strategic Conclusion

Careero has crossed from job tracker into career operations platform.

The next architectural center should be:

> Opportunity as the durable, strategic, historical intelligence object.

Everything else should orbit that:

- STRIDE evaluates the opportunity.
- Artifacts target the opportunity.
- Applications track pursuit of the opportunity.
- Notes, reminders, and interviews describe activity around the opportunity.
- Analytics learn from opportunity outcomes.
- Integrations import/export opportunity-related data.
- Automation suggests actions around opportunity lifecycle.

This document should be updated whenever implementation reality changes, especially after branch reconciliation, Layer 4 completion, and Layer 7 LEAP Recon output.
