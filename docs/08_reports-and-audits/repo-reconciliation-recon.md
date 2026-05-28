# Repo Reconciliation Recon

Status: Active  
Doc Type: Audit  
Layer: N/A  
Source of Truth: No  
Last Reviewed: 2026-05-28  
Related Docs:
- docs/01_strategy/00_product-strategy.md
- docs/02_layers/00_layer-index.md
- docs/03_domain-design/00_domain-index.md
- docs/04_ai-and-compass/00_ai-compass-index.md
- docs/06_operations/execution-drift-ledger.md

## 1. Executive Summary

This recon audited the current checkout on `main`. The original request named branch `layer5`, but the local repository is on `main` tracking `origin/main`; this report describes the inspected `main` state only.

The roadmap is broadly aligned with implementation reality, but still has meaningful drift and compatibility debt. The repository is well beyond the original early prototype: it has local platform foundations, first-party local auth, workspaces/search tracks, Role-backed opportunity intake, resume/profile source grounding, COMPASS evaluation, artifact generation foundations, application workflow, analytics, strategy synthesis, automation guardrail foundations, productization readiness surfaces, and local advisor packet preview.

The main correction is not that the roadmap is wrong; it is that several layers are only local, partial, or readiness-oriented. Layer 4 is substantially implemented locally, Layers 5-12 contain partial/local/readiness surfaces, Layers 13-16 remain future or planning only, and the durable Opportunity model remains Role-backed. Recommendations in this report are audit findings only and are not implementation approval.

## 2. Documentation Inventory

| Document | Classification | Notes |
| --- | --- | --- |
| `README.md` | Mostly current with minor drift | Accurately describes local capabilities and out-of-scope items. It still depends on readers understanding that "local-first" does not mean production-ready. |
| `docs/00_start-here.md` | Current | Correctly identifies canonical doc locations and states that active docs use COMPASS while STRIDE is legacy. |
| `docs/01_strategy/00_product-strategy.md` | Mostly current with minor drift | The layer table matches most code evidence. It should be refreshed after this recon to capture branch target and any Layer 4/5/6 nuance. |
| `docs/01_strategy/02_layer-roadmap.md` | Current | Defers to product strategy and layer index. |
| `docs/01_strategy/03_current-layer-status.md` | Mostly current with minor drift | Compact summary is directionally right; details belong in product strategy. |
| `docs/01_strategy/04_cross-layer-impact-map.md` | Needs reconfirmation | Likely useful, but cross-layer impacts should be rechecked after Layer 4/5/6 corrections. |
| `docs/01_strategy/05_monetization-boundary.md` | Current | Correctly keeps monetization behind readiness gates. |
| `docs/01_strategy/06_productization-readiness.md` | Mostly current with minor drift | Aligns with local readiness implementation; production readiness remains blocked. |
| `docs/02_layers/00_layer-index.md` | Current | Canonical layer entry point for Layers 0-16. |
| `docs/02_layers/00_layer-00-product-foundation.md` through `04_layer-04-application-workflow.md` | Mostly current with minor drift | Layers 0-4 are active and substantially represented in code, with production gaps still explicit. |
| `docs/02_layers/05_layer-05-workflow-intelligence-and-insights.md` | Partially stale | Marked Draft and acknowledges distributed detail; implementation is broader than the capsule. |
| `docs/02_layers/06_layer-06-advanced-compass-and-artifact-lifecycle.md` | Partially stale | Correctly says lifecycle is partial, but generated artifact/export foundations exist and should be reconciled with missing UX/lifecycle states. |
| `docs/02_layers/07_layer-07-opportunity-model-strategy.md` | Current | Correctly frames Opportunity as outward semantics while persistence remains Role-backed. |
| `docs/02_layers/08_layer-08-integrations-and-export.md` | Mostly current with minor drift | Backend local artifact export exists; frontend export workflow and external integrations remain future. |
| `docs/02_layers/09_layer-09-automation-guardrails.md` | Mostly current with minor drift | Local durable suggestions, approval logs, and preferences exist; external/state-changing automation remains prohibited. |
| `docs/02_layers/10_layer-10-advanced-search-tracks-and-career-strategy.md` | Mostly current with minor drift | Strategy synthesis exists as read-only workspace/cross-track surfaces; durable strategy memory remains absent. |
| `docs/02_layers/11_layer-11-productization-deployment-and-monetization.md` | Mostly current with minor drift | Readiness surfaces, local auth, data export, usage, lifecycle requests, and entitlements exist; hosted productization remains blocked. |
| `docs/02_layers/12_layer-12-advisor-and-collaboration-mode.md` | Mostly current with minor drift | Local packet preview/export exists; hosted collaboration is not implemented. |
| `docs/02_layers/13_layer-13-marketplace-and-employer-side-exploration.md` | Current / documented only | Future layer; no code implementation found. |
| `docs/02_layers/14_layer-14-model-catalog-and-prompt-management.md` | Current / documented only | Planning source; no model catalog, gateway, prompt-only export, credit ledger, or model-cost controls found. |
| `docs/02_layers/15_layer-15-api-job-sources-and-managed-deltas.md` | Current / documented only | Planning source; no provider adapters, source snapshots, import candidates, or managed deltas found. |
| `docs/02_layers/16_layer-16-guided-onboarding-and-support.md` | Current / documented only | Planning source; no persisted onboarding state, guided flow, help drawer, or feedback capture found. |
| `docs/03_domain-design/*` | Mostly current with minor drift | Good active design references. Artifact and workflow docs should be reconciled after Layer 4/6 hardening. |
| `docs/04_ai-and-compass/*` | Mostly current with minor drift | COMPASS docs are active; prompt management and cost controls are partly future-facing for Layer 14. |
| `docs/05_security-privacy-governance/*` | Mostly current with minor drift | Local account/auth/privacy boundaries are documented; production hardening remains future. |
| `docs/06_operations/execution-drift-ledger.md` | Current | Important source for recent implementation reality and known risks. |
| `docs/07_prompts/*` | Historical/reference only | Generated prompts are not source-of-truth product specs. |
| `docs/08_reports-and-audits/*` | Duplicative or needs consolidation | Useful audit space; recon summaries are reserved but sparse. This report should be indexed here. |
| `docs/99_archive/*` | Historical/reference only | Should not drive current planning except for explicit historical comparison. |

