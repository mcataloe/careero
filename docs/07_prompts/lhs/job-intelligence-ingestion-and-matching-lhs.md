# LEAP LHS — Job Intelligence Ingestion and Candidate Matching Pipeline

Status: Active Prompt  
Doc Type: LHS Prompt  
Source of Truth: No  
Last Generated: 2026-09-28  
Target Repo: `mcataloe/careero`  
Target Branch: create a new feature branch from current `main`  
Related Source Truth:
- `docs/03_domain-design/job-intelligence-ingestion-and-matching.md`
- `docs/02_layers/15_layer-15-api-job-sources-and-managed-deltas.md`
- `docs/03_domain-design/candidate-opportunity-matching.md`
- `docs/03_domain-design/opportunity-model.md`
- `docs/04_ai-and-compass/ai-governance.md`
- `docs/06_operations/execution-drift-ledger.md`

## Prompt Type and LHS Decision

Use LEAP LHS because this initiative has staged dependency order, additive schema work, provider contracts, source-governance risk, matching/taxonomy behavior, docs/tests, and later background-execution risk.

This LHS covers DU1-DU4 planning and implementation sequencing. DU5 daily/background orchestration is intentionally deferred behind a later human checkpoint and must not be implemented from this prompt.

## User Action Before Submission

Before giving this prompt to Codex, confirm that the intended first implementation remains:

- public/official board-scoped ATS-style sources first;
- manual/user-triggered ingestion first;
- proposed capability review required before canonical taxonomy mutation;
- multi-user architecture by design even while local deployment is single-user;
- PostgreSQL-first persistence with no dedicated graph/vector database.

If any of those decisions changed, stop and revise source truth before implementation.

## Agent Execution Configuration

| Field | Required configuration |
|---|---|
| Agent / Tool | Codex |
| Codex Plan Mode | On |
| Model | strongest available coding/reasoning model |
| Reasoning Level | High |
| Execution Mode | plan-first for each Delivery Unit; implement only after plan approval if Codex is configured to ask |
| Scope Scale | Initiative split into Delivery Units and Build Units |
| Repository | `mcataloe/careero` |
| Branch / Worktree | create a feature branch from current `main` |
| Permissions | additive schema/code/tests/docs only |
| Destructive changes | not allowed |
| New infrastructure | not allowed without stop/approval |
| Validation | targeted backend tests, migrations, contracts, relevant frontend checks when UI changes occur |
| Commit Guidance | one coherent commit per Build Unit or tightly coupled Build Unit group; use clear Delivery Unit / Build Unit commit messages |

## Objective

Build the staged foundation for Careero's Job Intelligence Ingestion and Candidate Matching Pipeline.

The pipeline should eventually ingest permitted job postings, preserve source truth, normalize and dedupe postings, decompose job descriptions, resolve capabilities, compare requirements against candidate evidence, and produce explainable fit signals.

This prompt must start with the lowest-risk foundation: manual/user-triggered ingestion, source governance, run accounting, source snapshots, and review-before-save import candidates.

## Current Repo Reality To Respect

- Careero is local-first and not production hardened.
- The repo already has PostgreSQL, SQLAlchemy, Alembic, FastAPI, React/Vite, Mantine, and contracts.
- `Opportunity` is the canonical persistence model backed by the `opportunities` table.
- `Role` and `/api/roles` compatibility surfaces remain and must not be removed.
- `JobSource` exists but is not sufficient by itself for provider governance, source snapshots, query plans, or ingestion runs.
- `workers/` exists as a placeholder only; no background job engine exists.
- Current `/api/opportunities/parse` is OpenAI-backed optional parsing and does not provide the new deterministic/source-ingestion pipeline.
- `AIUsageEvent` exists and should be reused or extended only where model-assisted parsing is actually introduced.
- No `pgvector`, graph database, vector database, provider scheduler, or job-ingestion adapter implementation exists in `main`.

## Source-of-Truth Instructions

Read these files before editing:

1. `AGENTS.md`
2. `docs/00_start-here.md`
3. `docs/01_strategy/00_product-strategy.md`
4. `docs/01_strategy/07_revised-build-order-execution-plan.md`
5. `docs/03_domain-design/job-intelligence-ingestion-and-matching.md`
6. `docs/02_layers/15_layer-15-api-job-sources-and-managed-deltas.md`
7. `docs/03_domain-design/candidate-opportunity-matching.md`
8. `docs/03_domain-design/opportunity-model.md`
9. `docs/06_operations/execution-drift-ledger.md`
10. relevant backend/frontend/contracts files discovered during repo preflight.

Do not use archived docs as current source truth unless explicitly comparing history.

## Global Constraints

- Multi-user by design: all new user-owned records must carry explicit ownership boundaries such as `user_id` and, where relevant, `workspace_id` or a clearly documented later tenant/account abstraction.
- Preserve user-owned Opportunity data separately from imported source truth.
- Adapters must not write directly to Opportunity records.
- The first provider path must be manual/user-triggered only.
- No scraping, restricted-source extraction, LinkedIn scraping, Indeed scraping, Glassdoor scraping, browser automation, anti-bot evasion, or terms-sensitive collection.
- No unattended daily/background execution in this LHS.
- No Neo4j, Neptune, dedicated vector database, Kafka, Celery, APScheduler, hosted queue, cron service, or other major infrastructure without a fresh checkpoint.
- No automatic canonical taxonomy mutation from parser/model output.
- No auto-created Opportunities from imported postings.
- No broad aggregator ingestion in the first slice unless source governance is separately approved.
- No weakening auth/session/current-user boundaries.
- No removal of existing Role compatibility aliases or routes.

## Implementation Stages

### DU1 — Source Governance and Manual Ingestion Foundation

Goal: establish provider/source governance, search intent, provider query planning, and ingestion-run accounting without importing directly into Opportunities.

Build Units:

1. **Provider governance contract**
   - Add conceptual/persistence support for provider metadata and approval status.
   - Capture provider name, provider type, API documentation URL, auth requirement, allowed use, storage permission, raw payload retention permission, summary permission, rate limits, attribution, known restrictions, risk level, and approval status.
   - Keep records additive and multi-user safe. Provider definitions may be system-level; user-specific connections/subscriptions must be scoped.

2. **SearchProfile/SearchIntent boundary**
   - Inspect current Workspace/search-track structures before creating a new entity.
   - Prefer compiling an initial search intent from existing workspace/preferences if sufficient.
   - Create a distinct persisted `SearchProfile` only if lifecycle/versioning/query-plan needs cannot be represented cleanly by existing structures.
   - Document the decision.

3. **IngestionRun and IngestionRunExecution**
   - Add additive persistence for run-level and execution-level records.
   - Track started/completed timestamps, status, trigger type, provider/source/query-plan metadata, requested scope/window, counts, error summary, rate-limit observations, and user/workspace ownership.
   - Manual/user-triggered is the only allowed trigger in this LHS.

4. **Provider adapter interface**
   - Define a boring adapter contract that returns provider-normalized source observations and does not write Opportunities.
   - Include provider capability metadata so board-scoped providers and broad search providers can be treated differently.
   - Add fixtures/tests around the adapter contract.

5. **First read-only provider adapter**
   - Implement one read-only Greenhouse-style public board adapter if provider governance approves it for the local prototype.
   - Use static fixture tests for provider responses.
   - Live calls, if added at all, must be opt-in and not required for test success.

Acceptance criteria:

- A manual ingestion run can be created/executed against a fixture-backed first adapter.
- Run and execution records preserve ownership, timestamps, status, and counts.
- No Opportunity is created or updated automatically.
- No background scheduler exists.
- Provider governance can represent whether a provider is approved, blocked, or pending review.

Suggested validation:

- Alembic migration upgrade test path.
- Backend model/service/API tests for run creation and execution summary.
- Adapter fixture tests.
- Existing Opportunity intake tests still pass.

### DU2 — Source Snapshot, Normalization, Identity, Dedupe, and Import Candidates

