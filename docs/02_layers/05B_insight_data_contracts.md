# Layer 5B Insight Data Contracts

Status: Complete  
Doc Type: Implementation Summary  
Layer: Layer 5  
Source of Truth: No  
Last Reviewed: 2026-05-28  
Related Docs:
- 05_layer-05-workflow-intelligence-and-insights.md
- ../08_reports-and-audits/layer-recon-summaries/layer-5-insight-recon.md
- ../03_domain-design/workspace-intelligence.md

## Summary

Layer 5B adds a normalized insight contract across shared contracts, backend
schemas, service return shapes, and frontend TypeScript types. The change is
additive and keeps current API routes and collection names intact.

Careero still computes most Layer 5 insights on demand. No durable generic
`Insight` table, migration, route rename, or broad UI redesign was added.

## Contract Shape

Canonical insight fields now include:

- `id`
- `category`
- `label`
- `message`
- `basis`
- `confidence`
- `confidence_level`
- `confidence_explanation`
- `known_uncertainty`
- `warnings`
- `severity`
- `priority`
- `generation_method`
- `visibility`
- `scope`
- `source_references`
- `source_inputs`
- `freshness`
- `recommended_action`
- optional `created_at` and `updated_at`

The backend API shape intentionally uses snake_case to match current FastAPI
responses. The shared TypeScript/Zod contract uses camelCase canonical field
names for package-level schema generation.

## Compatibility Decisions

- Existing response fields such as `confidence`, `basis`, `source_inputs`,
  `title`, `reason`, `signal_type`, `gentle_guidance`, and `value` remain in
  place for existing consumers.
- `confidence` remains the display label. `confidence_level` is the normalized
  machine-readable value.
- Existing routes remain unchanged.
- Workspace/user ownership remains enforced by current service queries rather
  than by exposing user IDs in insight payloads.

## Visibility Boundary

Layer 5 insights default to `visibility="internal"`. These records are for the
job seeker and should not be treated as employer-facing artifact content.

Future advisor/collaboration work can selectively introduce additional
visibility behavior, but this layer does not export internal COMPASS rationale,
compensation strategy, ATS risk notes, or private search strategy to employers.

## Known Limitations

- Most Layer 5 insights are still computed on demand rather than persisted as
  durable snapshots.
- Source references are supported by the contract but not yet exhaustively
  populated across every service.
- Dashboard UI still needs the Layer 5C metadata rendering pass.
- Layer 5D should add broader endpoint response-shape coverage, including
  database-backed analytics tests when `CAREERO_TEST_DATABASE_URL` is available.
