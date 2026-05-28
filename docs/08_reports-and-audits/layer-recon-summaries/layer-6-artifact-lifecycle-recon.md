# Layer 6A Artifact Lifecycle Recon

Status: Complete  
Doc Type: Audit  
Layer: Layer 6  
Source of Truth: No  
Last Reviewed: 2026-05-28  
Branch Inspected: `main`  
Related Docs:
- `docs/01_strategy/00_product-strategy.md`
- `docs/01_strategy/07_revised-build-order-execution-plan.md`
- `docs/02_layers/03_layer-03-compass-and-artifact-foundation.md`
- `docs/02_layers/04_layer-04-application-workflow.md`
- `docs/02_layers/06_layer-06-advanced-compass-and-artifact-lifecycle.md`
- `docs/03_domain-design/resume-artifact-generation.md`
- `docs/03_domain-design/cover-letter-artifact-generation.md`
- `docs/03_domain-design/application-workflow-persistence.md`
- `docs/03_domain-design/opportunity-model.md`

This report is recon-only audit evidence. It records current implementation reality before Layer 6B-6E changes. It does not itself approve schema changes, lifecycle routes, UI changes, or submitted-artifact behavior.

## 1. Summary

Layer 6 is partially built. Careero already has grounded resume and cover-letter generation, `GeneratedArtifact` persistence, source/evaluation metadata, revision numbers, artifact export, artifact performance records, application timeline artifact-created events, and advisor-packet redaction warnings.

The missing lifecycle work is concentrated in four areas:

- Canonical artifact lifecycle state is not implemented as durable first-class behavior.
- Review, submit, archive, edit, and version-history operations are absent.
- There is no dedicated artifact detail/list UX.
- Submitted artifact tracking is not protected from mutation and is not clearly tied to the application timeline.

The owner approved the Layer 6 four-state model during recon handoff: `draft`, `reviewed`, `submitted`, and `archived`. Existing `approved` and `exported` terminology should be treated as legacy/compatibility metadata during implementation, not as current canonical lifecycle states.

## 2. Current Implementation Inventory

Backend artifact generation:

- `backend/app/services/resume_artifacts.py` generates tailored resume artifacts from workspace, Role-backed opportunity, required COMPASS evaluation, and active or selected resume source version.
- `backend/app/services/cover_letter_artifacts.py` generates cover-letter artifacts from workspace, Role-backed opportunity, optional COMPASS evaluation, optional resume source version, and tone.
- `backend/app/api/resume_artifacts.py` exposes `POST /api/roles/{role_id}/resume-artifacts` and `POST /api/opportunities/{opportunity_id}/resume-artifacts`.
- `backend/app/api/cover_letter_artifacts.py` exposes equivalent cover-letter generation routes.
- Both services persist to `GeneratedArtifact`, validate generated contract JSON against shared JSON Schema, run truthfulness checks, record AI usage events, append activity logs, and create artifact performance records.

Backend artifact export:

- `backend/app/services/artifact_exports.py` exports stored artifact `content` to Markdown, DOCX, or PDF.
- `backend/app/api/artifact_exports.py` exposes `POST /api/artifacts/{artifact_id}/exports/{export_format}`.
- Export records are appended to `metadata.contract.exportMetadata` and `metadata.export_history`.
- Export currently does not mark an artifact reviewed, submitted, or final.

Backend adjacent behavior:

- `backend/app/services/applications.py` includes latest resume and cover-letter summaries in application list/detail responses.
- Application timeline includes generated-artifact events from `GeneratedArtifact` rows.
- `backend/app/services/artifact_performance.py` records artifact-performance rows at generation time and updates observed workflow outcomes later.
- `backend/app/services/automation.py` can suggest artifact readiness review but explicitly does not mark artifacts reviewed, approved, exported, or submitted.
- `backend/app/services/advisor_packets.py` summarizes artifacts and redacts private/internal content by default.

Shared contracts:

- `packages/contracts/src/artifacts.ts` defines `ResumeArtifactSchema`, `CoverLetterArtifactSchema`, generation metadata, export metadata, revision metadata, upload metadata, parsing metadata, and format metadata.
- `packages/contracts/src/enums.ts` currently defines `ArtifactLifecycleStatusSchema` as `draft`, `reviewed`, `approved`, `exported`, `archived`. This conflicts with the approved Layer 6 four-state model and needs normalization.

Frontend:

- `frontend/src/pages/ApplicationDetailPage.tsx` displays latest artifact badges in the application overview.
- `frontend/src/components/ApplicationTimeline.tsx` renders artifact timeline events when returned by the backend.
- `frontend/src/components/AdvisorPacketPanel.tsx` shows artifact summaries and optional local preview selection.
- There is no dedicated artifact API client, artifact type file, artifact list component, artifact detail panel, or lifecycle-action UI.

Tests:

- `backend/tests/test_resume_artifacts.py` covers generation persistence, source/evaluation linkage, truthfulness checks, validation rollback, API aliases, and revision increment.
- `backend/tests/test_cover_letter_artifacts.py` covers analogous cover-letter generation paths and optional source/evaluation behavior.
- `backend/tests/test_artifact_exports.py` covers Markdown/DOCX/PDF export and export metadata recording.
- `backend/tests/test_application_workflows.py` covers latest artifact summaries and timeline generated-artifact events.
- `backend/tests/test_automation_guardrails.py` confirms readiness suggestions do not mark artifacts submitted.
- `backend/tests/test_artifact_performance.py` covers artifact performance summaries.
- Frontend application detail tests cover artifact/advisor packet summaries indirectly, not artifact lifecycle.

## 3. Current Data Model Summary

`GeneratedArtifact` is the central persisted artifact row:

- `id`
- `user_id`
- `workspace_id`
- `application_id`
- `role_id`
- `artifact_type`
- `title`
- `content`
- `metadata` mapped as `artifact_metadata`
- `created_at`
- `updated_at`
- `deleted_at`

Current relationships:

- User ownership is present through `user_id`.
- Workspace/search-track linkage is present through `workspace_id`.
- Opportunity linkage is present through `role_id`, where Role currently backs the product-facing Opportunity.
- Application linkage exists through nullable `application_id`, but generation services usually set only `role_id`; artifact performance derives application at generation time if present.
- COMPASS/evaluation linkage is stored inside `artifact_metadata.target_evaluation_id` and `artifact_metadata.contract.metadata.targetEvaluationId`, not as a first-class FK column.
- Resume/profile source linkage is stored in metadata under `source_resume` and contract generation metadata.

Current versioning:

- Contract `revision.revisionNumber` increments on regeneration for the same workspace, role, and artifact type.
- Contract `revision.parentArtifactId` points to the previous generated artifact.
- There is no separate artifact revision table.

Current lifecycle:

- Generated artifacts are effectively drafts.
- Some adjacent code checks `contract.lifecycleStatus`, but generation does not set it consistently and no state machine enforces transitions.
- `deleted_at` exists for soft-delete style hiding, but archive semantics are not implemented.
- `submitted_at` exists on `ArtifactPerformanceRecord`, not on `GeneratedArtifact`.

## 4. Current UI Summary

Application detail currently provides only compact artifact visibility:

- Overview badges show latest resume and cover-letter revision numbers.
- Timeline can show artifact-created events.
- Advisor packet preview shows artifact summaries, lifecycle warnings, and optional local-only content inclusion.

Missing UI:

- No artifact list by opportunity/application.
- No artifact list by workspace/search track.
- No artifact detail view or content review panel.
- No status controls for review, submit, archive.
- No distinction between latest draft and submitted/final version.
- No editing or new-version workflow for submitted artifacts.
- No frontend export/download workflow for selected artifact versions.

## 5. Current API and Service Summary

Existing artifact APIs are generation and export only:

- Generate resume artifact for role/opportunity.
- Generate cover letter artifact for role/opportunity.
- Export artifact by ID and format.

Missing lifecycle APIs/services:

- Create draft independent of AI generation.
- List artifacts by opportunity/application.
- List artifacts by workspace.
- Get artifact detail/history.
- Update draft content/title.
- Mark reviewed.
- Mark submitted.
- Archive artifact.
- Create new draft from submitted artifact.

