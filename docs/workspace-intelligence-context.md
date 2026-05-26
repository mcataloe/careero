# Workspace Intelligence Context

Workspace context lets one local user run multiple independent career searches,
such as a Staff Engineer search, a consulting search, and an exploratory
leadership search. Each workspace owns its own preferences, notes, tags, and AI
context summary.

## Workspace State

Workspaces are persisted in the backend and linked to roles, COMPASS evaluations,
resume artifacts, and cover letter artifacts.

Active-by-default workspaces have:

- `status` of `active` or `paused`
- `archived_at = null`

Archived and completed workspaces remain inspectable with
`include_inactive=true`, but they are not valid targets for new roles,
evaluations, or generated artifacts. Reactivating a workspace sets
`status="active"` and clears `archived_at`.

The local seed creates a default active workspace. Existing records are
backfilled to that workspace during migration unless a generated artifact already
stores a valid canonical `workspaceId`.

## Context Inputs

Workspace preferences use the canonical fields:

- target titles
- target seniority
- preferred remote types
- preferred locations
- target compensation
- target keywords
- avoid keywords
- notes

Additional backend-only preferences that are not yet part of the canonical
Workspace contract can live under `metadata.contextPreferences`, such as
preferred industries, preferred technologies, employment type preference, and
tone/style preferences.

`ai_context_summary` is passed to AI workflows as scoped context. It is not
generated or updated automatically in this layer.

## AI Workflow Consumption

COMPASS evaluation loads the role's workspace and merges workspace preferences
into the evaluation context. Explicit request `user_context` values override
workspace defaults for that one run. The workspace context is stored in
`raw_evaluation_json`, included in the AI prompt, and included in the evaluation
input hash so cache results cannot bleed across workspaces.

Resume artifact generation validates that the supplied `workspace_id` exists,
is active, and owns the target role. It includes workspace context in the prompt,
input hash, canonical artifact metadata, and persisted generated artifact row.

Cover letter artifact generation follows the same workspace validation and
prompt scoping. Missing COMPASS evaluation or resume source can still be allowed,
but workspace ownership is required.

Workspace context is input context only. It must not be treated as proof of
candidate experience, and it must not be copied between workspaces.

## Strategy Synthesis Consumption

Layer 10 uses workspaces/search tracks as the strategy scope. The strategy
service reads workspace preferences, saved opportunities, applications, COMPASS
evaluations, source intelligence, compensation intelligence, search health,
recommendations, historical learning, and artifact performance to produce a
read-only summary.

This synthesis is derived and transient. It does not mutate workspace
preferences, create automation suggestions, save retrospectives, or copy
workspace context into employer-facing artifacts. Cross-workspace comparison is
an internal comparison across stored local tracks only.

## Non-Goals

This layer does not add embeddings, vector search, external market intelligence,
or long-term memory automation. Resume sources remain user-level for now;
workspace-specific source selection can be added in a future layer.
