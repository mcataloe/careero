# Careero Product Strategy and Layer Status

Status: Active  
Doc Type: Strategy  
Layer: N/A  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/00_start-here.md
- docs/02_layers/00_layer-index.md
- docs/01_strategy/03_current-layer-status.md
- docs/01_strategy/07_revised-build-order-execution-plan.md

## Purpose

This document is the Careero-specific source of truth for current layer status and high-level build order. The operational LEAP/LHS execution guide for the revised build order lives in [revised build order execution plan](07_revised-build-order-execution-plan.md).

Careero-specific product strategy, implementation status, domain model decisions, and layer planning belong here. Reusable LEAP methodology belongs in the separate LEAP framework repository.

---

## Current Planning Hierarchy

1. `README.md` - short project entry point and pointer to canonical planning docs.
2. `docs/01_strategy/00_product-strategy.md` - canonical Careero-specific layer status and high-level build order.
3. `docs/01_strategy/07_revised-build-order-execution-plan.md` - operational LEAP/LHS execution guide, prompt sequence, readiness gates, and pull-forward rules.
4. Active layer-specific docs:
   - `docs/03_domain-design/opportunity-model.md`
   - `docs/01_strategy/06_productization-readiness.md`
   - `docs/03_domain-design/advisor-collaboration-mode.md`
   - `docs/02_layers/14_layer-14-model-catalog-and-prompt-management.md`
   - `docs/02_layers/15_layer-15-api-job-sources-and-managed-deltas.md`
   - `docs/02_layers/16_layer-16-guided-onboarding-and-support.md`
5. `docs/99_archive/*` - historical context only.
6. LEAP repo - reusable framework methodology, not Careero product truth.

Archived roadmap material must not be used for current LEAP Recon or Codex implementation prompts unless a task explicitly asks for historical comparison.

The older combined `docs/99_archive/careero-layer-14-strategic-plan-section.md` is superseded by the split Layer 14 and Layer 15 docs and should not be used for new implementation prompts.

---

## Strategic Context

Careero is no longer just a local job tracker or COMPASS evaluation prototype. The repo now contains meaningful parts of a career operations platform: local-first backend/frontend foundation, PostgreSQL persistence, workspace/search-track persistence, Opportunity-facing intake backed by current Role persistence, resume/profile source grounding, COMPASS evaluation, artifact generation foundations, application workflow tracking, state history, notes, external links, structured interview tracking, analytics, and dashboard intelligence surfaces.

The current strategic move is to stabilize existing workflow and intelligence reality while keeping Layer 10 as derived, read-only career strategy synthesis. Later strategic expansion is now split after Layer 13:

- **Layer 14** owns user-selected model routing, model catalog architecture, Careero Prompt Architecture, model gateway behavior, prompt-only export, quality checks, usage accounting, and credit controls.
- **Layer 15** owns API job sources, official ATS/job-board imports, source snapshots, managed deltas, import candidates, source governance, and review-before-save source workflows.
- **Layer 16** owns guided onboarding, first-search activation, contextual help, feedback capture, and user-support entry points.

Layers 14, 15, and 16 are planning-only in `main`; none of their model catalog, prompt gateway, credit wallet, API job-source ingestion, source snapshot, managed-delta, guided onboarding, onboarding-state, or support-feedback capabilities have been implemented.

---

## Current Repo Reality Summary

### Strongly present / already built

- FastAPI backend
- React + Vite frontend
- Mantine-based UI
- PostgreSQL persistence
- Alembic migrations
- local development scripts and health checks
- default local user seed model
- workspace persistence
- manual role intake
- optional AI-assisted role parsing
- role listing/detail/update/archive
- resume/profile source storage and versions
- active resume/profile source grounding
- COMPASS evaluation generation, deterministic scoring, optional OpenAI enrichment, metadata, input hashing, and caching/reuse
- canonical TypeScript/Zod contracts and generated JSON Schema contracts
- resume and cover-letter artifact generation services
- GeneratedArtifact persistence, truthfulness checks, and artifact performance records
- application persistence, state machine, state history, list/detail APIs, and pipeline APIs
- application notes, external links, structured interviews, local reminders, timeline aggregation, and activity log
- local integration adapter boundary and backend local Markdown/DOCX/PDF artifact export
- automation suggestion persistence, approval logs, workspace automation preferences, and review surfaces
- search analytics, artifact performance analytics, COMPASS insights, source intelligence, compensation intelligence, search health, recommendations, historical learning, and dashboard surfaces