The repository has a clear service/API pattern for this work in application workflow services: centralized service logic, explicit errors, thin FastAPI adapters, Pydantic schemas, current-user ownership checks, activity logs, and focused tests.

## 6. Current Test Coverage Summary

Strong coverage exists for generation, truthfulness, export rendering, application summary/timeline inclusion, and automation non-mutation boundaries.

Coverage gaps:

- Allowed lifecycle transitions.
- Disallowed lifecycle transitions.
- Submitted timestamp behavior.
- Archived artifact filtering.
- Draft update/edit behavior.
- Submitted artifact protected-edit behavior.
- Artifact detail/list API response shape.
- Opportunity/workspace/evaluation/source traceability after lifecycle operations.
- Frontend status display and lifecycle actions.
- Internal COMPASS/analysis leakage checks for lifecycle/export/detail surfaces.

## 7. Gaps Against Layer 6 Objective

Layer 6 objective gap list:

- Artifacts are not yet durable workflow-aware lifecycle records.
- Draft/reviewed/submitted/archived status is not canonical or enforced.
- Submitted versions are not protected from silent overwrite.
- Artifact state changes are not visible as application timeline events.
- Application detail cannot identify latest draft versus submitted artifact.
- Workspace/search-track artifact retrieval is not available.
- Evaluation/source traceability is metadata-only and not consistently elevated into API responses.
- User edits are not modeled.
- Archive state is not separate from soft delete.
- Current `approved/exported` vocabulary conflicts with the approved four-state model.

## 8. Privacy and Trust Risks

Privacy and trust risks:

- Employer-facing `GeneratedArtifact.content` is stored next to internal metadata, so API responses must avoid blindly returning metadata as exportable content.
- Export currently uses only `artifact.title` and `artifact.content`, which is correct, but lifecycle/export UI must preserve that boundary.
- Advisor packet content inclusion is local-only and explicit, but lifecycle status currently defaults to unknown/draft-like, which weakens user confidence.
- Application timeline descriptions should not include COMPASS rationale, ATS risk notes, compensation strategy, or private notes when referencing artifact events.
- Artifact detail UX must separate employer-facing content from internal metadata, source traceability, and review notes.

## 9. Internal-Content Leakage Risks

Current generation contracts store internal-ish support fields in metadata:

- `metadata.targetEvaluationId`
- `metadata.sourceResume`
- `metadata.workspace`
- `tailoringNotes`
- generation warnings and limitations
- source hashes and input hashes

These are useful for traceability but must not be merged into exportable artifact body fields.

Current `artifact_exports.py` exports only `title` and `content`. Keep that behavior. New lifecycle APIs and UI should expose traceability metadata as separate review/context fields and never append it to employer-facing resume or cover-letter content.

## 10. Versioning and Submitted-State Risks

Versioning risks:

- Revision numbers are currently contract-only. Queries order by `created_at`, which is good enough for generation but weak for history display if edited rows mutate in place.
- Parent lineage exists for regenerations but not for edited drafts created from submitted artifacts.
- There is no first-class submitted timestamp on `GeneratedArtifact`.
- `ArtifactPerformanceRecord.submitted_at` can mirror application applied date, which is not the same as user marking a specific artifact submitted.
- Existing `approved/exported` statuses may appear in older metadata or tests.

Recommended default:

- Add first-class lifecycle fields to `GeneratedArtifact` with additive migration.
- Keep revision metadata in the contract for compatibility, but expose normalized lifecycle fields from the row.
- On submitted artifact edit, create a new draft row with incremented revision and parent link instead of mutating submitted content.
- Treat archive as lifecycle status plus `archived_at`, not as `deleted_at`.

## 11. Recommended Implementation Sequence for 6B-6E

### 6B - Artifact Data Model and Lifecycle State Machine

Add the foundational lifecycle model:

