# Careero Revised Build Order Execution Plan

Status: Active  
Doc Type: Strategy  
Layer: N/A  
Source of Truth: Yes  
Last Reviewed: 2026-05-28  
Related Docs:
- docs/01_strategy/00_product-strategy.md
- docs/01_strategy/03_current-layer-status.md
- docs/02_layers/00_layer-index.md
- docs/08_reports-and-audits/repo-reconciliation-recon.md

## 1. Purpose

This document converts the product strategy build order into an actionable LEAP/LHS execution plan. It should guide prompt sequencing, dependency checks, and scope discipline after the Repo A reconciliation.

Use this file for execution order. Use [product strategy](00_product-strategy.md) for the high-level roadmap and current layer status. Use [Repo reconciliation recon](../08_reports-and-audits/repo-reconciliation-recon.md) as non-canonical audit evidence for the current `main` checkout.

## 2. Current Build Order

1. Repo reconciliation and roadmap correction.
2. Layer 4 workflow completion.
3. Layer 5 insight stabilization.
4. Layer 6 artifact lifecycle completion.
5. Layer 7 opportunity model strategy and compatibility surface.
6. Layer 8 integrations.
7. Layer 9 automation guardrails.
8. Layer 10 advanced search-track strategy stabilization.
9. Layer 11 productization implementation only after readiness gates are satisfied.
10. Layer 12 advisor/collaboration mode.
11. Layer 13 marketplace/employer-side exploration.
12. Layer 14 model catalog, Careero Prompt Architecture, model choice, usage accounting, and credit controls.
13. Layer 15 API job sources, import pipelines, source snapshots, and managed deltas.
14. Layer 16 guided onboarding, first-search activation, contextual help, and support/feedback capture.

Layer 4 is complete for current MVP workflow scope after the Layer 4D hardening
pass. Layer 5 insight stabilization is the next immediate implementation focus.

## 3. Layer Status Table

