# Careero Layer 11 LEAP Recon Request

Filled from `templates/leap-recon-template.md` in `mjcataldi/leap_framework` for the current state of `mjcataldi/careero` on `main`.

```text
Run LEAP Recon under LEAP v1.6.

Phase 0 / project baseline status:
- Phase 0 complete? yes
- Phase 0 mode used: Existing project / source-of-truth baseline already established
- Gate decision from Phase 0: Proceed with layer-based planning only if Careero remains job-seeker-first, local-first until product value is proven, AI-grounded, source-traceable, privacy-conscious, and humane. Layer 11 must be treated as productization readiness and boundary design first, not a premature production launch.
- Human approvals already granted: Layer 0 product foundation is accepted; Careero-specific planning belongs in the Careero repo; reusable methodology belongs in the LEAP repo; marketplace/employer-side features remain last; automation must remain review-first and auditable; monetization must not compromise user trust.
- Known open questions:
  - Has the user-side workflow proven enough durable local value to justify any productionization work now, or should Layer 11 remain mostly a readiness/recon/design layer?
  - Which deployment target should be assumed for the first production path: local-only packaged app, single-user hosted app, private beta SaaS, or future multi-tenant SaaS?
  - What authentication model is preferred for first productization: email/password, Google OAuth, GitHub OAuth, passkeys, or a staged local-to-cloud account model?
  - What data classes require explicit privacy and retention rules before hosted deployment: resumes, source materials, STRIDE evaluations, artifacts, notes, recruiter contacts, compensation targets, application history, and AI prompts/outputs?
  - Should billing be deferred entirely until workflow/artifact/integration value is validated, or should Layer 11 only define pricing meters and cost-control boundaries?
  - What AI usage should count against future paid tiers: parsing, STRIDE enrichment, artifact generation, career strategy synthesis, integration summarization, or automation suggestions?
  - What account deletion/export requirements should exist before any hosted beta?

Source-of-truth manifest:
- Manifest path or pasted manifest: README.md current planning hierarchy plus docs/careero-application-plan-and-layer-status.md
- Project charter path: docs/careero-application-plan-and-layer-status.md and Layer 0 strategy synopsis
- MVP boundary path: docs/careero-application-plan-and-layer-status.md and Layer 0 strategy synopsis
- Pressure-test summary path: none found as a dedicated current Careero doc; infer from Layer 0 risk boundaries and current layer status only
- Implementation strategy path: docs/careero-application-plan-and-layer-status.md
- Layer map path: docs/careero-application-plan-and-layer-status.md
- Execution log path: not found as a dedicated current file; use Git history, README, and layer-status doc until an execution/drift ledger exists
- Cross-layer impact map path: not found as a dedicated current file; infer from layer-status doc and opportunity-model-strategy.md until a formal impact map exists
- Stale / archived / do-not-use docs: docs/archive/*, especially docs/archive/strategic-layer-roadmap-legacy.md, unless explicitly requested for historical comparison

Solution/system overview:
- Solution name: Careero
- Solution type: Local-first career operations / job-search workflow platform with future product/SaaS potential
- High-level goal: Reduce the chaos, opacity, and emotional exhaustion of modern job searching by giving individuals a structured, intelligent, source-grounded system for managing opportunities, evaluating fit, preparing application materials, and tracking progress across parallel search tracks.
- Current state:
  - Local-first FastAPI backend, React + Vite frontend, Mantine UI, PostgreSQL persistence, Alembic migrations, local scripts, and local health checks exist.
  - Workspace/search-track persistence exists.
  - Opportunity-facing intake/list/detail/update/archive surfaces exist, while persistence remains Role-backed.
  - Resume/profile source grounding, STRIDE evaluation, artifact generation foundations, application workflow, state history, notes, external links, structured interview tracking, analytics, dashboard intelligence, local integration adapter boundary, backend Markdown/DOCX/PDF export, automation guardrails, and read-only career strategy synthesis foundations exist.
  - Layer 11 is explicitly future in the canonical layer-status document.
- Known constraints:
  - Careero is local-first and not production-ready.
  - Production auth, tenant isolation, authorization hardening, billing, deployment architecture, account lifecycle, data retention, and hosted privacy controls are not implemented.
  - Layer 4 reminders remain partially reconciled; Layer 5 insights need stabilization; Layer 6 artifact lifecycle remains incomplete; Layer 7 destructive Role-to-Opportunity rename is deferred; Layer 8 integrations are only partially local/manual; Layer 9 automation must not mutate external systems; Layer 10 strategy synthesis is read-only and non-durable.
  - AI must remain advisor-only, source-grounded, reviewable, and non-fabricating.
  - Monetization must preserve job-seeker trust and avoid employer-first incentives, pay-to-rank distortion, or pressure mechanics.
  - Do not productize into hosted multi-tenant SaaS until privacy, auth, export/delete, cost controls, and workflow maturity are clear.

Target layer or target task:
- Layer 11 — Productization / Deployment / Monetization

Repo / branch context:
- Repository: mjcataldi/careero
- Base branch: main
- Target branch/worktree, if known: recommend creating a dedicated Layer 11 recon/planning branch after this recon; no Layer 11 branch found during inspection
- Open PRs or active branches to inspect, if known:
  - PR #1: Surface external link counts in application summaries; Layer 4-related and not Layer 11, but relevant because unfinished workflow reconciliation should gate production readiness.
  - No Layer 11 branch found by branch search.
- Areas likely affected:
  - docs/careero-application-plan-and-layer-status.md
  - README.md
  - docs/local-development.md
  - docs/automation-guardrails.md
  - docs/resume-artifact-generation.md
  - docs/cover-letter-artifact-generation.md
  - docs/opportunity-model-strategy.md
  - backend configuration, auth, user/account, privacy/export/delete, usage-metering, and billing boundary modules if introduced
  - frontend account/settings, data export/delete, usage visibility, billing placeholder, and deployment-readiness surfaces if introduced
  - packages/contracts for account, usage, privacy, billing, and lifecycle schemas if introduced
  - infra/README.md and future deployment/IaC docs if deployment planning is scoped
- Areas not to touch:
  - Do not overwrite generic LEAP methodology in the Careero repo.
  - Do not treat docs/archive/* as current strategy.
  - Do not build marketplace, employer-side, recruiter-side, or pay-to-rank capabilities.
  - Do not implement paid placement incentives or sponsored role prioritization.
  - Do not implement production billing before defining privacy, auth, account lifecycle, AI usage metering, and user trust boundaries.
  - Do not implement external sending, auto-apply, background account sync, or state-changing automation as part of Layer 11.
  - Do not perform destructive Role-to-Opportunity persistence rename unless separately gated under Layer 7C.
  - Do not claim production readiness unless tests, security/privacy gates, account lifecycle, deployment docs, and operational controls are actually present.

Buildout settings:
- Buildout mode: Productization readiness / architecture guardrails, not production launch
- Model tier: Thinking Extended recommended for recon; Pro Standard recommended if the LEAP Prompt will define production architecture, privacy model, billing boundaries, or multi-step implementation sequencing
- Reasoning level: Extended for recon; High/Extended for implementation prompt generation depending on blast radius
- Production compatibility required: yes for design decisions, no for immediate hosted launch unless explicitly approved
- Destructive changes allowed: no by default; only recommend destructive changes if isolated, justified, and separately gated
- One Build Unit per commit: yes
- Source-of-truth updates required: yes
- Execution log / drift ledger update required: you recommend; create or update if the repo has a current place for it, otherwise flag absence
- Cross-layer impact map update required: you recommend; create or update if the repo has a current place for it, otherwise flag absence

Required gate:
- Verify whether the Phase 0 baseline and source-of-truth manifest are sufficient.
- Classify docs as Canonical, Active, Draft, Stale, Archived, Delete Candidate, or Unknown.
- Inspect repo reality before implementation planning when repo access exists.
- Search for already-existing functionality before recommending new work.
- If docs and repo reality conflict, report the conflict before generating a coding-agent prompt.
- If branch/worktree/PR drift affects ownership or merge order, require resolution before prompt generation.

Layer 11-specific recon requirements:
- Treat Layer 11 as readiness, trust, deployment, privacy, account lifecycle, cost-control, and monetization-boundary work first.
- Confirm whether prior layers are mature enough to justify productionization now.
- Identify hard blockers to hosted deployment, including auth, authorization, tenant isolation, data export/delete, data retention, sensitive career-data privacy, AI-output traceability, deployment architecture, monitoring, backup/restore, and cost controls.
- Separate productization work into:
  - production readiness gates,
  - deployment architecture,
  - identity/auth/account lifecycle,
  - privacy/data governance,
  - AI usage/cost metering,
  - billing/subscription boundary design,
  - free/paid tier modeling,
  - operational support/readiness,
  - legal/compliance placeholders,
  - documentation and user trust surfaces.
- Recommend the safest Layer 11 MVP sequence without prematurely launching hosted multi-tenant SaaS.
- Identify which pieces can be built locally now as productization scaffolding without committing to a live production service.
- Identify which pieces should stay documentation/design-only until Layer 4-10 maturity improves.
- Preserve job-seeker-first monetization: free useful baseline, paid power-user/AI/artifact tiers only after value is proven, no employer-distorted recommendations, no pay-to-rank roles, no hidden sponsored prioritization.
- Preserve no-auto-apply, review-before-send, TruthGuard, source-grounded AI, and explicit user approval boundaries.
- Require any billing work to be decoupled from Stripe/provider specifics unless a payment provider is explicitly selected.
- Require tests for account lifecycle, data export/delete, usage metering, authorization boundaries, and billing-state transitions if implementation is recommended.
- Require documentation updates that clearly distinguish local POC, private beta, and production readiness.

Return only the LEAP Recon output first. Do not generate the LEAP Prompt yet.
At the end, ask any material clarification questions that should be answered before generating the LEAP Prompt.
Then remind me that I can say: “Generate the LEAP Prompt.”
```

## Expected Recon sections

```text
# LEAP Recon — Layer 11 Productization / Deployment / Monetization

## 1. Framework Interpretation
## 2. Source-of-Truth Manifest Check
## 3. Phase 0 / Baseline Gate Check
## 4. Repo Reality Reconciliation
## 5. Branch / Worktree / PR Drift Review
## 6. Documentation Lifecycle Review
## 7. Strategic Plan Reconciliation
## 8. Existing Functionality Collision Check
## 9. Stale Assumption Scan
## 10. Cross-Layer Impact Scan
## 11. Layer Boundary Review
## 12. Generated / Refined Build Unit Inventory
## 13. Recommended Build Sequence
## 14. Dependency and Destructive-Change Review
## 15. Architecture Right-Sizing Review
## 16. Human Checkpoints Required
## 17. Execution Log / Drift Ledger Expectations
## 18. Coding-Agent Risk Forecast
## 19. Recommended Model Tier
## 20. Clarification Questions Before LEAP Prompt Generation
## 21. Gate Decision / Next Step
```