### Partially built / needs reconciliation or validation

- Local application reminders exist but remain local workflow records only; no cloud scheduling, calendar sync, email notifications, or external reminder delivery exists.
- External-link workflow summaries exist and application list/detail summary counts include links alongside notes, reminders, and interviews.
- Private remote branch or PR drift, if any, must be validated before being treated as complete.
- Layer 5 insight stabilization and Layer 6 artifact lifecycle remain important near-term completion work after Layer 4D hardening.

### Not yet built / still future

- production authentication hardening and account recovery
- real multi-user tenant behavior
- production authorization hardening
- billing/subscriptions
- production deployment architecture
- runtime workspace switching UX
- mature workspace management UX
- first-run guided onboarding workflow
- persisted per-user onboarding state
- tour skip/resume/replay behavior
- contextual empty-state onboarding guidance
- support/help/bug/suggestion feedback capture
- privacy-safe support payload governance
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
- Careero Prompt Architecture / modular prompt compiler architecture beyond current artifact-generation prompt foundations
- model gateway, prompt-only export, model task defaults, and model price snapshots
- credit wallet, durable credit ledger, usage metering, credit reservation/debit/refund, rollover, top-ups, or billing-linked credits
- API-only job-source adapters from official ATS/job-data providers
- imported job posting source records, immutable snapshots, import candidates, managed deltas, or review-before-save import workflows
- API source governance, provider validation, source storage policy, and source-freshness tracking
- scraping or restricted-source extraction; this is explicitly deferred for later legal/product/technical review

---

## Revised Layer Status Table