## 3. Implementation Inventory

| Layer | Status | Actual repo state |
| --- | --- | --- |
| Layer 0 - Product Foundation | Implemented | Product principles and strategy are documented. Code reflects user-first local workflow, COMPASS positioning, and explicit production boundaries. |
| Layer 1 - Core Platform | Partially implemented | FastAPI, React/Vite, PostgreSQL, Alembic, local scripts, local password auth, HttpOnly session cookies, current-user context, and ownership helpers exist. Production auth hardening, recovery, OAuth/SSO, tenant isolation, and hosted deployment are missing. |
| Layer 2 - Intake and Parsing | Partially implemented | Manual opportunity/role intake, optional AI parsing, resume/profile source storage, versions, active source grounding, and file import exist. Parser confidence UX, richer source normalization, and Google Docs import remain future. |
| Layer 3 - Evaluation and Artifacts | Partially implemented | COMPASS deterministic rules, optional OpenAI enrichment, caching, audit metadata, resume and cover-letter generation, generated artifact persistence, and truthfulness checks exist. Artifact lifecycle UX and submitted tracking remain incomplete. |
| Layer 4 - Application Workflow | Partially implemented | Application workflows, state machine, state history, notes, external links, reminders, interviews, timeline, pipeline APIs, and routed application detail UI exist. Hosted reminders, notification delivery, calendar/email sync, and production workflow hardening remain missing. |
| Layer 5 - Insights | Partially implemented | Dashboard analytics, search analytics, COMPASS insights, source intelligence, compensation intelligence, search health, recommendations, historical learning, and artifact performance surfaces exist. Confidence calibration, workspace filtering consistency, and actionability need stabilization. |
| Layer 6 - Artifact Lifecycle | Partially implemented | Generated artifacts and backend Markdown/DOCX/PDF export exist. Dedicated artifact list/detail/review/edit/approve/archive UX, submitted artifact tracking, comparison, and employer-facing/internal-strategy separation remain missing. |
| Layer 7 - Opportunity Model Strategy | Partially implemented | Opportunity-facing frontend routes and backend aliases exist, but persistence remains `Role`, `roles`, and `role_id` based. Destructive rename is not done and should remain a separate decision. |
| Layer 8 - Integrations | Partially implemented | Local integration adapter boundary and backend local artifact export exist. Google Docs, Gmail/Outlook, calendar sync, browser/share intake, OAuth, and cloud sync are missing. |
| Layer 9 - Automation Guardrails | Partially implemented | Automation suggestions, approval logs, workspace preferences, and review UI exist. External actions, batch approvals, and silent state mutation remain prohibited/future. |
| Layer 10 - Advanced Search-Track Strategy | Partially implemented | Read-only workspace strategy synthesis and cross-track comparison exist. No durable strategy tables, external market data, hidden strategy memory, or automation mutation found. |
| Layer 11 - Productization / Deployment / Monetization | Partially implemented | Local readiness endpoint/UI, account lifecycle requests, local data export, AI usage metadata, entitlement reporting, and local password auth exist. Billing, subscriptions, production deployment, hosted export/delete, retention enforcement, credits, and paid quotas are missing. |
| Layer 12 - Advisor / Collaboration Mode | Stubbed | Local-only advisor packet preview and Markdown export exist with redaction metadata. Hosted advisors, invitations, comments, permissioning, public links, external sharing, and revocation/audit workflows are missing. |
| Layer 13 - Marketplace / Employer-Side Exploration | Documented only | No recruiter/employer marketplace implementation found. |
| Layer 14 - Model Catalog / Prompt Architecture / Usage Accounting | Documented only | Local AI usage events exist, but no model catalog, provider gateway, prompt compiler, prompt-only export, credit ledger, wallet, reservation/debit/refund flow, or model-cost control surface found. |
| Layer 15 - API Job Sources / Import Pipelines / Managed Deltas | Documented only | Source type enums include ATS/job-source names, but no official provider adapters, imported posting records, immutable source snapshots, import candidates, deduplication, managed deltas, or source governance implementation found. |
| Layer 16 - Guided Onboarding / Help / Support / Feedback | Documented only | No onboarding state, first-run guided flow, skip/resume/replay, help drawer, support ticket/feedback capture, or privacy-safe support payload review surface found. |

