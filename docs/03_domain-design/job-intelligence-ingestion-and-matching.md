# Job Intelligence Ingestion and Candidate Matching Pipeline

Status: Active  
Doc Type: Domain Design  
Layer: Layers 2, 7, 10, 14, 15  
Source of Truth: Yes  
Last Reviewed: 2026-09-28  
Related Docs:
- docs/02_layers/15_layer-15-api-job-sources-and-managed-deltas.md
- docs/03_domain-design/opportunity-model.md
- docs/03_domain-design/candidate-opportunity-matching.md
- docs/04_ai-and-compass/ai-governance.md
- docs/01_strategy/07_revised-build-order-execution-plan.md

## Purpose

This document captures the source-truth clarification and recommended decisions from the LEAP Recon for the Careero Job Intelligence Ingestion and Candidate Matching Pipeline.

The initiative is intended to ingest permitted external job postings, preserve source truth, normalize and deduplicate postings, decompose job descriptions into duties/requirements/nice-to-haves, resolve capabilities, compare postings against candidate evidence, and produce explainable fit signals.

The initiative should serve the current user's job search first while preserving a multi-user architecture from the start.

## Current Architecture Posture

Careero remains local-first and may have only one active user in the current deployment, but new ingestion, search-profile, candidate-evidence, taxonomy, matching, and source-record design must be multi-user-safe by design.

Required ownership posture:

- User-owned data must remain explicitly scoped by `user_id` and, where relevant, `workspace_id` or a later account/tenant boundary.
- Candidate evidence, search preferences, applications, match results, user decisions, ignored import candidates, saved Opportunities, and user overrides are private/user-scoped.
- Provider definitions, provider capability metadata, canonical capability definitions, canonical aliases, and approved non-private taxonomy records may be shared system-level records when appropriate.
- Provider connections, source subscriptions, query plans, ingestion runs, source observations, import candidates, and match results must not assume a global single-user corpus.
- Do not design this initiative as "Matt's global job database" with tenancy bolted on later.

## Material Decisions

The following decisions are approved as working assumptions for the next LEAP Prompt/LHS unless later changed by the user.

### 1. Initial Provider Scope

Start with official/public board-scoped ATS-style sources before broad aggregator sources.

Preferred first class:

- Greenhouse public job board API.
- Lever public postings/feed where permitted.
- Ashby public job posting API where permitted.

Broad search providers such as Adzuna, Coresignal, Lightcast, TheirStack, and similar providers remain separate source-governance candidates because pricing, search semantics, storage rights, retention rights, attribution obligations, and commercial-use terms differ materially from public board-scoped ATS feeds.

Technical endpoint availability is not enough to approve a source. Every provider must have a source-governance record before implementation or active use.

### 2. Automation Boundary

The first implementation must stop at manual/user-triggered ingestion.

Daily unattended/background execution is explicitly deferred behind a later human checkpoint after:

- source governance exists;
- one manual provider path is proven;
- source snapshots and deduplication are stable;
- errors and rate limits are visible;
- data retention/source-term behavior is documented;
- a worker/scheduler architecture is separately approved.

The presence of a `workers/` directory does not authorize a background job engine.

### 3. Capability Taxonomy Authority

Unknown capabilities must enter a proposed/review state before becoming canonical.

Parsers, semantic models, or LLM adjudicators must not automatically create canonical capabilities from a single job posting or candidate artifact.

The intended flow is:

```text
unknown phrase
  -> existing alias check
  -> semantic/relationship candidate match
  -> unresolved concept
  -> proposed capability candidate
  -> review/promote/merge/reject
```

Proposed capabilities should preserve source examples, nearest existing concepts, proposed type/category, confidence, frequency, parser/model/ruleset version, and review status.

## Provider Query Model

Careero must not assume every provider supports the same query shape.

Broad search providers may support title/location/work-mode style searches. ATS public job-board APIs are usually company/job-board scoped.

The correct abstraction is:

```text
SearchProfile
  -> SearchIntent
  -> ProviderCapability
  -> ProviderQueryPlan
  -> IngestionRun
  -> IngestionRunExecution(s)
```