Goal: preserve source truth separately from user-owned Opportunities and prepare reviewable import candidates.

Build Units:

1. **Source records and immutable snapshots**
   - Add source-record and snapshot persistence.
   - Preserve source provider, external job ID, source organization/account/board identifier, posting URL/apply URL, retrieved timestamp, source-updated timestamp when available, normalized fields, content hash, and safe raw/source payload handling according to governance.
   - Snapshots must be append-only.

2. **Normalized posting contract**
   - Define normalized posting fields for title, company, location, remote type, employment type, compensation, date posted, description text/html where permitted, status, and provenance.
   - Keep normalized posting source truth separate from user-owned Opportunity fields.

3. **Dedupe and identity candidate logic**
   - Implement deterministic candidate identity using provider/external ID, source URL, company/title, and content hash where appropriate.
   - Do not auto-merge destructively.
   - Surface duplicate/match candidates as advisory records.

4. **Import candidate model**
   - Add review-before-save import candidate persistence.
   - Candidate states should support at least pending/reviewed/saved/ignored/archived or equivalent.
   - Saving as Opportunity can be designed but should remain explicit user action.

Acceptance criteria:

- Ingestion produces immutable source snapshots and reviewable import candidates.
- Duplicate/source identity candidates are visible through backend tests/service outputs.
- Existing user-owned Opportunities are not overwritten.

Suggested validation:

- Backend tests for snapshot immutability.
- Hash/dedupe tests.
- Import candidate lifecycle tests.
- Data export implications reviewed if new user-owned records are created.

### DU3 — JD Decomposition and Capability Taxonomy Foundation

Goal: decompose posting text into structured duties, requirements, preferred qualifications, and proposed/canonical capabilities without relying on LLMs as the default path.

Build Units:

1. **Deterministic JD structural decomposition**
   - Implement heading/bullet/section parsing for common job description structures.
   - Output responsibilities, requirements, preferred/nice-to-have items, and ambiguous items.
   - Preserve source text and parser version.

2. **Requirement records**
   - Persist or return structured requirement records linked to source snapshots/import candidates.
   - Track requirement type: required, preferred, responsibility, descriptive, ambiguous, or equivalent.
   - Include confidence and source text.

3. **Capability taxonomy foundation**
   - Add canonical capability, alias, and relationship records only if not already present.
   - Keep system-shared canonical records distinct from user/private evidence.
   - Use additive migrations only.

4. **Proposed capability workflow**
   - Unknown terms produce proposed capability candidates, not canonical capability records.
   - Track source examples, nearest existing concepts, proposed type, confidence, frequency, parser/ruleset version, and review status.
   - No automatic promotion to canonical.

5. **Optional small-model hook boundary**
   - Define an interface for future lightweight extractor/classifier/embedding tools, but do not add a new model dependency unless explicitly approved and tested.
   - If a model hook is added, it must be optional, disabled by default, and metered through existing AI usage behavior where applicable.

Acceptance criteria:

- JD decomposition works on fixture postings without AI.
- Requirement records preserve type, source text, confidence, and parser version.
- Unknown capabilities enter proposed state.
- No parser output silently mutates canonical taxonomy.

Suggested validation:

- Parser unit tests with representative JD fixtures.
- Proposed capability tests.
- Backward compatibility tests for existing `/api/opportunities/parse` if touched.

### DU4 — Candidate Evidence and Explainable Matching

Goal: compare structured requirements against candidate evidence with traceable, non-overstated support.

Build Units:

1. **Candidate evidence contract**
   - Inspect existing resume/profile source storage before adding new persistence.
   - Define candidate evidence records with source artifact/version references, source text, evidence type, and ownership.
   - Do not duplicate raw private content unnecessarily.

2. **Evidence-to-capability links**
   - Link candidate evidence to canonical capabilities with method, confidence, source text, and parser/ruleset version.
   - Unknown evidence terms should use proposed capability workflow.

