# @careero/contracts

Executable canonical platform contracts for Careero.

This package is additive and future-facing. Current backend and frontend runtime models continue to work as they do today. These contracts define the shared source of truth that future backend persistence, frontend rendering, AI orchestration, export generation, and workflow tracking should migrate toward.

## Contents

- Zod schemas for canonical entities.
- TypeScript types inferred from those schemas.
- Validation helpers for generic and entity-specific parsing.
- Provider-neutral STRIDE evaluation engine helpers.
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

TypeScript consumers import from `@careero/contracts`. Python/backend consumers should use the generated JSON Schema files; the backend should not import TypeScript directly.

## STRIDE Engine

Layer 3B adds a reusable provider-neutral STRIDE engine:

```ts
import {
  buildStrideEvaluationPrompt,
  evaluateStrideOpportunity,
} from "@careero/contracts";
```

The engine accepts canonical `Workspace` and `Opportunity` objects plus optional resume/profile content. It calls an injected model provider, parses raw JSON, validates the result with `StrideEvaluationSchema`, and returns both the raw model output and the normalized validated evaluation. Invalid JSON, schema failures, and provider errors return a valid failed fallback evaluation instead of a completed evaluation.

Model configuration belongs to the caller or provider adapter. This package does not depend on the OpenAI SDK.

## Contract Version

Current contract version:

```text
careero.contracts.v1
```

Breaking schema changes should introduce a new version rather than silently changing existing contract semantics.
