# Careero Layer 12 LEAP Recon Request

Filled from `templates/leap-recon-template.md` in `mjcataldi/leap_framework` for the current state of `mjcataldi/careero` on `main`.

```text
Run LEAP Recon under LEAP v1.7.

Phase 0 / project baseline status:
- Phase 0 complete? yes
- Phase 0 mode used: Existing project / source-of-truth baseline already established
- Gate decision from Phase 0: Proceed with layer-based planning only if Careero remains job-seeker-first, local-first until product value is proven, AI-grounded, source-traceable, privacy-conscious, humane, and user-controlled. Layer 12 must be treated as advisor/collaboration readiness and boundary design first, not external sharing implementation unless prerequisite auth, privacy, tenant, and artifact boundaries are explicitly approved.
- Human approvals already granted: Layer 0 product foundation is accepted; Careero-specific planning belongs in the Careero repo; reusable methodology belongs in the LEAP repo; marketplace/employer-side features remain last; automation must remain review-first and auditable; monetization must not compromise user trust; production readiness remains future until Layer 11 blockers are resolved.
- Known open questions:
  - Should Layer 12 begin as docs-first collaboration strategy, local-only advisor packet preview, or actual scoped sharing implementation?
  - Who are the first supported advisor personas: career coach, resume reviewer, spouse/family advisor, mentor, recruiter relationship reviewer, or internal self-review persona?
  - What data may be shared by default, and what must remain private unless explicitly selected: STRIDE analysis, compensation targets, private notes, generated artifacts, source resume/profile material, recruiter contacts, interview notes, application history, and opportunity rationale?
  - Should collaboration start with shareable read-only packets only, or with comment-only review workflows?
  - Should shared packets be local/exported artifacts only until production auth and tenant isolation exist?
  - What revocation/audit model is required before any hosted collaboration is allowed?
  - Is the near-term goal personal use with trusted reviewers, future coach/advisor subscription support, or eventual product collaboration capability?

Source-of-truth manifest:
- Manifest path or pasted manifest: README.md current planning hierarchy plus docs/careero-application-plan-and-layer-status.md
- Project charter path: docs/careero-application-plan-and-layer-status.md and Layer 0 strategy synopsis
- MVP boundary path: docs/careero-application-plan-and-layer-status.md and Layer 0 strategy synopsis
- Pressure-test summary path: none found as a dedicated current Careero doc; infer from Layer 0 risk boundaries, productization readiness gates, execution drift ledger, and current layer status only
- Implementation strategy path: docs/careero-application-plan-and-layer-status.md
- Layer map path: docs/careero-application-plan-and-layer-status.md
- Execution log path: docs/execution-drift-ledger.md
- Cross-layer impact map path: docs/cross-layer-impact-map.md
- Layer 11 readiness path: docs/productization-readiness.md plus docs/privacy-data-governance.md, docs/account-lifecycle.md, docs/ai-usage-cost-controls.md, docs/monetization-boundary.md, and docs/deployment-readiness.md
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
  - Layer 11 readiness docs now exist, including productization, privacy/data governance, account lifecycle, AI usage/cost controls, monetization boundary, deployment readiness, cross-layer impact map, and execution drift ledger.
  - Layer 12 is explicitly future in the canonical layer-status document.
  - Repo search found no implemented advisor/collaboration module, no Layer 12-specific doc, and no active Layer 12 branch.
- Known constraints:
  - Careero is local-first and not production-ready.
  - Production auth, tenant isolation, authorization hardening, billing, hosted deployment, account lifecycle implementation, data retention enforcement, and production privacy controls are not implemented.
  - Layer 12 depends directly on account roles, scoped sharing, revocation, audit, artifact boundaries, privacy controls, and tenant/authorization design that are not yet implemented.
  - Layer 4 reminders remain partially reconciled; Layer 5 insights need stabilization; Layer 6 artifact lifecycle remains incomplete; Layer 7 destructive Role-to-Opportunity rename is deferred; Layer 8 integrations are only partially local/manual; Layer 9 automation must not mutate external systems; Layer 10 strategy synthesis is read-only and non-durable; Layer 11 is readiness-only.
  - AI must remain advisor-only, source-grounded, reviewable, and non-fabricating.
  - External sharing must not expose private STRIDE analysis, compensation strategy, notes, recruiter intelligence, or internal decision rationale by default.
  - Any collaboration workflow must preserve user ownership, explicit consent, least-privilege access, revocation, auditability, and review-before-externalization.

Target layer or target task:
- Layer 12 — Advisor / Collaboration Mode

Repo / branch context:
- Repository: mjcataldi/careero
- Base branch: main
- Target branch/worktree, if known: recommend creating a dedicated Layer 12 recon/planning branch after this recon; no Layer 12 branch found during inspection
- Open PRs or active branches to inspect, if known:
  - PR #1: Surface external link counts in application summaries; Layer 4-related and not Layer 12, but relevant because unfinished workflow reconciliation should gate collaboration readiness.
  - No Layer 12 branch found by branch search.
- Areas likely affected:
  - docs/careero-application-plan-and-layer-status.md
  - README.md
  - docs/productization-readiness.md
  - docs/privacy-data-governance.md
  - docs/account-lifecycle.md
  - docs/cross-layer-impact-map.md
  - docs/execution-drift-ledger.md
  - docs/opportunity-model-strategy.md
  - docs/automation-guardrails.md
  - docs/resume-artifact-generation.md
  - docs/cover-letter-artifact-generation.md
  - backend account/user/authorization models if collaboration implementation is later approved
  - backend workspace/opportunity/application/artifact sharing boundary services if later approved
  - backend comments/review/audit models if comment-only collaboration is later approved
  - frontend opportunity/application/artifact packet preview and sharing UI if local-only collaboration scaffolding is approved
  - packages/contracts for shared packet, advisor role, permission, comment, invitation, revocation, and audit schemas if introduced
- Areas not to touch:
  - Do not overwrite generic LEAP methodology in the Careero repo.
  - Do not treat docs/archive/* as current strategy.
  - Do not build marketplace, employer-side, recruiter-side, paid placement, or pay-to-rank capabilities.
  - Do not implement production external sharing until auth, authorization, tenant isolation, privacy controls, export/delete, and revocation/audit requirements are designed and approved.
  - Do not create hidden employer/recruiter visibility.
  - Do not expose internal STRIDE analysis, ATS risk notes, compensation strategy, company commentary, private notes, or decision rationale in employer-facing or advisor-facing materials unless explicitly selected by the user.
  - Do not implement OAuth token storage, external account sync, email sending, auto-apply, batch approvals, or state-changing automation as part of Layer 12.
  - Do not perform destructive Role-to-Opportunity persistence rename unless separately gated under Layer 7C.
  - Do not claim production collaboration readiness unless tests, security/privacy gates, account lifecycle, permission boundaries, revocation, audit, and operational controls are actually present.

Buildout settings:
- Buildout mode: Standard / readiness-first architecture guardrails; local-only preview implementation may be considered only after recon confirms safe scope
- LEAP process tier: Thinking Extended recommended for recon; Pro Standard recommended if the LEAP Prompt will define auth-adjacent collaboration architecture, permission models, privacy gates, or multi-step implementation sequencing
- Codex model: GPT-5.5 Thinking recommended for recon and scoped planning; GPT-5.5 Pro recommended only if generating a high-blast-radius implementation prompt for permissions, sharing, audit, or account-role architecture
- Codex reasoning level: Extended for recon; High/Extended for implementation prompt generation depending on blast radius
- Codex execution mode: recon-only first; do not implement directly from this request
- Production compatibility required: yes for design decisions and privacy/permission boundaries; no for immediate hosted sharing implementation unless explicitly approved
- Destructive changes allowed: no by default; only recommend destructive changes if isolated, justified, and separately gated
- One Build Unit per commit: yes
- Source-of-truth updates required: yes
- Execution log / drift ledger update required: yes, update docs/execution-drift-ledger.md if Layer 12 scope or gate decision is accepted
- Cross-layer impact map update required: yes, update docs/cross-layer-impact-map.md if Layer 12 introduces new dependencies or constraints

Required gate:
- Verify whether the Phase 0 baseline and source-of-truth manifest are sufficient.
- Classify docs as Canonical, Active, Draft, Stale, Archived, Delete Candidate, or Unknown.
- Inspect repo reality before implementation planning when repo access exists.
- Search for already-existing functionality before recommending new work.
- Recommend an explicit Codex execution configuration before LEAP Prompt generation.
- If docs and repo reality conflict, report the conflict before generating a coding-agent prompt.
- If branch/worktree/PR drift affects ownership or merge order, require resolution before prompt generation.
- If model or reasoning level is missing, recommend safe defaults based on scope, ambiguity, and implementation risk.

Layer 12-specific recon requirements:
- Treat Layer 12 as advisor/collaboration readiness, privacy-scoped sharing, comment boundaries, revocation, and audit design first.
- Confirm whether Layer 12 should wait entirely until Layer 11 auth/tenant/account lifecycle blockers are resolved, or whether a local-only collaboration packet/export preview can safely be built now.
- Separate collaboration work into:
  - advisor/collaborator personas,
  - shareable data classes,
  - non-shareable/private data classes,
  - permission matrix,
  - packet/export model,
  - comment-only review model,
  - invitation/access model,
  - revocation model,
  - audit and activity model,
  - privacy/user-trust copy,
  - future production auth/tenant dependencies,
  - explicit non-goals for employer/marketplace visibility.
- Preserve user ownership and explicit consent: nothing should be shared by default.
- Preserve separation between private strategy and shareable/employer-facing materials.
- Confirm how shared opportunity packets relate to Opportunity, Application, Artifact, STRIDE, notes, reminders, interviews, external links, and career strategy synthesis.
- Identify which data should be redacted by default, especially compensation targets, internal STRIDE analysis, ATS/company risk, recruiter notes, personal notes, and sensitive source material.
- Require least-privilege collaboration roles such as viewer, commenter, reviewer, coach, and owner only if implementation is recommended.
- Require revocation and audit semantics before any hosted or persistent advisor access is implemented.
- Require compatibility with Role-backed Opportunity persistence until Layer 7C is approved.
- Require TruthGuard boundaries for any advisor-facing or exported resume/cover-letter packet.
- Require no external send, no auto-apply, no batch approval, and no employer visibility as part of Layer 12.
- Identify any safe Build Units that can be done now as docs/design-only or local-only scaffolding.
- Identify any Build Units that must remain blocked until production auth, tenant isolation, privacy controls, artifact lifecycle, and account lifecycle are implemented.
- Require tests for permission enforcement, packet data selection/redaction, comments, audit logs, revocation, and non-leakage of private fields if implementation is recommended.

Return only the LEAP Recon output first. Do not generate the LEAP Prompt yet.
At the end, ask any material clarification questions that should be answered before generating the LEAP Prompt.
Then remind me that I can say: “Generate the LEAP Prompt.”
```