| Layer | Name | Current status | Dependency status | Next LEAP prompt | Notes |
| --- | --- | --- | --- | --- | --- |
| Layer 0 | Product Foundation | Implemented | Stable enough to guide all later layers. | None unless product direction changes. | Preserve job-seeker-first, grounded AI, and marketplace-last principles. |
| Layer 1 | Core Platform | Partially implemented | Local foundation exists; production hardening is incomplete. | Layer 11 auth/ownership hardening when productization resumes. | Local auth and ownership prep exist; hosted auth, account recovery, SSO, tenant isolation, and deployment remain future. |
| Layer 2 | Intake, Parsing, and Grounding | Partially implemented | Stable enough for Layer 4-6 work. | Source/provenance hardening after workflow priorities. | Manual intake, optional parsing, and resume/profile source grounding exist. |
| Layer 3 | COMPASS and Artifact Foundation | Partially implemented | Stable enough for Layer 4 and Layer 6; lifecycle remains incomplete. | Layer 6 artifact lifecycle completion. | COMPASS traceability is strong; artifact review/submitted lifecycle is not complete. |
| Layer 4 | Application Workflow | Complete for current MVP workflow scope | Lower-layer local foundations exist; hosted/productized delivery remains later. | None unless Layer 4D validation finds a blocker. | State machine, notes, links, reminders, interviews, timeline, pipeline, workflow UX, and regression coverage exist locally. Hosted reminder delivery, calendar/email sync, and production hardening remain future. |
| Layer 5 | Workflow Intelligence and Insights | Partially implemented / next focus | Depends on reliable Layer 4 workflow data, now hardened for local MVP use. | Layer 5 - Insight stabilization. | Dashboard and analytics surfaces exist; workspace filtering, confidence, basis, and thin-data behavior need validation. |
| Layer 6 | Advanced COMPASS and Artifact Lifecycle | Partially implemented | Depends on Layer 3 generation and Layer 4 workflow context. | Layer 6 - Artifact lifecycle completion. | Generated artifacts and backend export exist; lifecycle UX, approval, archive, comparison, and submitted tracking remain missing. |
| Layer 7 | Opportunity Model Strategy | Partially implemented | Depends on stable workflow and artifact semantics. | Layer 7 - Opportunity model compatibility recon. | Public Opportunity language exists while persistence remains Role-backed. |
| Layer 8 | Integrations and Export | Partially implemented | Depends on Opportunity semantics and artifact lifecycle. | Layer 8 - Local export UX / integration recon. | Backend local export exists; frontend artifact export workflow and external integrations remain future. |
| Layer 9 | Automation Guardrails | Partially implemented | Depends on trustworthy workflow and approval boundaries. | Layer 9 - Automation guardrail hardening. | Suggestions, approval logs, and preferences exist; external/state-changing automation remains prohibited. |
| Layer 10 | Advanced Search Tracks and Career Strategy | Partially implemented | Depends on Layer 4/5/6 data maturity. | Layer 10 - Strategy stabilization. | Read-only strategy synthesis exists; no durable strategy memory or external market data. |
| Layer 11 | Productization, Deployment, and Monetization | Partially implemented as readiness/local foundations | Blocked until readiness gates pass. | Layer 11 - Productization gate hardening. | Readiness, local auth, export, lifecycle requests, usage visibility, and entitlements exist locally; hosted productization remains future. |
| Layer 12 | Advisor and Collaboration Mode | Stubbed locally | Hosted mode depends on Layer 11 auth/privacy and Layer 6 artifact lifecycle. | Layer 12 - Collaboration boundary hardening. | Local-only advisor packet preview/export exists; accounts, invitations, comments, sharing, and revocation remain future. |
| Layer 13 | Marketplace and Employer-Side Exploration | Documented only | Blocked behind user-side trust and productization. | Layer 13 recon only after user-side value is proven. | Employer-side concepts remain future and must not distort MVP priorities. |
| Layer 14 | Model Catalog, Prompt Architecture, and Credit Controls | Documented only, with local usage events in Layer 11 | May be pulled forward if Layer 11 cost/model controls require it. | Layer 14A - Prompt architecture / usage accounting recon. | No model catalog, gateway, prompt compiler, prompt-only export, or credit ledger exists. |
| Layer 15 | API Job Sources and Managed Deltas | Documented only | Depends on Opportunity semantics and integration boundaries. | Layer 15 - API job sources recon. | No provider adapters, snapshots, import candidates, or managed deltas exist. |
| Layer 16 | Guided Onboarding and Support | Documented only | May be pulled forward if activation blocks beta readiness. | Layer 16A - Onboarding state / activation recon. | No onboarding state, first-run flow, help drawer, or support/feedback capture exists. |

## 4. Prompt Sequence

Immediate sequence:

1. Repo A - Repository reconciliation recon.
2. Repo B - Roadmap/docs correction.
3. Layer 4A - Workflow recon.
4. Layer 4B - Application state and timeline completion.
5. Layer 4C - Workflow UX completion.
6. Layer 4D - Tests and docs hardening.
7. Layer 5 - Insight stabilization.

Later prompt groups:

- Layer 5 - Insight stabilization: workspace filters, confidence, basis strings, thin-data behavior, and dashboard actionability.
- Layer 6 - Artifact lifecycle completion: artifact list/detail, review/edit/approve/archive, submitted tracking, comparison, and frontend export.
- Layer 7 - Opportunity compatibility: keep Role-backed persistence explicit or plan a separately approved migration.
- Layer 8 - Integrations: start with local/manual export UX before OAuth, cloud sync, or external account linking.
- Layer 9 - Automation: preserve suggestion-first, review-first, audit-first behavior.
- Layer 10 - Strategy: keep strategy read-only, source-grounded, and non-mutating.
- Layer 11 - Productization: implement only after readiness gates are satisfied.
- Layer 12 - Collaboration: keep local-only packet boundaries until hosted auth/privacy/revocation prerequisites exist.
- Layer 13 - Marketplace: defer until user-side trust and product value are proven.
- Layer 14 - Model and prompt controls: pull forward only under the rules below.
- Layer 15 - API job sources: defer until Opportunity and integration boundaries are stable.
- Layer 16 - Onboarding/support: pull forward only under the rules below.