- `ArtifactType` and `ArtifactLifecycleStatus` constants.
- Additive migration for `generated_artifacts.lifecycle_status`, `version_number`, `source_artifact_id`, `evaluation_id`, `source_resume_version_id`, `generation_metadata`, `reviewed_at`, `submitted_at`, and `archived_at` if repository conventions make them safe.
- Central lifecycle transition service.
- Contract enum update to `draft`, `reviewed`, `submitted`, `archived`.
- Backward-compatible serialization that can read legacy contract metadata.

Likely files:

- `backend/app/constants.py`
- `backend/app/models.py`
- `backend/alembic/versions/*`
- `backend/app/schemas/*artifacts*.py`
- `backend/app/services/*artifacts*.py`
- `packages/contracts/src/enums.ts`
- `packages/contracts/src/artifacts.ts`
- generated JSON schemas
- artifact generation tests
- migration tests
- Layer 3/6 artifact docs

### 6C - Versioning, Review, and Submitted-State Workflow

Add operational lifecycle APIs:

- Create/update draft.
- Mark reviewed.
- Mark submitted.
- Archive.
- List by opportunity/workspace.
- Get detail/history.
- Protected submitted edit creates a new draft version.
- Application timeline gets reviewed/submitted/archived artifact events from safe metadata.

Likely files:

- New or existing backend artifact lifecycle service/API/schema files
- `backend/app/main.py`
- `backend/app/services/applications.py`
- `backend/tests/test_artifact_lifecycle.py`
- `backend/tests/test_application_workflows.py`
- generation service tests
- export tests

### 6D - Artifact UX, Retrieval, and Opportunity Integration

Add user-facing artifact lifecycle experience:

- Frontend artifact API client and types.
- Artifact summary/detail panel.
- Application overview artifact section.
- Lifecycle status badges and action buttons.
- Empty states.
- Submitted/final distinction.
- Opportunity/application links to artifact detail.

Likely files:

- `frontend/src/api/artifacts.ts`
- `frontend/src/types/artifacts.ts`
- `frontend/src/components/ArtifactLifecyclePanel.tsx`
- `frontend/src/pages/ApplicationDetailPage.tsx`
- `frontend/src/pages/ApplicationDetailPage.test.tsx`
- possibly `frontend/src/pages/RoleDetailPage.tsx`
- app styles if needed

### 6E - Tests, Docs, and Regression Hardening

Harden:

- Backend lifecycle transition matrix and invalid transitions.
- Submitted protected edit behavior.
- Archived filtering.
- Application summary/timeline integration.
- Export boundary.
- Frontend lifecycle rendering and empty states.
- STRIDE terminology scan, preserving explicit historical references only.
- Update Layer 6 docs and strategy status if implementation is complete for local MVP scope.

Likely files:

- focused backend tests
- focused frontend tests
- contracts tests and generated schema
- `README.md`
- `backend/README.md`
- `docs/01_strategy/*`
- `docs/02_layers/06_layer-06-advanced-compass-and-artifact-lifecycle.md`
- `docs/03_domain-design/resume-artifact-generation.md`
- `docs/03_domain-design/cover-letter-artifact-generation.md`
- `docs/03_domain-design/application-workflow-persistence.md`

## 12. Open Questions Requiring Owner Input

Resolved during 6A handoff:

- The owner approved the canonical four-state lifecycle model: `draft`, `reviewed`, `submitted`, `archived`.

No remaining owner questions block 6B. Current assumptions:

- Additive schema changes are acceptable; destructive schema changes are not.
- Current Role-backed Opportunity persistence remains unchanged.
- Export/download should remain local and employer-facing-content-only.
- Submitted artifact mutation should be protected by creating a new draft/version rather than mutating submitted content.

## 13. Validation

Recon validation performed:

- Read current artifact generation, export, performance, automation, application workflow, advisor packet, model, schema, contract, UI, test, and documentation files.
- Confirmed `main` worktree was clean before edits.
- Confirmed current docs identify Layer 6 artifact lifecycle as next immediate implementation focus.
- Confirmed no active STRIDE terminology misuse requiring Layer 6A changes; historical/migration references should remain.

No runtime tests were required for this recon-only document. Follow-on implementation subsections must run focused backend, frontend, and contract checks.
