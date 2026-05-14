# Canonical Domain Model

Careero's canonical contracts define the long-term platform objects used across frontend rendering, backend persistence, AI orchestration, workflow tracking, and future export generation.

The contracts live in `packages/contracts` and are executable TypeScript/Zod schemas. Generated JSON Schema files are available for backend and AI structured-output validation.

Current contract version:

```text
careero.contracts.v1
```

## Design Principles

- Contracts are platform contracts, not frontend-only or backend-only shapes.
- Raw AI outputs, validated normalized outputs, persisted outputs, and rendered outputs remain separate.
- AI prompts must target versioned contracts and validate their output before persistence.
- Persistence can evolve toward the contracts incrementally; this phase does not require database migrations.
- Explainability and auditability are required for evaluations, generated artifacts, and workflow transitions.
- Workspaces isolate career objective context, preferences, memory summaries, artifacts, and workflow history.

## Package Layout

```text
packages/contracts/
  src/
    workspace.ts
    opportunity.ts
    stride-evaluation.ts
    artifacts.ts
    application-state.ts
    primitives.ts
    enums.ts
    examples.ts
  generated/json-schema/
```

## Consumption Boundary

TypeScript consumers should import schemas, inferred types, and validation helpers from `@careero/contracts`. Python/backend consumers should use the generated JSON Schema files in `packages/contracts/generated/json-schema/`; the backend should not import TypeScript directly.

## Entity Responsibilities

### Workspace

`Workspace` is the highest-level organizational container beneath a user. It represents one coherent career/search objective, such as a full-time leadership search, contract consulting search, exploration workspace, or relocation-focused search.

Responsibilities:

- Own workspace preferences and metadata.
- Isolate contextual AI memory through `aiContextSummary`.
- Contain opportunities, applications, artifacts, and evaluation history.
- Support lifecycle states: `active`, `paused`, `archived`, `completed`.
- Preserve tags and timestamps for future analytics.

Persistence guidance:

- Future persistence should add a workspace table beneath `users`.
- Current single-user ownership can map existing records into a default workspace during migration.
- Do not overload user-level fields with workspace-specific preferences.

Frontend guidance:

- Workspace navigation should select career context before listing opportunities and artifacts.
- Paused, archived, and completed workspaces should remain inspectable.

AI guidance:

- Workspace context is input context, not a source of invented facts.
- AI memory summaries must be traceable, updateable, and scoped to one workspace.

### Opportunity

`Opportunity` is the canonical successor to the current `Role` concept. It represents a specific role, contract, consulting engagement, or professional opportunity.

Responsibilities:

- Preserve raw ingestion content and normalized structured content.
- Track source/provenance, parse confidence, warnings, and AI notes.
- Link to STRIDE evaluations, application state, and artifacts.
- Support opportunity status tracking without coupling it to application workflow state.

Ingestion guidance:

- Store raw pasted/imported content separately from normalized fields.
- Record source type, URL when explicitly supplied, parser version, warnings, and content hash.
- Do not fabricate compensation, dates, company websites, or remote type during parsing.

Normalization guidance:

- Keep title, company, location, compensation, employment type, and remote type as structured fields.
- Preserve description and extracted lists as normalized content for rendering and evaluation.

AI parsing guidance:

- AI parsing should return validated contract-compatible data.
- Invalid or low-confidence extraction should be surfaced as warnings, not silently persisted as fact.

### STRIDE Evaluation

`StrideEvaluation` is the intelligence core. It must be reproducible, explainable, structured, and versionable.

Responsibilities:

- Link to workspace and opportunity.
- Store evaluation version, model metadata, prompt/ruleset versions, and input hashes.
- Separate strengths, gaps, risks, ATS findings, compensation findings, recommendation, and confidence.
- Preserve assumptions and reproducibility metadata.

AI contract guidance:

- Prompt outputs should validate against the JSON Schema generated from the canonical contract or a compatible narrowed output schema.
- AI output cannot invent resume facts, company facts, compensation, or external research.
- AI enrichment should clearly distinguish evidence, assumptions, gaps, and insufficient data.

Rendering guidance:

- Render structured sections directly from validated fields.
- Do not parse raw AI prose in the frontend to infer business logic.

Persistence guidance:

- Store deterministic baseline metadata and AI enrichment metadata separately when possible.
- Keep evaluation records append-only by default; use supersession/version metadata for re-runs.

Versioning strategy:

- `version.version`, `modelMetadata.promptVersion`, and `modelMetadata.rulesetVersion` are required.
- Changes to scoring or prompt behavior should update version fields.

