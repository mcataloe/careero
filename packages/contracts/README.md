# @careero/contracts

Executable canonical platform contracts for Careero.

This package is additive and future-facing. Current backend and frontend runtime models continue to work as they do today. These contracts define the shared source of truth that future backend persistence, frontend rendering, AI orchestration, export generation, and workflow tracking should migrate toward.

## Contents

- Zod schemas for canonical entities.
- TypeScript types inferred from those schemas.
- Example fixtures for each entity.
- Generated JSON Schema files for Python/backend validation and AI structured outputs.

Canonical entities:

- `Workspace`
- `Opportunity`
- `StrideEvaluation`
- `ResumeArtifact`
- `CoverLetterArtifact`
- `ApplicationState`

## Commands

```powershell
npm install
npm run build
npm run test
npm run generate:json-schema
```

Generated JSON Schema files are written to `generated/json-schema/`.

## Contract Version

Current contract version:

```text
careero.contracts.v1
```

Breaking schema changes should introduce a new version rather than silently changing existing contract semantics.