| Layer | Revised name | Revised status | Notes |
| --- | --- | --- | --- |
| Layer 0 | Product Foundation | Built / defined | Product mission, user-first posture, search-track concept, AI governance, UX philosophy, monetization caution, and risk boundaries are defined. |
| Layer 1 | Local Platform Foundation | Built locally / first-party password auth foundation started; production incomplete | Local backend, frontend, database, migrations, config, seed model, email/password registration/login, and local HttpOnly session cookies exist. Production auth hardening, account recovery, SSO, tenancy, and authorization hardening remain future. |
| Layer 2 | Intake, Parsing & Grounding | Mostly built | Manual role intake, AI-assisted parsing, resume/profile source storage, active source grounding, and local imports exist. Parser confidence UX and richer source normalization remain. |
| Layer 3 | COMPASS + Artifact Foundation | Mostly built / lifecycle incomplete | COMPASS and artifact generation foundations exist. Artifact review, edit, approval, export, submitted tracking, and retrieval UX remain. |
| Layer 4 | Application Workflow | Complete for current local MVP scope | Applications, state transitions, timeline, notes, external links, local reminders, structured interview tracking, archive/reactivate, workspace context, workflow UX, and regression coverage exist. Cloud reminders, notification delivery, calendar sync, email integration, hosted automation, production auth, and Layer 11 readiness gates remain future. |
| Layer 5 | Workflow Intelligence / Insights | Partially built / next focus | Analytics and dashboard surfaces exist. Needs validation, workspace filtering, confidence calibration, thin-data handling, and cohesive insight behavior. |
| Layer 6 | Advanced COMPASS + Artifact Lifecycle | Partially built / next lifecycle layer | Build artifact lifecycle UX, COMPASS history, evidence mapping, submitted artifacts, and export flow. |
| Layer 7 | Opportunity Model Strategy | In progress / compatibility surface started | Opportunity-facing API and UX aliases have started while persistence remains Role-backed. Destructive rename remains future. |
| Layer 8 | Integrations | Partially built / local export started | Local integration adapter boundary and backend Markdown/DOCX/PDF artifact export exist. Frontend export workflow, Google Docs, Gmail/Outlook, calendar, browser/share, and cloud sync remain future. |
| Layer 9 | Automation Guardrails | Partially built / local guardrail foundation started | Durable suggestions, approval logs, workspace preferences, and review surfaces exist. External actions, batch approvals, and state-changing automation remain prohibited/future. |
| Layer 10 | Advanced Search Tracks / Career Strategy | Partially built / derived strategy synthesis MVP started | Read-only workspace strategy summary and internal cross-track comparison exist. No durable strategy tables, external market data, AI strategy memory, or automation mutation. |
| Layer 11 | Productization / Deployment / Monetization | Future / readiness surface and local foundations started | Productization, privacy/data governance, account lifecycle, AI usage/cost controls, monetization boundaries, and deployment gates are documented. Local readiness, current-user context, local auth, local export, lifecycle request tracking, local AI usage events, and local entitlement reporting exist. Production auth hardening, account recovery, OAuth/SSO, billing, tenant isolation, hosted export/delete, retention enforcement, paid quotas, credits, and production deployment remain future. |
| Layer 12 | Advisor / Collaboration Mode | Future / local-only packet preview started | Advisor collaboration readiness is documented in `docs/03_domain-design/advisor-collaboration-mode.md`. Local-only redacted advisor packet preview/Markdown export and redaction metadata exist for application detail. Hosted collaboration, advisor accounts, invitations, comments, public links, external sharing, and employer/recruiter visibility remain future. |
| Layer 13 | Marketplace / Employer-Side Exploration | Future / last employer-facing layer | Recruiter-facing workflows, ethical matching, user-controlled visibility, employer partnerships, strict disclosure rules. |
| Layer 14 | Model Catalog, Prompt Architecture & Credit Controls | Future / appended model strategy layer | Planning source exists in `docs/02_layers/14_layer-14-model-catalog-and-prompt-management.md`. No model catalog, prompt compiler/gateway, model task defaults, prompt-only export, quality-check pipeline, credit ledger, or model-cost controls exist in `main`. May be pulled forward with Layer 11 when model usage, billing, and cost controls are actively scoped. |
| Layer 15 | API Job Sources, Import Pipelines & Managed Deltas | Future / appended API intelligence layer | Planning source exists in `docs/02_layers/15_layer-15-api-job-sources-and-managed-deltas.md`. No ATS/job-data provider adapters, job source connections, job posting snapshots, import candidates, managed deltas, or API source governance exist in `main`. Waits on Opportunity semantics and integration boundaries; scraping remains out of scope. |
| Layer 16 | Guided Onboarding & First Search Activation | Future / appended onboarding and support layer | Planning source exists in `docs/02_layers/16_layer-16-guided-onboarding-and-support.md`. No persisted onboarding state, guided first-run flow, tour skip/resume/replay behavior, contextual onboarding empty states, or support/feedback capture exists in `main`. COMPASS setup should be encouraged but not required before first value. |

---

# Layer Details

## Layer 0 â€” Product Foundation

Layer 0 defines the product conscience for Careero. Careero should remain job-seeker-first, AI-grounded, source-traceable, emotionally humane, and search-track-aware.

## Layer 1 â€” Local Platform Foundation

Layer 1 provides the local-first technical foundation. It is built locally but production incomplete. Production auth hardening, account recovery, OAuth/SSO, multi-user account support, tenant isolation, secrets/config hardening, and deployment-ready environment modeling remain future.

## Layer 2 â€” Intake, Parsing & Grounding

Layer 2 turns raw job/opportunity and source-material input into structured, reviewable, grounded system data. It is stable enough to build on, while parser confidence UX, source deduplication, company/source/recruiter normalization, and Google Docs import remain future.

## Layer 3 â€” COMPASS + Artifact Foundation

Layer 3 evaluates opportunities and generates grounded application artifacts. Generation foundations exist, but artifact lifecycle, submitted version tracking, artifact comparison, artifact retrieval UX, and explicit internal-strategy vs employer-facing separation remain future.

## Layer 4 â€” Application Workflow

Layer 4 manages saved-opportunity workflow and is complete for current local
MVP scope. Applications, states, notes, external links, local reminders,
interviews, timeline, archive/reactivate, workspace context, and workflow UX are
built locally. Hosted reminders, notifications, calendar sync, email
integration, production auth dependencies, artifact lifecycle, and insight
stabilization remain later-layer work.