### Resume Artifact

`ResumeArtifact` represents an uploaded, imported, generated, or tailored resume version associated with a workspace and optionally an opportunity.

Responsibilities:

- Preserve source linkage, target opportunity linkage, artifact type, and lifecycle status.
- Track generation, upload, parsing, export, tailoring, and revision metadata.
- Support future diff/comparison and lineage.

Storage recommendations:

- Store artifact content separately from export files.
- Store file exports as generated representations with format, hash, and timestamp metadata.
- Uploaded source resumes and generated tailored resumes should share artifact lineage rather than separate unrelated models.

Artifact lifecycle:

- `draft`: generated or uploaded but not finalized.
- `reviewed`: user has reviewed.
- `approved`: ready to export or apply.
- `exported`: exported to at least one format.
- `archived`: retained but inactive.

### Cover Letter Artifact

`CoverLetterArtifact` represents a contextual communication artifact tied to a workspace and opportunity.

Responsibilities:

- Store tone metadata, generation metadata, edit history, export metadata, and revision lineage.
- Keep prompt inputs and AI output validation separate from rendered/exported text.

AI prompt contract guidance:

- Prompt inputs should include opportunity, workspace context, selected resume/profile source, and explicit tone instructions.
- AI must not invent personal experience or company facts.
- Generated content should remain a draft until reviewed by the user.

Rendering/export guidance:

- Frontend rendering should use the validated content and metadata.
- Export generation should be deterministic from stored artifact content and selected format.

### Application State

`ApplicationState` is a workflow system, not just a flat enum.

Minimum states:

- `discovered`
- `interested`
- `applied`
- `interviewing`
- `offer`
- `rejected`
- `withdrawn`
- `archived`

Responsibilities:

- Track current state and full state history.
- Store reminders, notes, interview stages, external links, and application metadata.
- Support future automation without losing auditability.

State transition guidance:

- Every state change should append a history entry with timestamp, actor, reason, and metadata.
- Automation may suggest transitions, but user-visible state changes should remain auditable.
- Interview details should live in structured `interviewStages`, not freeform notes only.

Timeline guidance:

- State history, notes, reminders, and interview stages can render as a unified timeline.
- Timeline rendering must not become the persistence model; use typed structures as the source.

## AI Orchestration Boundaries

Keep these layers separate:

- Ingestion: accepts raw role/profile/application inputs.
- Parsing: converts raw input into validated normalized output.
- Evaluation: scores and explains opportunity fit.
- Artifact generation: creates resume or cover letter drafts from validated inputs.
- Rendering: displays validated platform objects.
- Persistence: stores durable records, lineage, metadata, and audit history.
- Export: converts reviewed artifacts into files.

AI services should consume validated inputs and return structured outputs. Raw provider responses should be retained for debugging only when safe and should never be the frontend rendering contract.

## Migration And Compatibility

Current models remain operational. Future migration guidance:

- Current `Role` maps toward `Opportunity`.
- Current `StrideEvaluation` maps toward canonical `StrideEvaluation`.
- Current `Application` maps toward `ApplicationState`.
- Current `GeneratedArtifact` maps toward `ResumeArtifact` and `CoverLetterArtifact`.
- Current `ResumeSource` and resume source versions map toward source inputs and lineage for `ResumeArtifact`.
- Current single-user `user_id` ownership remains valid until workspace persistence is implemented.
- A future default workspace can backfill existing local records without introducing tenants or workspaces prematurely.

## Contract Versioning Philosophy

- Additive compatible fields may stay in `careero.contracts.v1`.
- Breaking field changes, semantic changes, or enum removals require a new contract version.
- AI prompt versions and ruleset versions are separate from contract versions.
- Persisted records should carry enough version metadata to reproduce or interpret old outputs.

## Testing Strategy

Recommended tests:

- Schema validation for examples and edge cases.
- Invalid enum/status rejection.
- Serialization and deserialization round trips.
- Generated JSON Schema presence and registry consistency.
- Backend migration compatibility tests when persistence adopts these contracts.
- AI output validation against narrowed schemas derived from canonical objects.
- Frontend rendering tests that consume canonical fixture shapes.
- Version compatibility tests before changing contract semantics.

## Backlog Notes

- Add workspace persistence after current single-user local workflows remain stable.
- Add profile fact extraction only after resume/profile source storage and grounding behavior are stable.
- Add artifact generation only after evaluation outputs are reliable and auditable.