3. **Deterministic/canonical matching**
   - Implement exact/canonical capability matching for requirement-to-evidence support.
   - Distinguish EXACT, EQUIVALENT, INFERRED, SEMANTIC, PARTIAL, UNSUPPORTED, and UNKNOWN or an approved subset.

4. **Relationship/graph inference using relational tables**
   - Use relational capability relationships for graph-shaped inference.
   - Do not introduce a graph database.
   - Do not overstate adjacent technology experience as direct experience.

5. **Semantic fallback placeholder**
   - Design a seam for future embeddings/semantic retrieval, but do not implement pgvector or external embedding infrastructure unless separately approved.
   - If a tiny local embedding experiment exists outside the app, keep it out of production persistence unless a later prompt approves it.

6. **Fit summary and evidence report**
   - Produce an approximate fit result with evidence references, unsupported gaps, match types, confidence, and method.
   - A numeric aggregate is allowed only if evidence-level explanations remain visible.

Acceptance criteria:

- Requirements can be matched to candidate evidence through exact/canonical and relationship-based matching.
- Fit output distinguishes supported, partial, unsupported, and unknown requirements.
- Every positive qualification claim traces back to evidence.
- No LLM is required for first explainable matching.

Suggested validation:

- Backend tests with synthetic candidate evidence and JD fixtures.
- False-positive guard tests, especially adjacent tech such as SQS vs Kafka.
- Multi-user isolation tests for candidate evidence and match results.

### DU5 — Deferred Multi-Source Daily/Background Orchestration

Do not implement DU5 from this prompt.

DU5 requires a later human checkpoint and likely its own Recon or LHS section after DU1-DU4 prove the model.

DU5 future scope may include:

- scheduled daily runs;
- concurrency limits;
- retry/backoff policy;
- rate-limit handling;
- run resumption/idempotency;
- alerting/failure visibility;
- provider freshness reporting;
- automation approvals/preferences.

Stop if Codex attempts to implement this now.

## Stop Conditions

Stop and report before proceeding if any of these occur:

- provider terms/storage rights are unclear for the selected source;
- implementation would require scraping or browser automation;
- a destructive migration appears necessary;
- a new infrastructure dependency appears necessary;
- a background scheduler/worker becomes necessary;
- user-owned Opportunity data would be overwritten automatically;
- canonical taxonomy would be mutated automatically from parser/model output;
- multi-user ownership boundaries are ambiguous;
- `/api/roles`, Role aliases, or compatibility fields would be removed;
- tests require live third-party provider access;
- implementation would store raw licensed data beyond approved governance.

## Verification Requirements

Run the most relevant available checks for each Build Unit.

Expected checks include:

```powershell
cd backend
$env:CAREERO_TEST_DATABASE_URL="postgresql://careero:careero@localhost:5432/careero_test"
pytest
```

If frontend UI is touched:

```powershell
cd frontend
npm run test
npm run build
```

If contracts are touched:

```powershell
cd packages/contracts
npm run validate
```

If database schema changes are added, inspect and run Alembic migration paths. Do not claim DB-backed tests passed if the test database is unavailable.

## Documentation Update Policy

Update source-truth docs when behavior or contracts change:

- `docs/03_domain-design/job-intelligence-ingestion-and-matching.md`
- `docs/02_layers/15_layer-15-api-job-sources-and-managed-deltas.md`
- `docs/03_domain-design/candidate-opportunity-matching.md`
- `docs/06_operations/execution-drift-ledger.md` when implementation reality changes or a risk/decision should be preserved.

Do not treat this prompt as source truth. It is an execution artifact.

## Completion Report Format

For each completed Build Unit or Delivery Unit, report:

- objective completed;
- files changed;
- migrations added;
- API/contracts changed;
- tests/checks run;
- tests/checks not run and why;
- assumptions used;
- stop conditions encountered;
- source-truth docs updated;
- remaining risks;
- next recommended Build Unit.

## Gate Decision

Gate decision: LHS generated; ready for Codex only after user confirms the first implementation slice and creates/uses a feature branch.

Recommended first Codex execution: DU1 only, not the whole LHS.
