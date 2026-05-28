# Layer 6 - Advanced COMPASS and Artifact Lifecycle

Status: Draft  
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

Artifacts are user-owned and may be linked to a workspace/search track, Role-backed
opportunity, application workflow, COMPASS evaluation, source resume version, and
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

Employer-facing artifact content is always the stored `title` and `content`.
Internal analysis, source/evaluation traceability, generation metadata, export
metadata, and user notes stay in separate fields and must not be appended to
resume or cover-letter body content.
