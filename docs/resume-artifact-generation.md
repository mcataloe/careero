# Resume Artifact Generation

Resume artifact generation creates a validated canonical `ResumeArtifact` draft for
one workspace, target opportunity, STRIDE evaluation, and resume/profile source.
It does not render the resume in the frontend and does not export files.

## Boundary

The backend generation flow is:

```text
Workspace ID + Role/Opportunity + STRIDE Evaluation + Resume Source Version
-> Resume Prompt Builder
-> AI Model Call
-> Raw Structured Resume Output
-> Truthfulness Checks
-> ResumeArtifact JSON Schema Validation
-> GeneratedArtifact persistence
```

Current `Role` rows act as target Opportunities until canonical Opportunity
persistence exists. Workspace persistence is not implemented yet, so callers
provide `workspace_id`; the value is stored in the canonical artifact contract.

Rendering and export are separate layers. Generated artifacts store markdown
content with `formatMetadata.primaryFormat = "md"` and
`availableFormats = ["md"]`. PDF, DOCX, HTML, and other exports should be
created later from the stored validated artifact and recorded in
`exportMetadata`.

## Truthfulness Rule

Resume generation is grounded only in the supplied resume/profile source, target
role, and STRIDE evaluation. The generator must not invent employers, roles,
dates, technologies, credentials, metrics, accomplishments, or experience.

If source material is insufficient, the generated resume should weaken or omit
the unsupported claim and record the limitation in generation warnings. The
normalization layer rejects output that reports unsupported claims, and it
rejects generated content that includes a STRIDE missing keyword when that
keyword is not present in the source resume/profile text.

## Artifact Lifecycle

The service persists generated resumes through the existing
`generated_artifacts` table:

- `generated_artifacts.id` is the canonical `ResumeArtifact.id`.
- `generated_artifacts.role_id` links the artifact to the target Role.
- `metadata.contract` stores the complete validated `ResumeArtifact`.
- `metadata.source_resume` stores source id, source version id, source label,
  source type, and source hash.
- `metadata.target_evaluation_id` stores the STRIDE evaluation id.

Lineage is revision-based. The first generated resume for a workspace and role
has `revisionNumber = 1` and no parent. Later generations for the same workspace
and role increment the revision and point `parentArtifactId` to the previous
artifact. `sourceArtifactId` remains `null` until source resumes are persisted as
canonical artifact rows.

Generation is draft-only. User review, approval, export, and archive states are
future workflow layers and should not be inferred from generation alone.