## 5. Readiness Gates Before Layer 11

Layer 11 productization implementation must wait until these gates are satisfied or explicitly scoped into a Layer 11 prompt:

- Auth and ownership checks are validated beyond local-only assumptions.
- Account lifecycle path is defined, including request, export, deletion, retention, and recovery boundaries.
- Export/delete requirements are documented for hosted use.
- Privacy-sensitive data boundaries are reviewed for resumes, raw job descriptions, notes, compensation strategy, generated artifacts, COMPASS rationale, prompts, and support payloads.
- Artifact traceability is implemented enough to support user review and lifecycle decisions.
- COMPASS output traceability is implemented and remains prompt/ruleset/source/hash aware.
- Usage accounting model is ready, or Layer 14A is pulled forward before paid or hosted model usage.
- Workflow tests are passing for application states, notes, reminders, interviews, timeline, archive/reactivate, and ownership.
- UX pass is completed for core flows: opportunity intake, application workflow, artifact lifecycle, dashboard/insights, settings, and workspace context.
- Deployment assumptions are documented, including environment model, secrets, backups, rollback, monitoring, and support expectations.
- MVP value does not depend on employer-side, recruiter-side, marketplace, sponsored, or pay-to-rank functionality.

## 6. Pull-Forward Rules

Layer 14 may be pulled forward only when one or more of these conditions is true:

- AI model usage must be metered for hosted or paid operation.
- Billing or credits require usage accounting.
- Prompt architecture needs standardization before productization.
- Model choice affects cost, latency, output quality, or user-facing behavior.

Minimum safe Layer 14 subset:

- Provider/model registry metadata.
- Task-level model defaults.
- Prompt architecture and prompt compiler boundaries.
- Safe usage accounting and cost estimates.
- Credit ledger design only if billing or credits are in scope.
- No API job-source ingestion; that belongs to Layer 15.

Layer 16 may be pulled forward only when one or more of these conditions is true:

- Users cannot understand first-search setup.
- Activation is a beta-readiness blocker.
- Support/feedback capture is needed before wider usage.
- UX complexity causes avoidable user confusion.

Minimum safe Layer 16 subset:

- First-search activation guidance.
- Contextual empty states.
- Skippable/resumable local onboarding state.
- Help and feedback entry points.
- Privacy-safe support payload review.
- No full support desk, live chat, sensitive automatic capture, or external support workflow unless separately approved.

## 7. Terminology Rules

- COMPASS is the current role-evaluation, fit-analysis, and resume-tailoring framework.
- STRIDE is legacy terminology. Replace it in current product docs and UI only when it is being used as current terminology.
- Preserve STRIDE references that explicitly explain historical naming or migration context.
- LSROP should be treated as historical unless a migration note requires it.
- Workspace is the persisted search context. Search track is the product-facing concept for a user's focused search lane.
- Opportunity is the product-facing term. Current persistence remains Role-backed until a separate destructive migration is approved.
- Employer-side, recruiter-side, marketplace, sponsored placement, and pay-to-rank concepts remain future-facing and must not distort the user-first MVP.

## 8. Scope Discipline

Future LEAP prompts should:

- Analyze existing modules, docs, tests, and migrations before proposing changes.
- Reuse repository patterns and local service/API/component conventions.
- Preserve backward compatibility unless destructive change is explicitly approved.
- Keep changes modular, testable, and tied to one layer or prompt slice.
- Avoid marketplace drift and employer-first incentives.
- Avoid over-automation, especially unreviewed state changes or external actions.
- Maintain truthful, grounded AI outputs with source visibility and no fabricated user experience.
- Keep UX calm, navigable, and progressive-disclosure oriented.
- Record gaps as follow-up work rather than silently implementing adjacent features.