## 4. Doc-to-Code Mismatch Matrix

| Area | Doc claim | Actual repo state | Severity | Recommended correction | Suggested follow-up prompt |
| --- | --- | --- | --- | --- | --- |
| Branch target | User prompt requested `layer5` | Local checkout is `main...origin/main` | Medium | State audit target explicitly; do not imply `layer5` was inspected. | Repo B - Roadmap/docs correction |
| Layer 4 readiness | Docs say workflow is substantially built locally | Code supports local workflow records and UI, but hosted reminders/notifications/calendar/email are absent | Medium | Keep "substantially built locally"; avoid productization-ready language. | Layer 4A - Workflow recon |
| Application reminders | Older frontend README says fuller reminder UI is not merged | Current code has `ApplicationRemindersPanel`, routes, tests, and backend CRUD/complete APIs | Medium | Update frontend README and any stale Layer 4 note to reflect reminder UI exists locally. | Layer 4B - Application state and timeline completion |
| Opportunity model | Docs say Opportunity-facing compatibility has started | Code uses `/opportunities` aliases and UI labels, but persistence remains Role-backed | High | Keep compatibility language explicit; do not schedule destructive rename without Layer 7 recon. | Layer 7 - Opportunity model compatibility prompt |
| Artifact lifecycle | Docs describe durable lifecycle goals | Code has generated artifact persistence and export, but no dedicated artifact lifecycle UI | High | Split "generation/export foundation exists" from "lifecycle incomplete." | Layer 6 - Artifact lifecycle completion |
| Layer 5 insights | Strategy says analytics surfaces exist but need stabilization | Code has many analytics endpoints and dashboard sections, but trust/quality consistency needs validation | Medium | Add Layer 5 stabilization criteria around workspace filtering, confidence, insufficient-data messaging, and basis strings. | Layer 5 - Insight stabilization |
| Layer 8 export | Docs say local export started | Backend export exists; dedicated frontend artifact export workflow is missing | Medium | Keep backend/frontend distinction explicit. | Layer 8 - Local export UX recon |
| Layer 11 productization | Docs describe readiness/local foundations | Code has local readiness, auth, export, lifecycle, usage, entitlement surfaces but no hosted productization | High | Keep production blockers prominent. | Layer 11 - Productization gate hardening |
| Layer 12 collaboration | Docs frame hosted collaboration as future | Code has local advisor packet preview/export only | Medium | Preserve "local-only owner-visible" language. | Layer 12 - Collaboration boundary hardening |
| Layer 14 usage accounting | Docs include credit controls | Code has local AI usage events but no credit ledger or model catalog | High | Avoid implying usage events equal Layer 14 accounting. | Layer 14 - Model catalog and credit controls recon |
| Layer 15 source imports | Docs describe API job sources and managed deltas | Code has source enums and manual source metadata, no import pipeline | Blocking | Keep Layer 15 deferred until Opportunity and integration boundaries are stable. | Layer 15 - API job sources recon |
| Layer 16 onboarding | Docs describe guided first-search activation | Code has no onboarding/support state or routes | High | Treat as documented only; consider minimum early subset before beta. | Layer 16 - Guided onboarding recon |
| Docs location | Prompt suggested `docs/recon` | Repo convention uses reports/audits and recon summaries | Low | Store this report in `docs/08_reports-and-audits/` and index it. | Repo B - Roadmap/docs correction |

