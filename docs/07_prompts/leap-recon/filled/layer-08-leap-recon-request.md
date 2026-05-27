# Careero Layer 8 LEAP Recon Request

Status: Historical  
Doc Type: Prompt  
Layer: Layer 8  
Source of Truth: No  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/07_prompts/00_prompt-index.md
Filled from `templates/leap-recon-template.md` for the current state of `mjcataldi/careero` on `main`.

```text
Run LEAP Recon under LEAP v1.6.

Phase 0 / project baseline status:
- Phase 0 complete? yes
- Phase 0 mode used: Existing project / source-of-truth baseline already established
- Gate decision from Phase 0: Proceed with layer-based planning, but preserve Careero's job-seeker-first, local-first, AI-grounded, source-traceable, humane workflow boundaries.
- Human approvals already granted: Layer 0 product foundation is accepted; Careero-specific planning belongs in the Careero repo; reusable methodology belongs in the LEAP repo; Layer 8 integrations should come after Opportunity semantics are stable.
- Known open questions:
  - Should Layer 8 start with artifact export, Google Docs import, email/calendar integrations, job-board/browser intake helpers, or a narrower integration adapter foundation?
  - Should Layer 8 wait for Layer 7C destructive persistence rename, or proceed against the Layer 7B Opportunity-facing compatibility surface while persistence remains Role-backed?
  - What minimum source/provenance/contact model is needed before Gmail, Outlook, LinkedIn, or job-board integrations?
  - Should DOCX/PDF/Markdown export be treated as Layer 6 artifact lifecycle completion or Layer 8 integration/export work?
  - Which integrations should remain local/manual import only for MVP versus account-linked OAuth integrations?

Source-of-truth manifest:
- Manifest path or pasted manifest: README.md current planning hierarchy plus docs/01_strategy/00_product-strategy.md
- Project charter path: docs/01_strategy/00_product-strategy.md and Layer 0 strategy synopsis
- MVP boundary path: docs/01_strategy/00_product-strategy.md and Layer 0 strategy synopsis
- Pressure-test summary path: none found as a dedicated current Careero doc; infer from Layer 0 risk boundaries and current layer status only
- Implementation strategy path: docs/01_strategy/00_product-strategy.md
- Layer map path: docs/01_strategy/00_product-strategy.md
- Execution log path: not found as a dedicated current file; use Git history, README, and layer-status doc until an execution/drift ledger exists
- Cross-layer impact map path: docs/01_strategy/04_cross-layer-impact-map.md
- Stale / archived / do-not-use docs: docs/99_archive/*, especially docs/99_archive/strategic-layer-roadmap-legacy.md, unless explicitly requested for historical comparison

Solution/system overview:
- Solution name: Careero
- Solution type: Local-first career operations / job-search workflow platform
- High-level goal: Reduce the chaos, opacity, and emotional exhaustion of modern job searching by giving individuals a structured, intelligent, source-grounded system for managing opportunities, evaluating fit, preparing application materials, and tracking progress across parallel search tracks.
- Current state:
  - Local-first FastAPI backend, React + Vite frontend, PostgreSQL persistence, Alembic migrations, Mantine UI, and local scripts exist.
  - Workspace/search-track persistence exists.
  - Opportunity-facing intake/list/detail/update/archive surfaces exist, but persistence remains Role-backed.
  - Resume/profile source grounding, COMPASS evaluation, artifact generation foundations, application workflow, state history, notes, external links, structured interview tracking, analytics, and dashboard intelligence surfaces exist.
  - Layer 7 Opportunity model strategy exists and Layer 7B compatibility surface has started.
  - Layer 8 integrations are planned, not implemented as current product capability.
- Known constraints:
  - Careero is local-first and not production-ready.
  - Production auth, tenant isolation, billing, deployment architecture, background jobs, OAuth integrations, email/calendar sync, browser extension/share-sheet intake, and automated application submission are not implemented.
  - AI must remain advisor-only, source-grounded, reviewable, and non-fabricating.
  - Integrations must not auto-apply, auto-send, or mutate external systems without explicit review/approval.
  - Imported content should preserve source/provenance and should land on the correct Opportunity/Application/Artifact boundary.
  - Avoid building integrations before Opportunity semantics are stable enough to receive imported data without rework.

Target layer or target task:
- Layer 8 â€” Integrations

Repo / branch context:
- Repository: mjcataldi/careero
- Base branch: main
- Target branch/worktree, if known: recommend creating a dedicated Layer 8 recon/planning branch after this recon; no Layer 8 branch found during inspection
- Open PRs or active branches to inspect, if known:
  - PR #1: Surface external link counts in application summaries; Layer 4-related and not Layer 8, but relevant to workflow-summary reconciliation
  - No Layer 8 branch found by branch search
- Areas likely affected:
  - docs/01_strategy/00_product-strategy.md
  - docs/03_domain-design/opportunity-model.md
  - backend app services/routes/schemas for opportunity intake, source/provenance, artifacts, applications, reminders, interviews, external links, and activity logs
  - frontend opportunity intake/detail/application/artifact surfaces
  - packages/contracts source schemas and generated JSON Schema contracts
  - local development docs and environment/config docs
  - future integration adapter directories/services if introduced
- Areas not to touch:
  - Do not overwrite generic LEAP methodology in the Careero repo.
  - Do not treat docs/99_archive/* as current strategy.
  - Do not perform destructive Role-to-Opportunity persistence rename unless the recon explicitly gates it as required.
  - Do not implement production auth, billing, marketplace, employer-side workflows, automated application submission, or external sending as part of Layer 8 MVP.
  - Do not add vector/embedding-based dedupe unless deterministic matching is shown to be insufficient.

Buildout settings:
- Buildout mode: Rapid POC with architecture guardrails
- Model tier: Thinking Extended recommended for recon; Pro Standard recommended if generating a high-blast-radius implementation plan
- Production compatibility required: no, but avoid choices that make later production auth/privacy/OAuth impossible
- Destructive changes allowed: no for Layer 8 initial recon/prompt; only recommend destructive persistence changes if clearly separated into a future Layer 7C gate
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

Layer 8-specific recon requirements:
- Confirm whether Layer 7B Opportunity-facing compatibility is stable enough for integrations to target `/opportunities` and Opportunity contracts while persistence remains Role-backed.
- Separate integration categories into:
  - import/intake integrations,
  - export/artifact integrations,
  - communication integrations,
  - calendar/scheduling integrations,
  - browser/job-board capture helpers,
  - cloud/source sync,
  - integration adapter foundation.
- Recommend the safest Layer 8 MVP sequence.
- Identify which capabilities should remain manual/local-first first, before OAuth or background sync.
- Identify data ownership boundaries for Opportunity vs Application vs Artifact vs Source/Provenance vs future Contact/Recruiter.
- Identify required contract/schema changes before implementation.
- Identify test fixtures needed for deterministic integration behavior.
- Preserve review-before-save, review-before-send, no-auto-apply, and TruthGuard boundaries.
- Avoid recommending external account linking until local adapter boundaries and source/provenance rules are clear.

Return only the LEAP Recon output first. Do not generate the LEAP Prompt yet.
At the end, ask any material clarification questions that should be answered before generating the LEAP Prompt.
Then remind me that I can say: â€œGenerate the LEAP Prompt.â€
```

## Expected Recon sections

```text
# LEAP Recon â€” Layer 8 Integrations

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



