# Resume Artifact Generation

Status: Active  
Doc Type: Domain Design  
Layer: Layer 3 / Layer 8  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/03_domain-design/cover-letter-artifact-generation.md
- docs/04_ai-and-compass/compass-evaluation-model.md
Resume artifact generation creates a validated canonical `ResumeArtifact` draft for
one workspace, target opportunity, COMPASS evaluation, and resume/profile source.
It does not render the resume in the frontend. Local Markdown, DOCX, and PDF
exports are handled by the Layer 8 artifact export API after the artifact is
persisted.

## Boundary

The backend generation flow is:

```text
Workspace ID + Role/Opportunity + COMPASS Evaluation + Resume Source Version
-> Resume Prompt Builder
-> AI Model Call
-> Raw Structured Resume Output
-> Truthfulness Checks
-> ResumeArtifact JSON Schema Validation
-> GeneratedArtifact persistence
```

Current `Role` rows act as target Opportunities until canonical Opportunity
persistence exists. Workspace persistence exists locally; callers provide
`workspace_id`, and the backend verifies that the workspace exists, is active or
paused, and owns the target role before storing the value in the canonical
artifact contract.

Frontend rendering remains a separate layer. Generated artifacts store markdown
content with `formatMetadata.primaryFormat = "md"`. Local Markdown, DOCX, and
PDF exports are created from the stored validated artifact and recorded in
`exportMetadata`. Cloud export and external account sync remain future work.

## Truthfulness Rule

Resume generation is grounded only in the supplied resume/profile source, target
role, and COMPASS evaluation. The generator must not invent employers, roles,
dates, technologies, credentials, metrics, accomplishments, or experience.

If source material is insufficient, the generated resume should weaken or omit
the unsupported claim and record the limitation in generation warnings. The
normalization layer rejects output that reports unsupported claims, and it
rejects generated content that includes a COMPASS missing keyword when that
keyword is not present in the source resume/profile text.

## Artifact Lifecycle

The service persists generated resumes through the existing
`generated_artifacts` table:

- `generated_artifacts.id` is the canonical `ResumeArtifact.id`.
- `generated_artifacts.role_id` links the artifact to the target Role.
- `metadata.contract` stores the complete validated `ResumeArtifact`.
- `metadata.source_resume` stores source id, source version id, source label,
  source type, and source hash.
- `metadata.target_evaluation_id` stores the COMPASS evaluation id.

Lineage is revision-based. The first generated resume for a workspace and role
has `revisionNumber = 1` and no parent. Later generations for the same workspace
and role increment the revision and point `parentArtifactId` to the previous
artifact. `sourceArtifactId` remains `null` until source resumes are persisted as
canonical artifact rows.

Generation is draft-only. User review, approval, export, and archive states are
future workflow layers and should not be inferred from generation alone.