## 5. Stale Terminology Audit

Targeted search: `rg -n "\bSTRIDE\b|\bLSROP\b" docs backend frontend packages README.md`.

| Term | Found state | Classification | Recommended handling |
| --- | --- | --- | --- |
| `STRIDE` | Found only in `docs/00_start-here.md`, `docs/04_ai-and-compass/00_ai-compass-index.md`, and `docs/04_ai-and-compass/compass-evaluation-model.md` as explicit legacy terminology guidance. | Preserved as historical | Leave alone. These references explain that active guidance uses COMPASS. |
| `LSROP` | No references found in inspected repo. | Left alone | No action. |
| `COMPASS` | Broad active use in docs, contracts, backend services, tests, and frontend UI. | Left alone | Current canonical term. Review only for places that imply unsupported product completeness. |
| `workspace` | Broad active use in docs/code. | Reviewed manually | Concept is current. UX management/switching is weaker than backend persistence. |
| `search track` | Used as product language for workspace-scoped search strategy. | Reviewed manually | Keep paired with workspace until Layer 7/10 terminology is settled. |
| `strategy` | Active in Layer 10 docs, backend strategy API, frontend Strategy page, and contracts. | Reviewed manually | Keep read-only/advisory boundaries explicit. |
| `opportunity` | Active public term in routes/UI/contracts, backed by Role persistence. | Reviewed manually | Preserve public term; document Role-backed compatibility debt. |
| `artifact` | Active in generation, export, contracts, analytics, and docs. | Reviewed manually | Distinguish generated draft/export foundations from full lifecycle. |
| `layer` | Active LEAP planning term across docs. | Left alone | Current planning taxonomy. |

No mass terminology replacement is recommended.

## 6. Route and UX Structure Audit

Frontend route evidence lives in `frontend/src/App.tsx`. The app has protected routes for Dashboard, Career strategy, Opportunities, Applications, and Settings, with redirects from legacy `/roles` paths to canonical opportunity paths.

Current routed workspaces:

- Dashboard: `/dashboard/:section`, with 9 sections from `frontend/src/pages/DashboardPage.tsx`.
- Strategy: `/strategy/:section` and `/workspaces/:workspaceId/strategy/:section`, with 10 sections from `frontend/src/pages/StrategyPage.tsx`.
- Opportunity detail: `/opportunities/:opportunityId/:section`, with 5 sections from `frontend/src/pages/RoleDetailPage.tsx`.
- Application detail: `/applications/:applicationId/:section`, with 8 sections from `frontend/src/pages/ApplicationDetailPage.tsx`.
- Settings: `/settings/:section`, with 8 sections from `frontend/src/pages/SettingsPage.tsx`.

Findings:

- The repo has moved away from fully panoramic single pages; major pages now use routed local sections.
- Dashboard and Strategy are still dense workspaces. They avoid showing every section at once, but individual sections still lean on card/table/report layouts and should be pressure-tested for "what do I do next?" clarity.
- Application detail is functionally broad. Interviews, reminders, suggestions, advisor packet, notes, links, and timeline are routed, but the overview is thin and does not yet guide the user through next workflow action, artifact readiness, or COMPASS/application context.
- Settings is correctly sectioned but still reads like a local admin console. Runtime/readiness/account/usage/plan areas remain utilitarian rather than user-guided.
- Workspace switching exists most clearly in Strategy. A mature global workspace/search-track context indicator and management UX is still missing.
- Dedicated artifact list/detail/review/edit/approve/archive/export UI is missing despite backend artifact persistence and export.
- Layer 16 onboarding/help/support empty-state guidance is not implemented. Existing empty states are local and feature-specific, not a cohesive first-search activation system.
- Sidebar/global navigation is compact and limited to implemented areas, which is good. The risk is discoverability of section-specific work inside dense feature workspaces.

## 7. Data Model and API Audit

Backend router evidence lives in `backend/app/main.py` and `backend/app/api/*`. Core data model evidence lives in `backend/app/models.py`.

Implemented backend/data areas:

- User and AuthSession models support local first-party password auth.
- Workspace, Company, Role, JobSource, ResumeSource, ResumeSourceVersion, CompassEvaluation, Application, ApplicationStateHistory, ApplicationNote, ApplicationReminder, ApplicationInterviewStage, ApplicationExternalLink, GeneratedArtifact, ArtifactPerformanceRecord, AutomationSuggestion, AutomationApprovalLog, AccountLifecycleRequest, AIUsageEvent, and ActivityLog models exist.
- Ownership/current-user helpers exist in `backend/app/services/current_user.py` and `backend/app/services/ownership.py`.
- Opportunity-facing APIs in `backend/app/api/opportunities.py` wrap Role services.
- Application APIs cover create/get/list/pipeline, metadata update, transitions, timeline, notes, reminders, interviews, external links, and workspace-scoped aliases.
- COMPASS APIs cover create/latest/list/get evaluation flows.
- Artifact generation and export APIs exist for resume/cover letter generation and local artifact exports.
- Analytics APIs cover search, COMPASS, source, compensation, search health, recommendations, history, artifact performance, and strategy.
- Productization/readiness APIs cover local readiness, export, account lifecycle requests, AI usage, and entitlements.

Gaps and risks:

- Ownership checks are present for core user/workspace/role/application services, but every newer service should continue to be audited for current-user scoping before hosted use.
- Opportunity/workspace semantics are incomplete because public Opportunity routes are Role-backed. This is acceptable compatibility debt, not a finished model.
- Application state has a real state machine and history, but Role status remains a parallel lightweight status. Avoid letting Role status re-become workflow authority.
- Timeline is an aggregate read model over typed tables and activity logs, not a dedicated timeline table. This is fine locally, but future event semantics need careful versioning if external integrations are added.
- Reminders are local workflow records only. They are not notification jobs, calendar events, or email reminders.
- Interview tracking is manual-only. No calendar sync, meeting generation, email parsing, or scheduling assistant exists.
- Artifact traceability exists through generated artifact metadata/contracts and links to workspace/role/application/evaluation/source inputs, but lifecycle state, user approval, submitted version, comparison, retrieval, and frontend export workflows are incomplete.
- COMPASS traceability is stronger than most areas: prompt/ruleset versions, hashes, AI status, source hash, metadata, and activity logs exist. Layer 14 prompt architecture/model gateway is still absent.
- Integration/import boundary risk is high for Layer 15: SourceType enums and manual metadata must not be mistaken for provider adapters, imported posting snapshots, or managed deltas.

## 8. Testing Audit

Test evidence lives in `backend/tests`, `frontend/src/**/*.test.tsx`, and `packages/contracts/tests`.