## Expected Recon sections

```text
# LEAP Recon — Layer 12 Advisor / Collaboration Mode

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
## 19. Recommended Codex Execution Configuration
## 20. Clarification Questions Before LEAP Prompt Generation
## 21. Gate Decision / Next Step
```

## Recommended Codex Execution Configuration section

```text
## 19. Recommended Codex Execution Configuration

| Field | Recommendation | Rationale |
|---|---|---|
| Model | GPT-5.5 Thinking for recon and scoped planning; GPT-5.5 Pro only for high-blast-radius permission/sharing architecture prompts | Layer 12 crosses privacy, authorization, data sharing, artifact boundaries, and future production assumptions. It needs careful reasoning before implementation. |
| Reasoning Level | Extended for recon; High/Extended for implementation depending on blast radius | Collaboration can accidentally leak sensitive job-search data if redaction, permission, and audit boundaries are weak. |
| Execution Mode | Recon-only first; plan-first before any implementation | Repo reality shows Layer 12 is future and blocked by Layer 11/auth/privacy prerequisites. Direct implementation would be premature. |
| Scope Scale | Entire layer recon, then Build Unit-sized docs/design or local-only scaffolding | The layer should be decomposed into permission model, data packet model, comment model, audit/revocation model, and UI scaffolding only if approved. |
| Validation | Tests/lint/typecheck/build plus explicit privacy and non-leakage test cases if implementation proceeds | Permission and redaction behavior must be tested, not eyeballed. |
```