## Layer 5 â€” Workflow Intelligence / Insights

Layer 5 turns workflow activity into useful guidance. Analytics and dashboards exist, but validation, workspace filtering, confidence calibration, insufficient-data handling, and signal explainability need stabilization.

## Layer 6 â€” Advanced COMPASS + Artifact Lifecycle

Layer 6 should turn generated output from â€œAI resultâ€ into durable, inspectable, user-approved product records through evidence mapping, comparison, lifecycle states, submitted tracking, review/edit/export flows, and strict employer-facing artifact boundaries.

## Layer 7 â€” Opportunity Model Strategy

Layer 7 defines Opportunity as the central durable intelligence object. Opportunity-facing API and UX aliases have started while persistence remains Role-backed. The destructive Role-to-Opportunity persistence rename remains a separate future decision.

## Layer 8 â€” Integrations

Layer 8 reduces manual entry through integrations while preserving review-before-save, review-before-send, no-auto-apply, and TruthGuard boundaries. Local/manual integration paths come first; OAuth, account-linked sync, background polling, and external token storage remain future.

## Layer 9 â€” Automation Guardrails

Layer 9 automates repetitive actions safely while preserving user control. Automation should suggest or draft before it acts. External communication, batch approvals, and state-changing automation remain prohibited until review/audit boundaries are mature.

## Layer 10 â€” Advanced Search Tracks / Career Strategy

Layer 10 makes Careero more strategic by helping users evaluate whether their overall search strategy is working. Current strategy synthesis remains read-only, advisory, source-visible, and based on stored Careero evidence only.

## Layer 11 â€” Productization / Deployment / Monetization

Layer 11 turns Careero into a sustainable product without compromising trust. Current work is readiness and local foundations only. Layer 14 may be pulled forward with Layer 11 only when billing, metering, model usage, and credit controls are actively scoped. Layer 15 should not be treated as part of Layer 11 productization unless API-source costs and provider governance are explicitly included.

## Layer 12 â€” Advisor / Collaboration Mode

Layer 12 allows trusted external help while preserving privacy boundaries. Current implementation is local-only packet preview/export scaffolding and does not start hosted collaboration implementation.

## Layer 13 â€” Marketplace / Employer-Side Exploration

Layer 13 remains the last employer-facing/marketplace expansion. Careero should not compromise user trust by becoming employer-first too early.

## Layer 14 â€” Model Catalog, Prompt Architecture & Credit Controls

Active planning source: `docs/02_layers/14_layer-14-model-catalog-and-prompt-management.md`.

Layer 14 owns user-selected model choice, model catalog architecture, Careero Prompt Architecture, prompt-only export, model gateway behavior, quality checks, usage accounting, and credit controls.

Layer 14 may be pulled forward with Layer 11 productization when model usage, billing, metering, and cost controls are actively scoped. It does not include API job-source ingestion; that work belongs to Layer 15.

Layer 14 should make Careero flexible without making it chaotic. Users may choose model and budget; Careero should control prompt structure, source grounding, no-fabrication policy, output contracts, quality checks, cost estimates, and credit ledger behavior.

Candidate sublayers:

- Layer 14A: Careero Prompt Architecture & Prompt Compiler.
- Layer 14B: Model Catalog, Provider Adapters & Model Gateway.
- Layer 14C: Prompt-Only Export & User Model Defaults.
- Layer 14D: Quality Checks, Usage Metering & Credit Ledger.

Do not implement API job-source ingestion, ATS adapters, imported job snapshots, managed deltas, or source refresh logic in Layer 14.

## Layer 15 â€” API Job Sources, Import Pipelines & Managed Deltas

Active planning source: `docs/02_layers/15_layer-15-api-job-sources-and-managed-deltas.md`.

Layer 15 owns official-API-first job-source ingestion, imported job records, source snapshots, managed deltas, provider adapters, provenance, and review-before-save flows.

Layer 15 should reduce manual entry without weakening Careero's user-owned data model. Imported postings should be reviewable candidates before they become durable Opportunities. Source snapshots should be immutable. Managed deltas should be visible before they affect user-edited Opportunity fields.

Candidate sublayers:

- Layer 15A: Provider/source validation matrix.
- Layer 15B: Job-source provider adapter interface.
- Layer 15C: Normalized job posting source records and snapshots.
- Layer 15D: Import candidates, deduplication, and Opportunity matching.
- Layer 15E: Managed deltas and field-level review.
- Layer 15F: Future scraping review backlog item.

Hard boundary: Layer 15 is API-only or licensed-source-only. Do not implement scraping, restricted-source extraction, browser-driven collection, or terms-sensitive data collection in this layer. Scraping can be revisited later only through explicit legal, product, privacy, retention, source-terms, operational, and technical review.

## Layer 16 â€” Guided Onboarding & First Search Activation

Active planning source: `docs/02_layers/16_layer-16-guided-onboarding-and-support.md`.

Layer 16 owns the new-user first-search activation path, guided setup, onboarding state, contextual help, and basic support/feedback intake.

Layer 16 should help a user understand Careero quickly, create or select a workspace/search track, add a first opportunity, understand COMPASS, and know how to ask for help or report product issues.

Candidate sublayers:

- Layer 16A: Onboarding state, routing, and first-run eligibility.
- Layer 16B: Guided first-search activation flow.
- Layer 16C: Contextual empty-state guidance.
- Layer 16D: Help drawer and support/feedback capture.
- Layer 16E: Privacy-safe support payload boundaries and review surface.

Hard boundary: Layer 16 must not require COMPASS source-of-truth setup before first value, must not depend on AI availability, and must not silently capture sensitive support context such as raw resumes, raw job descriptions, private notes, compensation strategy, generated artifacts, or COMPASS rationale.

---

# Recommended Immediate Execution Plan

Operational detail for the revised build order, readiness gates, prompt sequence, and Layer 14/Layer 16 pull-forward rules lives in [revised build order execution plan](07_revised-build-order-execution-plan.md). Keep this section concise and avoid duplicating that plan.

## Step 1 â€” Repo Reality Reconciliation

Keep `main` in a clean, truthful state as new feature work lands.

Tasks:

- Review private remote branch/PR drift when external GitHub/PR access is available.
- Confirm reminder implementation against `main`.
- Confirm structured interview tracking remains clean in `main`.
- Keep external links included in application summary counts alongside notes, reminders, and interviews.
- Reconcile migrations carefully.
- Run backend compile/tests.
- Run frontend tests/build.
- Run contracts tests.
- Update README and roadmap docs to match actual implementation.

## Step 2 â€” Layer 4 Completion Pass

Finish the workflow records users expect before modeling Opportunity more deeply.

## Step 3 â€” Layer 5 Insight Stabilization

Make current analytics trustworthy before expanding the intelligence model.

## Step 4 â€” Layer 6 Artifact Lifecycle Completion

Turn generated artifacts into usable product objects.

## Step 5 â€” Layer 7 LEAP Recon: Opportunity Model Strategy

Design the durable Opportunity model before integrations.

## Step 6 â€” Layer 14 LEAP Recon: Model Catalog, Prompt Architecture & Credit Controls

Plan model choice, model catalog architecture, Careero Prompt Architecture, prompt-only export, quality checks, usage accounting, and credit controls without mixing in job-source API ingestion.

Exit criteria:

- Layer 14 implementation slices are ready.
- Model catalog and prompt architecture boundaries are clear.
- Credit economics are transparent and ledger-backed.
- Prompt-only export is specified.
- API job-source ingestion is explicitly deferred to Layer 15.

## Step 7 â€” Layer 15 LEAP Recon: API Job Sources, Imports & Managed Deltas

Plan official-API-first job-source ingestion, imported job records, source snapshots, managed deltas, provider governance, and review-before-save flows.

Exit criteria:

- Layer 15 implementation slices are ready.
- API-only boundary is clear.
- Scraping revisit is tracked as a future TODO only.
- Source snapshots, managed deltas, and source governance rules are explicit.

## Step 8 â€” Layer 16 LEAP Recon: Guided Onboarding & First Search Activation

Plan first-run onboarding, first-search activation, contextual help, feedback capture, and support-reporting boundaries.

Exit criteria:

- First useful action is clear: create/select a workspace/search track and add one opportunity.
- COMPASS is encouraged but not required before first value.
- Skip/resume/replay behavior is defined.
- Support and feedback categories are defined.
- Privacy-safe support payload boundaries are explicit.
- Contextual empty-state guidance is specified.

---

# Revised Build Order

Recommended order from here:

1. Repo reconciliation and roadmap correction.
2. Layer 4 workflow completion. Completed for current local MVP scope after Layer 4D.
3. Layer 5 insight stabilization. Next implementation focus.
4. Layer 6 artifact lifecycle completion.
5. Layer 7 Opportunity Model Strategy and compatibility surface.
6. Layer 8 integrations.
7. Layer 9 automation guardrails.
8. Layer 10 advanced search-track strategy stabilization.
9. Layer 11 productization implementation only after readiness gates are satisfied.
10. Layer 12 advisor/collaboration mode.
11. Layer 13 marketplace/employer-side exploration.
12. Layer 14 model catalog, Careero Prompt Architecture, model choice, usage accounting, and credit controls. Pull forward during Layer 11 if billing/model usage requires it.
13. Layer 15 API job sources, import pipelines, source snapshots, and managed deltas. Keep API-only and after Opportunity/integration boundaries are stable; keep Layer 13 as the last employer-side expansion.
14. Layer 16 guided onboarding, first-search activation, contextual help, and support/feedback capture. Pull forward before broad beta/productization if activation and support readiness become the gating issue.

---

# Preserved Value From Original Plan

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
- API-first job-source intelligence with source snapshots, managed deltas, source freshness, and no scraping in current scope.
- Guided first-search activation that helps users reach value without a heavy setup wall.
- Clear separation between model/prompt architecture, external job-source API ingestion, and onboarding/support activation.

Revise:

- Do not call Layer 1 fully complete until production auth/identity exists.
- Do not call Layer 4 productization-ready just because local reminder API/UI and summary-count reconciliation exist; hosted reminders, external notifications, production auth, and Layer 11 gates remain future.
- Do not call Layer 5 merely next; it is already partially implemented.
- Move Integrations from Layer 7 to Layer 8.
- Introduce Opportunity Model Strategy as Layer 7.
- Add Layer 14 as an appended model catalog, prompt architecture, and credit-control layer. Parts of Layer 14 may execute with Layer 11 productization even though the layer is documented after Layer 13.
- Add Layer 15 as an appended API job-source, import pipeline, source snapshot, and managed-delta layer.
- Add Layer 16 as an appended guided-onboarding, first-search activation, contextual-help, and support-feedback layer.

Delay:

- External integration work before Opportunity semantics are stable.
- Automation that mutates state without user-visible approval/audit.
- Marketplace/employer-side work until user-side trust is strong.
- Any scraping strategy until official APIs, licensed providers, source terms, privacy risks, and retention rules have been reviewed.
- Full support-ticketing, live chat, or customer-success operations until productization and hosted-support requirements justify them.

---

# Strategic Conclusion

Careero has crossed from job tracker into career operations platform.

The next architectural center should be:

> Opportunity as the durable, strategic, historical intelligence object.

Layer 14 adds a second strategic center for productization-scale model intelligence:

> Careero should let users choose the model and budget while Careero controls prompts, source grounding, quality, cost exposure, and credit behavior.

Layer 15 adds a third strategic center for source-governed job intelligence:

> Careero should ingest permitted external job-source data through official APIs, preserve source snapshots, compute managed deltas, and keep the user in control before imported data changes Opportunity records.

Layer 16 adds a fourth strategic center for activation and support readiness:

> Careero should guide users to first value quickly, encourage better COMPASS grounding over time, and provide clear support/feedback paths without turning onboarding into homework.

The long-term strategic system is not merely an AI resume generator. It is a career application intelligence platform where users can generate, compare, import, refresh, and improve job-search materials using the model, source depth, and budget they choose while Careero protects source truth, freshness, user control, and first-session clarity.

This document should be updated whenever implementation reality changes, especially after private PR reconciliation, Layer 4 completion, Layer 7 LEAP Recon output, Layer 14 model/prompt validation, Layer 15 source/provider validation, and Layer 16 onboarding/support validation.