| Area | Current coverage | Missing or needs hardening |
| --- | --- | --- |
| Opportunity workflow | Backend role/opportunity API tests and frontend route/list/detail tests exist. | More tests around Role-backed Opportunity compatibility during future Layer 7 changes. |
| Application state transitions | Strong backend service/API/state-machine tests exist, including reactivation and pipeline behavior. | More frontend tests for transition controls and user-facing invalid transition feedback if controls expand. |
| Notes | Backend CRUD/scoping/timeline tests and frontend panel tests exist. | Hosted/privacy review before support/advisor contexts expose note-derived data. |
| Reminders | Backend CRUD/complete/next-action tests and frontend reminder panel tests exist. | Tests for future notification/calendar behavior are missing because those features do not exist. |
| Timelines | Backend timeline aggregation tests and frontend timeline component/detail route tests exist. | More regression tests as artifact lifecycle and external integrations add event sources. |
| Archive/reactivate | Workspaces, roles, and application reactivation behavior have tests. | Cross-feature UX tests for archived/reactivated objects could be expanded. |
| Dashboard queries | Backend analytics tests and frontend Dashboard route tests exist. | Workspace filtering consistency, confidence calibration, and insufficient-data behavior need broader end-to-end validation. |
| Artifact lifecycle | Resume/cover-letter generation, export, performance, and contracts tests exist. | Dedicated artifact lifecycle tests are missing because review/edit/approve/archive/submitted UI and state are missing. |
| Ownership/access control | Local-user boundary tests exist for workspace, role, application, child records, export, usage, lifecycle. | Hosted tenant isolation, support/admin access, OAuth/session hardening, and production authorization tests are missing. |
| COMPASS/AI boundaries | COMPASS rules, prompt, AI fallback, validation, caching, metadata, and contracts tests exist. | Layer 14 prompt compiler/model gateway/credit ledger tests are missing because those capabilities do not exist. |
| Onboarding/support | No meaningful tests found. | Needed when Layer 16 introduces onboarding state, help drawer, feedback/support capture, and privacy-safe payload review. |

No broad test suite was run for this doc-only recon. Targeted `rg` verification commands were run to inventory terminology, routes, backend APIs, and test coverage.

## 9. Recommended Corrected Build Order

The documented revised build order should remain mostly unchanged. Repo evidence supports finishing local workflow and lifecycle gaps before adding external integrations, model marketplaces, job-source ingestion, or employer-facing surfaces.

Recommended order:

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
12. Layer 14 model catalog, Careero Prompt Architecture, model choice, usage accounting, and credit controls.
13. Layer 15 API job sources, import pipelines, source snapshots, and managed deltas.
14. Layer 16 guided onboarding, first-search activation, contextual help, and support/feedback capture.

Adjustment guidance:

- Pull Layer 16 earlier only as a minimum safe subset if beta activation becomes blocked. Minimum subset: contextual empty states, first-search guidance, skip/resume local onboarding state, and privacy-safe feedback draft capture. Do not add full support desk, live chat, or sensitive payload capture.
- Pull Layer 14 earlier only where productization requires model usage/metering/cost controls. Minimum subset: provider/model registry metadata, task-level defaults, safe usage accounting, cost estimates, and non-billing credit ledger design. Do not mix in API job-source ingestion.
- Keep Layer 15 after Opportunity semantics and integration boundaries are stable. No scraping or restricted-source extraction should be introduced in the current plan.

## 10. Follow-Up Prompt Plan

1. Repo B - Roadmap/docs correction
   - Update source-of-truth docs and READMEs to reflect this recon, especially branch target, local reminder UI, Layer 5 stabilization needs, Layer 6 lifecycle gaps, and Role-backed Opportunity compatibility debt.

2. Layer 4A - Workflow recon
   - Reconfirm application workflow code/docs/UX after reminder and interview work. Identify the smallest remaining local workflow completion pass.

3. Layer 4B - Application state and timeline completion
   - Harden state transitions, timeline event consistency, archive/reactivate behavior, next-action sync, and typed child record counts.

4. Layer 4C - Workflow UX completion
   - Improve application detail overview, next-action guidance, workspace context indicators, and task-oriented workflow affordances without adding external notifications or calendar/email integrations.

5. Layer 4D - Tests and docs hardening
   - Add regression tests for any Layer 4 fixes and update docs to avoid productization-ready claims.

6. Layer 5 - Insight stabilization
   - Validate workspace filtering, insufficient-data messaging, confidence/basis strings, and dashboard actionability.

7. Layer 6 - Artifact lifecycle completion
   - Add artifact list/detail/review/edit/approve/archive/submitted tracking and frontend export workflow, preserving internal-strategy vs employer-facing boundaries.

8. Layer 7 - Opportunity model compatibility recon
   - Decide whether to keep Role-backed persistence with public Opportunity semantics longer or plan a separate destructive migration.

9. Layer 14 and Layer 16 minimum-subset recons
   - Run only if productization/beta readiness makes cost controls or onboarding/support the actual blocker.

