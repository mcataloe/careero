# Cover Letter Artifact Generation

Status: Active  
Doc Type: Domain Design  
Layer: Layer 3 / Layer 8  
Source of Truth: Yes  
Last Reviewed: 2026-05-28
Related Docs:
- docs/03_domain-design/resume-artifact-generation.md
- docs/04_ai-and-compass/compass-evaluation-model.md
Cover letter artifact generation creates a validated canonical
`CoverLetterArtifact` draft for one workspace and target opportunity. It can use
a COMPASS evaluation and resume/profile source when they are available, but both
are optional for this layer.

## Boundary

The backend generation flow is:

```text
Workspace ID + Role/Opportunity + optional COMPASS Evaluation + optional Resume Source Version
-> Cover Letter Prompt Builder
-> AI Model Call
-> Raw Structured Cover Letter Output
-> Tone and Truthfulness Checks
-> CoverLetterArtifact JSON Schema Validation
-> GeneratedArtifact persistence
```

Current `Role` rows act as target Opportunities until canonical Opportunity
persistence exists. Workspace persistence exists locally; callers provide
`workspace_id`, and the backend verifies that the workspace exists, is active or
paused, and owns the target role before storing the value in the canonical
artifact contract.

Frontend rendering remains a separate layer. Generated cover letters store draft
content only. Local Markdown, DOCX, and PDF exports are created from the stored
validated artifact and recorded in `exportMetadata`. Cloud export and external
account sync remain future work.

## Tone Default

The product default is a neutral, forward-looking professional tone for cold
applications. It maps to the canonical `direct` tone enum. Generated content
must avoid overly enthusiastic openings such as "I'm excited to apply" or "I am
thrilled". A preferred default opening is direct and professional, such as "I'm
writing to be considered for...".

Other canonical tones can be requested, but they still must remain grounded and
professional.

## Truthfulness Rule

Cover letter generation is grounded only in the supplied role/opportunity,
optional COMPASS evaluation, optional resume/profile source, and explicit user
inputs. The generator must not invent employers, roles, dates, technologies,
credentials, metrics, accomplishments, or experience.

If no resume/profile source is available, the letter should avoid
candidate-specific experience claims and stay focused on professional interest
in the opportunity. If a COMPASS evaluation or source is missing, generation
metadata records a warning. Unsupported claims reported by the model are
rejected before persistence.

When a resume/profile source and COMPASS evaluation are available, generation
also rejects content that includes a COMPASS missing keyword not present in the
source text.

## Artifact Lifecycle

The service persists generated cover letters through the existing
`generated_artifacts` table:

- `generated_artifacts.id` is the canonical `CoverLetterArtifact.id`.
- `generated_artifacts.role_id` links the artifact to the target Role.
- `generated_artifacts.artifact_type` is `cover_letter`.
- `generated_artifacts.lifecycle_status` starts as `draft`.
- `generated_artifacts.version_number` mirrors the canonical revision number.
- `generated_artifacts.evaluation_id` links to the target COMPASS evaluation when present.
- `generated_artifacts.source_resume_version_id` links to the grounding resume/profile version when present.
- `generated_artifacts.source_artifact_id` links to the prior artifact version when one exists.
- `metadata.contract` stores the complete validated `CoverLetterArtifact`.
- `metadata.source_resume` stores source id, source version id, source label,
  source type, and source hash when a source is available.
- `metadata.target_evaluation_id` stores the COMPASS evaluation id or `null`.
- `metadata.tone` stores the requested canonical tone.

Lineage is revision-based. The first generated cover letter for a workspace and
role has `revisionNumber = 1` and no parent. Later generations for the same
workspace and role increment the revision and point `parentArtifactId` to the
previous cover letter artifact.

Generation is draft-only. User review, submitted, and archive states are
Layer 6 lifecycle workflow states and should not be inferred from generation
alone. Export metadata records file generation and does not by itself make an
artifact submitted.

