# Layer 6 - Advanced COMPASS and Artifact Lifecycle

Status: Complete for Current Local MVP Scope
Doc Type: Layer Spec  
Layer: Layer 6  
Source of Truth: Yes  
Last Reviewed: 2026-05-28
Related Docs:
- docs/04_ai-and-compass/compass-evaluation-model.md
- docs/03_domain-design/resume-artifact-generation.md

Layer 6 extends COMPASS and artifacts into lifecycle, evidence mapping, history, review, export, and submitted-artifact tracking.

The canonical local artifact lifecycle states are:

- `draft`: generated or user-edited material that is not yet reviewed.
- `reviewed`: user has reviewed the employer-facing content.
- `submitted`: user marked this exact artifact version as the one used for an application or equivalent submission.
- `archived`: retained for history but inactive by default.

Legacy `approved` and `exported` lifecycle metadata should be normalized as compatibility metadata, not treated as current lifecycle states. Export history remains separate from lifecycle status.

Artifacts are user-owned and may be linked to a workspace/search track,
Opportunity-backed persistence record, application workflow, COMPASS evaluation,
source resume version, and
source artifact. The persisted artifact row owns lifecycle status, version number,
parent/source artifact linkage, and reviewed/submitted/archived timestamps. The
canonical artifact contract in metadata mirrors those fields for compatibility.

Layer 6C adds the operational lifecycle API:

- `POST /api/artifacts`: create a manual draft artifact.
- `GET /api/artifacts`: list artifacts, optionally filtered by `workspace_id`,
  `opportunity_id`, or `application_id`.
- `GET /api/workspaces/{workspace_id}/artifacts`: list workspace artifacts.
- `GET /api/opportunities/{opportunity_id}/artifacts`: list opportunity artifacts.
- `GET /api/applications/{application_id}/artifacts`: list application artifacts.
- `GET /api/artifacts/{artifact_id}`: retrieve employer-facing content plus
  separated lifecycle and traceability metadata.
- `PATCH /api/artifacts/{artifact_id}`: edit a draft artifact.
- `POST /api/artifacts/{artifact_id}/review`: move draft to reviewed.
- `POST /api/artifacts/{artifact_id}/submit`: move reviewed to submitted.
- `POST /api/artifacts/{artifact_id}/archive`: archive draft, reviewed, or
  submitted artifacts.

Direct edits are allowed only for drafts. Editing a submitted artifact creates a
new draft revision with `source_artifact_id` pointing at the submitted record; the
submitted artifact remains historically traceable and is not silently overwritten.
Reviewed artifacts must be copied into a draft before further content changes.
Archived artifacts are excluded from active artifact lists and application
summaries by default.

Application timelines include artifact created, reviewed, submitted, and archived
events. Timeline metadata identifies artifact type, lifecycle status, and version
only; it must not include generated document body text, COMPASS rationale, ATS
risk notes, compensation strategy, or private decision rationale.

Layer 6D adds the user-facing artifact workflow in application detail:

- `/applications/{application_id}/artifacts` lists active resume and cover-letter
  artifacts separately and can opt into archived artifacts.
- Opportunity detail links tracked opportunities into the application artifact
  workspace and shows current resume/cover-letter lifecycle badges when present.
- Artifact detail shows status, version, submitted/final state, timestamps,
  source/evaluation traceability ids, export formats, and employer-facing
  content.
- Draft artifacts can be edited from the detail panel. Submitted artifacts show
  final-version language and expose a new-draft action instead of mutating the
  submitted record.
- Lifecycle actions use dismissible feedback for reviewed, submitted, archived,
  and new-version outcomes.

Employer-facing artifact content is always the stored `title` and `content`.
Internal analysis, source/evaluation traceability, generation metadata, export
metadata, and user notes stay in separate fields and must not be appended to
resume or cover-letter body content.

## Hardening Notes

Layer 6E validates the current local lifecycle scope:

- Draft creation is supported by generation services and the lifecycle API.
- Draft edits increment artifact version metadata.
- Submitted artifacts are protected by creating a new draft revision on edit.
- Active list/detail surfaces exclude archived artifacts by default and expose an
  opt-in archived view in the application artifact panel.
- Opportunity and application contexts can retrieve current resume and
  cover-letter artifacts without exposing internal COMPASS rationale.
- Export remains backend-local and uses only artifact `title` and `content`.

Known limitations:

- There is no standalone workspace-wide artifact browser yet; workspace-scoped
  retrieval exists in the API and application UX shows the owning search track.
- Frontend export/download controls are still Layer 8 work. Backend export
  endpoints remain available for exact artifact versions.
- Artifact comparison and richer evidence-map UX remain future Layer 6 expansion.
- Hosted multi-user permission enforcement still depends on later Layer 11 auth
  and authorization hardening.
- Local DB-backed regression tests require `CAREERO_TEST_DATABASE_URL`; without
  that environment variable, only pure backend lifecycle tests and frontend tests
  can run locally.