`SearchProfile` expresses the user's search strategy. `SearchIntent` expresses what Careero wants to find. `ProviderCapability` describes what a source can actually do. `ProviderQueryPlan` is the provider-specific execution plan derived from the intent and capability matrix.

This preserves a common product model without forcing incompatible providers into one fake HTTP contract.

## Ingestion Run Shape

The initiative should record run-level and execution-level timestamps and results.

Conceptual records:

- `IngestionRun`: user/workspace/search-profile scoped run with `started_at`, `completed_at`, trigger type, status, and summary counts.
- `IngestionRunExecution`: one run's provider/endpoint/query-plan execution with its own timing, status, request window/scope, counts, errors, rate-limit observations, and provider metadata.
- `JobSourceProvider`: system-level provider definition and governance metadata.
- `JobSourceConnection` or equivalent: user/account/workspace scoped source configuration, if needed.
- `JobPostingSourceRecord`: provider/source identity record.
- `JobPostingSnapshot`: append-only source snapshot.
- `JobPostingImportCandidate`: review-before-save candidate.

Names remain candidates until implementation, but the separation of responsibilities is source truth for planning.

## Source Truth vs User-Owned Opportunity

Imported job records are source truth. Opportunities are user-owned workflow records.

Adapters must not write directly to Opportunity records.

The first implementation must preserve this flow:

```text
provider response
  -> source record / raw-or-policy-safe payload reference
  -> immutable normalized snapshot
  -> dedupe / identity candidate
  -> import candidate
  -> user review
  -> save/link/ignore/archive decision
```

User edits must not be silently overwritten by later provider refreshes.

## Matching and Storage Posture

PostgreSQL remains the canonical persistence layer for the next implementation stage.

Relational tables should represent:

- canonical facts;
- source records and snapshots;
- graph-shaped capability/evidence/requirement relationships;
- proposed taxonomy candidates;
- match results and evidence.

Do not add Neo4j, Neptune, a dedicated vector database, Kafka, a background scheduler, or other major infrastructure unless a later Recon proves the need and the user approves it.

pgvector or a PostgreSQL-compatible vector extension may be considered later after deterministic/canonical/relationship matching proves insufficient and a benchmark identifies a semantic retrieval requirement.

## First Vertical Slice

The first implementation slice should prove the architecture without AI, embeddings, or scheduling.

Recommended first slice:

```text
source governance
  -> search intent / provider query plan
  -> ingestion-run accounting
  -> one read-only Greenhouse-style provider adapter
  -> immutable source snapshot
  -> import candidate record
```

Non-goals for the first slice:

- no auto-created Opportunities;
- no daily/background execution;
- no scraping;
- no broad aggregator ingestion;
- no embeddings;
- no LLM parsing;
- no canonical capability mutation;
- no dedicated graph/vector database.

## Delivery Unit Boundary

The initiative should be implemented through staged Delivery Units:

1. Source governance and manual ingestion foundation.
2. Source snapshots, normalization, identity, dedupe, and import candidates.
3. JD decomposition and capability taxonomy/proposed-capability workflow.
4. Candidate evidence and explainable matching.
5. Multi-source daily/background orchestration, deferred behind a later human checkpoint.

DU5 must not be pulled into the first implementation prompt.

## Validation Expectations

Before a Build Unit is considered complete, it should include:

- migration and model tests for ownership boundaries;
- provider-adapter fixture tests using static responses, not live provider dependency where avoidable;
- source-governance tests or contract checks;
- dedupe/content-hash tests where relevant;
- parser/taxonomy unit tests where relevant;
- no regression to existing Opportunity/manual intake behavior;
- documentation updates for any changed domain contract.

## Gate Decision

Gate decision: source-truth update approved for LHS generation.

Next step: use `docs/07_prompts/lhs/job-intelligence-ingestion-and-matching-lhs.md` as the staged implementation prompt, with DU5 deferred until a separate automation/background-execution checkpoint is approved.
