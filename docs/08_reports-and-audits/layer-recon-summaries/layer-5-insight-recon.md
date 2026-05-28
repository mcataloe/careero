# Layer 5A Insight Recon

Status: Complete  
Doc Type: Audit  
Layer: Layer 5  
Source of Truth: No  
Last Reviewed: 2026-05-28  
Related Docs:
- ../../01_strategy/00_product-strategy.md
- ../../01_strategy/07_revised-build-order-execution-plan.md
- ../../02_layers/05_layer-05-workflow-intelligence-and-insights.md
- ../../03_domain-design/workspace-intelligence.md
- ../../04_ai-and-compass/compass-evaluation-model.md

## Summary

Layer 5 is partially built and already useful. Careero has dashboard analytics,
COMPASS trend insight, search health, recommendations, source intelligence,
compensation intelligence, historical learning, artifact performance analytics,
opportunity intelligence, application workflow summaries, and read-only strategy
synthesis.

The implementation is not yet stabilized as one coherent insight system. Most
Layer 5 surfaces are deterministic and computed on demand from stored local
Careero data, while COMPASS evaluations, opportunity intelligence, generated
artifacts, artifact performance records, automation suggestions, and workflow
records persist insight-like outputs or inputs. The main stabilization risks are
inconsistent contracts, hidden provenance/freshness metadata, uneven workspace
scope visibility, loose `dict[str, Any]` / `Record<string, unknown>` shapes, and
dashboard UX that does not always explain what an insight is based on or what
the user should do next.

This report stays in the existing recon-report convention:
`docs/08_reports-and-audits/layer-recon-summaries/layer-5-insight-recon.md`.
It does not create `docs/layers/layer-05-insight-stabilization/`.

## Repository Inventory

Active source-of-truth strategy and domain docs inspected:

- `docs/01_strategy/00_product-strategy.md`: active strategy source. Identifies
  Layer 5 as the next immediate stabilization focus and records Layer 5 as
  partially built.
- `docs/01_strategy/07_revised-build-order-execution-plan.md`: active LEAP/LHS
  execution guide. Defines terminology rules, build order, and Layer 5 prompt
  sequence.
- `docs/02_layers/05_layer-05-workflow-intelligence-and-insights.md`: active
  but thin Layer 5 capsule. It correctly points to distributed detail but is
  stale relative to implementation breadth.
- `docs/03_domain-design/workspace-intelligence.md`: active workspace/search
  track intelligence design. It defines workspace-scoped strategy synthesis and
  read-only cross-track comparison boundaries.
- `docs/04_ai-and-compass/compass-evaluation-model.md`: active COMPASS guidance.
  It confirms COMPASS as current terminology and STRIDE as legacy.

Active backend insight services, routes, and schemas inspected:

- `backend/app/services/compass_insights.py`,
  `backend/app/api/compass_insights.py`,
  `backend/app/schemas/compass_insights.py`: active search-level COMPASS trend
  surface. Computed on demand from completed COMPASS evaluations, applications,
  roles, and optional workspace preferences. Partial contract: trend points and
  insight fields are typed, but confidence and provenance metadata are
  service-local strings.
- `backend/app/services/search_analytics.py`,
  `backend/app/api/search_analytics.py`,
  `backend/app/schemas/search_analytics.py`: active dashboard metrics,
  conversions, durations, response-rate segments, and focus signals. Partial
  contract: summary metrics are typed, but `signals` remain loose dictionaries.
- `backend/app/services/search_health.py`,
  `backend/app/api/search_health.py`,
  `backend/app/schemas/search_health.py`: active deterministic sustainability
  and workflow-health signals. Uses gentle guidance and avoids gamified
  pressure language. Partial contract: fields are typed, but confidence remains
  stringly typed.
- `backend/app/services/recommendations.py`,
  `backend/app/api/recommendations.py`,
  `backend/app/schemas/recommendations.py`: active read-only next-step
  recommendations. Computed on demand from opportunity intelligence,
  applications, artifact performance, and search-health signals.
- `backend/app/services/source_intelligence.py`,
  `backend/app/api/source_intelligence.py`,
  `backend/app/schemas/source_intelligence.py`: active private source traction
  comparison. Partial contract: source summaries are typed; `insights` are
  loose dictionaries.
- `backend/app/services/compensation_intelligence.py`,
  `backend/app/api/compensation_intelligence.py`,
  `backend/app/schemas/compensation_intelligence.py`: active deterministic
  stated-range and workspace-target comparison. Uses basis/confidence language
  but does not fully share the common governance shape.
- `backend/app/services/historical_learning.py`,
  `backend/app/api/historical_learning.py`,
  `backend/app/schemas/historical_learning.py`: active historical summary
  surface for archived/completed or selected tracks. Computed on demand and
  thin-data aware, but summary-shaped rather than full insight-shaped.
- `backend/app/services/artifact_performance.py`,
  `backend/app/api/artifact_performance.py`,
  `backend/app/schemas/artifact_performance.py`: active artifact performance
  analytics and persisted artifact performance record creation. Uses the shared
  `governed_insight` helper for insight output, but its response schema still
  exposes `insights` as loose dictionaries.
- `backend/app/services/strategy.py`,
  `backend/app/api/strategy.py`,
  `backend/app/schemas/strategy.py`: active read-only Layer 10 strategy
  synthesis that consumes Layer 5 surfaces. This is the strongest current
  contract example: camelCase aliases, confidence objects, insufficient-data
  items, warnings, source input metadata, known uncertainty, and generated
  timestamps.
- `backend/app/services/opportunity_intelligence.py`: active deterministic
  opportunity caution/category analysis stored under
  `roles.parse_metadata.opportunityIntelligence`. Useful but not normalized
  into the broader Layer 5 insight metadata shape.
- `backend/app/services/insight_governance.py`: active but underused helper for
  confidence labels, source inputs, default uncertainty, and governance checks.

Active persisted models inspected:

- `Workspace`: active search-track scope and preference model used by COMPASS,
  compensation intelligence, strategy synthesis, opportunities, artifacts, and
  applications.
- `Role`: active Role-backed opportunity persistence. `parse_metadata` stores
  parsed metadata and deterministic opportunity intelligence.
- `CompassEvaluation`: active persisted opportunity-level COMPASS result,
  summary, recommendation, confidence, section JSON, ATS keywords, source
  hashes, prompt/ruleset metadata, AI status, and raw evaluation JSON.
- `Application` and child workflow records: active workflow state, history,
  notes, reminders, interviews, links, and next-action dates used by dashboard,
  recommendations, search analytics, and application timelines.
- `GeneratedArtifact` and `ArtifactPerformanceRecord`: active generated
  content/metadata and observed artifact performance inputs for insight
  summaries.
- `AutomationSuggestion` and approval logs: active persisted suggestion/audit
  records with basis, confidence, and source inputs.

Active frontend insight surfaces inspected:

- `frontend/src/pages/DashboardPage.tsx`: active Layer 5 dashboard with routed
  sections for overview, COMPASS, sources, compensation, search health,
  recommendations, automation, artifacts, and history. Useful but inconsistent
  in metadata display; most sections omit full scope, freshness, generation
  method, source inputs, and known uncertainty.
- `frontend/src/pages/StrategyPage.tsx`: active read-only strategy workspace.
  Strongest UI example for confidence, warnings, insufficient data, sample size,
  read-only framing, and cross-track comparison.
- `frontend/src/pages/RoleDetailPage.tsx`,
  `frontend/src/components/RoleDetail.tsx`,
  `frontend/src/components/CompassEvaluationDetail.tsx`: active opportunity UI
  for deterministic opportunity intelligence and COMPASS detail. COMPASS detail
  exposes score, recommendation, sections, evidence, gaps, assumptions, AI
  status, unsupported-claim warnings, and validation issues.
- `frontend/src/pages/ApplicationDetailPage.tsx`,
  `frontend/src/components/ApplicationTimeline.tsx`: active application
  workflow UI. Shows current workflow context, COMPASS/artifact badges,
  suggestions, advisor packet preview, and timeline events, but not a complete
  application-specific insight summary.
- `frontend/src/components/InsightMeta.tsx`: active reusable metadata component,
  but too small for Layer 5 stabilization because it only displays confidence
  and basis.

Shared contracts and frontend types inspected:

- `packages/contracts/src/strategy.ts`: active canonical strategy contract with
  confidence, source inputs, known uncertainty, insufficient-data items,
  warnings, action candidates, and cross-track comparison.
- `packages/contracts/src/compass-evaluation.ts`: active canonical COMPASS
  contract. Backend still returns snake_case compatibility fields and broad JSON
  objects; frontend types support both canonical and compatibility shapes.
- `frontend/src/types/compassInsights.ts`,
  `frontend/src/types/searchAnalytics.ts`,
  `frontend/src/types/searchHealth.ts`,
  `frontend/src/types/recommendations.ts`,
  `frontend/src/types/sourceIntelligence.ts`,
  `frontend/src/types/compensationIntelligence.ts`,
  `frontend/src/types/historicalLearning.ts`,
  `frontend/src/types/artifactPerformance.ts`,
  `frontend/src/types/strategy.ts`: active frontend contracts. Many mirror
  loose backend metadata with `Record<string, unknown>`.

Tests inspected:

- Backend: `test_compass_insights.py`, `test_search_analytics.py`,
  `test_search_health.py`, `test_recommendations.py`,
  `test_insight_governance.py`, `test_source_intelligence.py`,
  `test_compensation_intelligence.py`, `test_historical_learning.py`,
  `test_artifact_performance.py`, and `test_strategy.py`.
- Frontend: `DashboardPage.test.tsx`, `StrategyPage.test.tsx`,
  `RoleDetailPage.test.tsx`, `ApplicationDetailPage.test.tsx`, and
  `CompassEvaluationDetail.test.tsx`.
- Contracts: `packages/contracts/tests/contracts.test.ts` and
  `packages/contracts/tests/compass-engine.test.ts`.

Stale, compatibility-only, or deferred items:

- STRIDE appears only in explicit legacy terminology guidance and migration
  compatibility for legacy `stride_evaluations` names. Preserve/defer these
  references; do not rename them now.
- Role-backed persistence remains visible in internals. User-facing copy is
  moving toward Opportunity language, but destructive persistence renames belong
  to later Opportunity model work.
- No generic durable `Insight` table exists. That is acceptable for Layer 5A;
  the immediate need is stronger computed insight contracts and UI metadata.

## Current Behavior Mapping

Computed on demand:

- Search analytics, search health, COMPASS trend insights, source intelligence,
  compensation intelligence, recommendations, historical learning, artifact
  performance summaries, and strategy synthesis are computed at request time
  from stored local data.
- Strategy synthesis composes multiple Layer 5 services and remains read-only:
  it does not mutate workspace preferences, create automation suggestions, save
  retrospectives, or externalize strategy.

Persisted insight-like outputs:

- COMPASS evaluations persist opportunity-level evaluation summaries,
  recommendations, confidence, rationale-like section JSON, evidence/gaps,
  prompt/ruleset/source hashes, AI status, and raw evaluation JSON.
- Opportunity intelligence is persisted inside `Role.parse_metadata` when role
  intake/update refreshes deterministic signals.
- Generated artifacts persist content and metadata used by later summaries.
- Artifact performance records persist observed artifact use/outcome data and a
  snapshot of COMPASS alignment for analytics.
- Automation suggestions persist recommendation-like records with basis,
  confidence, source inputs, preview, policy version, and approval logs.
- Application timeline events are generated from durable records and activity
  logs; the timeline itself is a read model, not a separate event ledger.

Scope relationships:

- Workspace/search track: most analytics endpoints accept optional
  `workspace_id`; strategy requires a workspace for track strategy and can
  compare across workspaces.
- Opportunity: COMPASS evaluations and opportunity intelligence are tied to the
  current Role-backed opportunity model.
- Application: workflow summaries, follow-up recommendations, timelines,
  suggestions, notes, reminders, interviews, and external links are application
  scoped.
- Artifacts: generated artifacts and performance records are tied to workspace,
  opportunity, and optionally application.
- User: services resolve the local current user and query within that boundary.

Generation methods:

- AI-generated or AI-enriched: COMPASS enrichment through OpenAI when enabled;
  resume and cover-letter generation. COMPASS persists AI status, model, prompt
  version, token estimates, latency, hashes, failures, and raw output.
- Deterministic: most Layer 5 insight surfaces use rules, counts, heuristics,
  and database queries over stored data.
- Static/mock data: frontend tests use fixtures; production UI fetches backend
  APIs.

## Data And Contract Audit

Strongest contracts:

- Strategy Pydantic schemas, frontend types, and shared Zod schemas align on a
  canonical contract with camelCase fields, confidence objects, known
  uncertainty, insufficient-data items, source inputs, and generated timestamps.
- COMPASS has a canonical shared contract, reproducibility fields, and backend
  persistence metadata.

Main mismatches and weak contracts:

- Several backend schemas expose `list[dict[str, Any]]` for insight-like arrays:
  search analytics `signals`, source intelligence `insights`, artifact
  performance `insights`, and many metadata/source-input fields.
- Frontend mirrors these weak shapes as `Array<Record<string, unknown>>`,
  requiring defensive `String(...)` rendering and making UI metadata guarantees
  implicit.
- Confidence values vary between canonical strategy levels
  (`weak`, `moderate`, `high`, `insufficient_data`) and display labels
  (`Weak Signal`, `Moderate Confidence`, `Insufficient Data`).
- `source_inputs` exists on many outputs but is rarely structured enough for
  consistent UI rendering, and dashboard panels rarely show it.
- Freshness and scope are incomplete: most analytics responses include
  `workspace_id`, but not `generated_at`, data-window, freshness, or generation
  method.
- Opportunity intelligence uses lower-case heuristic confidence strings and
  does not use the shared governance helper.
- COMPASS backend responses still expose snake_case compatibility fields and
  broad JSON objects while frontend types support a mixed canonical/legacy-ish
  surface.

Layer 5B should define a reusable canonical insight contract before expanding
feature behavior. Minimum fields should include `label`, `message`, `basis`,
`confidence`, `known_uncertainty`, `source_inputs`, `scope`, `generated_at`,
`freshness`, `generation_method`, `severity`, and optional
`recommended_action`.

## UX Audit

Where insights are shown:

- Dashboard overview: workflow attention, search metrics, conversion rates, and
  focus signals.
- Dashboard COMPASS: average score and search-level COMPASS trend insights.
- Dashboard sources: source summary table and private source traction.
- Dashboard compensation: stated-range intelligence.
- Dashboard search health: sustainability and stale/low-fit/volume signals.
- Dashboard recommendations: read-only next steps.
- Dashboard artifacts: observed artifact performance.
- Dashboard history: historical learning summaries.
- Strategy page: workspace strategy overview, retrospective, compensation, role
  positioning, skill gaps, career narrative, signals, actions, uncertainty, and
  cross-track comparison.
- Opportunity detail: opportunity intelligence and COMPASS evaluation detail.
- Application detail: workflow overview, COMPASS/artifact badges, suggestions,
  advisor packet preview, and timeline events.

UX strengths:

- Dashboard uses routed sections, reducing one long panoramic page.
- Strategy page is structured, read-only, and explicitly uncertainty-aware.
- Search-health copy is gentle and avoids gamified pressure.
- COMPASS detail exposes assumptions, evidence gaps, unsupported-claim
  warnings, AI status, validation issues, and section-level evidence.

UX gaps:

- Dashboard panels rarely answer all of: what is this based on, which workspace
  it belongs to, whether it is current, whether it is AI-generated or
  deterministic, and what the user should do next.
- `InsightMeta` only shows confidence and basis, so it is not enough for Layer
  5 stabilization.
- Some dashboard sections rely on dense tables without adjacent insight
  explanation, source-input visibility, uncertainty, or freshness metadata.
- Dashboard currently fetches all-workspace data by default and lacks a
  consistent runtime workspace filter or clear all-workspaces scope indicator.
- Artifact performance UI shows variant metrics but not the insight
  message/basis produced by the service.
- Application overview has useful badges but not an application-specific
  insight summary or next-best-action narrative.

## COMPASS And Terminology Alignment

COMPASS is the active evaluation framework name in code, docs, UI, APIs, tests,
and generated contracts. Current insight outputs generally align with COMPASS as
advisory, explainable, and source-grounded.

Legacy STRIDE references found:

- Active docs mention STRIDE only to state that it is legacy terminology.
- `backend/alembic/versions/0016_compass_table_repair.py` preserves migration
  compatibility for legacy `stride_evaluations` tables, indexes, and
  constraints.

Recommendation: preserve/defer these STRIDE references. Do not rename the
migration compatibility path now, and do not introduce new STRIDE references.

COMPASS alignment gaps:

- Search-level COMPASS insights preserve weak/insufficient confidence but do
  not expose the same structured uncertainty model as strategy.
- Dashboard insights do not consistently distinguish deterministic signals from
  AI-enriched COMPASS outputs.
- Internal strategy analysis is mostly separated from employer-facing artifacts
  through advisor-packet redaction and artifact-generation guardrails, but
  Layer 6 must harden artifact lifecycle and submitted-version boundaries.

## Layer 0 Alignment

Current behavior supports:

- Clarity: metrics and basis strings exist across most surfaces.
- Control: recommendations are read-only; automation remains suggestion/review
  oriented.
- Confidence: many outputs include confidence labels and thin-data messages.
- Continuity: insights draw from saved opportunities, applications, COMPASS,
  artifacts, and workspaces.
- Job-seeker-first support: search health avoids pressure language, and
  recommendations are advisory.
- AI as advisor, not fabricator: AI is concentrated in COMPASS enrichment and
  artifact generation with prompt/ruleset/source metadata and truthfulness
  checks.
- Evidence-based tailoring: COMPASS and artifact generation use active
  resume/profile source grounding.
- Emotional sustainability: search health detects high-pressure patterns
  without diagnosis or shame language.

Risks against Layer 0:

- Dashboard metrics can still feel abstract or opaque because provenance,
  source inputs, generation method, and freshness are hidden.
- Some heuristic labels such as `Strong Fit` or `Archive Candidate` in
  opportunity intelligence could over-signal certainty if not paired with
  visible uncertainty and source basis.
- Compensation heuristics must keep stating that they are internal comparisons
  of stated ranges, not external market salary claims.
- Recommendations need stronger UI language that they are read-only suggestions,
  not directives.
- Future advisor, collaboration, or employer-facing features must not expose
  private COMPASS rationale, ATS risk notes, compensation strategy, or internal
  strategy without explicit user approval.

## Gap Analysis

Missing functionality:

- Canonical Layer 5 insight contract shared across backend, frontend, and the
  contracts package.
- Dashboard workspace filter or explicit all-workspaces scope display.
- Generated/freshness timestamps and generation method metadata on analytics
  responses.
- Structured source input display and drill-in patterns.
- Cohesive "what should I focus on next?" dashboard synthesis that is grounded
  but not directive.

Incomplete functionality:

- Shared `insight_governance` exists but is not consistently used.
- Dashboard UI does not consistently surface insufficient-data messages.
- Artifact performance insights are computed but not prominently displayed.
- Application-specific insight summary is limited to badges, suggestions, and
  timeline events.
- Opportunity intelligence is stored but not normalized into the broader Layer
  5 insight shape.

Stale terminology:

- No active misuse of STRIDE found. Legacy references should remain only for
  historical guidance and migration compatibility.
- Role-backed persistence remains visible in API internals and some type names;
  user-facing copy should continue using Opportunity where possible.

Data model gaps:

- No durable generic `Insight` table exists. This is acceptable for Layer 5A,
  but response contracts need stronger computed insight metadata.
- No explicit insight freshness or data-window model.
- No structured provenance object shared by analytics services.

API contract gaps:

- Loose dictionaries for insights, signals, and source inputs.
- Inconsistent confidence enum/string shape.
- Missing `generated_at`, `scope`, `freshness`, and `generation_method` across
  most Layer 5 responses.
- Mixed snake_case and camelCase contracts outside strategy/shared contracts.

UX gaps:

- Dashboard panels are useful but uneven in hierarchy and explainability.
- Workspace/search-track ownership is often implicit.
- Source inputs and uncertainty are mostly hidden.
- Some pages still rely on dense cards/tables without a shared insight detail
  pattern.

Test gaps:

- No contract-level backend response-shape test suite covers every Layer 5
  endpoint shape.
- Frontend tests cover routing and basic render behavior, but not metadata
  visibility, source scope, freshness, generation method, or thin-data UX
  consistency.
- DB-backed tests require `CAREERO_TEST_DATABASE_URL`; local validation remains
  incomplete without it.

Documentation gaps:

- Layer 5 layer spec is too thin for the implementation breadth.
- No canonical Layer 5 contract/governance doc exists.
- Dashboard/insight UX stabilization criteria are not yet documented.

Risks before Layer 6:

- Artifact lifecycle work could inherit unstable insight/provenance language if
  Layer 5 does not standardize source basis, internal-only analysis, and
  confidence metadata first.
- Artifact performance signals could be misread as proof rather than
  correlation unless standardized uncertainty remains visible.
- Employer-facing artifact boundaries depend on clearly separating internal
  COMPASS/strategy insight from approved outward content.

## Recommended Layer 5B-5D Plan

### 5B - Insight Data Contracts

- Define a canonical insight metadata contract in shared contracts and backend
  schemas with `basis`, `confidence`, `known_uncertainty`, `source_inputs`,
  `scope`, `generated_at`, `freshness`, `generation_method`, `severity`, and
  optional `recommended_action`.
- Normalize confidence labels and enums across deterministic insight services,
  dashboard responses, recommendations, and strategy ingestion.
- Replace loose `dict[str, Any]` / `Record<string, unknown>` insight arrays
  where practical, starting with dashboard-facing analytics endpoints.
- Add explicit workspace/search-track scope and generated timestamp fields to
  all Layer 5 analytics responses.
- Preserve on-demand computation for now; do not add a durable generic insight
  table unless a later requirement needs historical insight snapshots.

### 5C - Insight UI Stabilization

- Expand `InsightMeta` into a reusable insight detail component that can show
  confidence, basis, known uncertainty, source inputs, scope, freshness, and
  generation method.
- Update dashboard panels to use consistent insight metadata display and
  thin-data messaging.
- Add dashboard workspace selection or a clear all-workspaces scope indicator.
- Show artifact performance insight messages in addition to the variant table.
- Keep recommendations read-only and framed as advisory next steps.
- Avoid broad layout changes; preserve routed dashboard sections and focus on
  explainability, hierarchy, and reduced scanning fatigue.

### 5D - Tests And Docs

- Add backend response-shape tests for every Layer 5 endpoint, including
  confidence, basis, source inputs, scope, generated timestamp, and thin-data
  behavior.
- Add frontend tests for dashboard metadata visibility, empty/thin-data states,
  workspace scope, routed section behavior, and artifact insight visibility.
- Add contract tests for the canonical insight metadata shape.
- Update `docs/02_layers/05_layer-05-workflow-intelligence-and-insights.md`
  after stabilization to point to the canonical insight contract and UX
  criteria.

## Deferrals

- Layer 6: artifact lifecycle, review/edit/approve/archive, submitted artifact
  tracking, artifact comparison, and JD-to-resume evidence mapping.
- Layer 7: destructive Role-to-Opportunity persistence rename.
- Layer 10: durable strategy records, external market strategy intelligence, or
  AI strategy memory.
- Layer 14: model catalog, model gateway, prompt compiler, prompt-only export,
  credit controls, and model-cost governance.
- Layer 16: first-run onboarding explanations for workspaces/search tracks,
  COMPASS setup, source grounding, and insight interpretation.

## Validation

Validation performed during Layer 5A recon on 2026-05-28:

- `cd backend; .\.venv\Scripts\python.exe -m pytest tests/test_compass_insights.py tests/test_search_analytics.py tests/test_search_health.py tests/test_recommendations.py tests/test_insight_governance.py tests/test_source_intelligence.py tests/test_compensation_intelligence.py tests/test_historical_learning.py tests/test_artifact_performance.py tests/test_strategy.py`
  returned 16 passed and 7 errors. The errors were all database-backed tests
  blocked by missing `CAREERO_TEST_DATABASE_URL`.
- `cd frontend; npm.cmd run test -- DashboardPage.test.tsx StrategyPage.test.tsx RoleDetailPage.test.tsx ApplicationDetailPage.test.tsx CompassEvaluationDetail.test.tsx`
  passed: 5 files, 29 tests.
- `cd packages/contracts; npx.cmd vitest run tests/contracts.test.ts tests/compass-engine.test.ts`
  passed: 2 files, 29 tests.

Do not hide the backend validation blocker: database-backed Layer 5 tests still
need a configured `CAREERO_TEST_DATABASE_URL` before they can fully pass.

## Recommendation

Proceed to Layer 5B data contract stabilization before changing dashboard
behavior. The contract pass should make insight provenance, confidence,
uncertainty, workspace scope, freshness, and generation method explicit enough
that Layer 5C can improve UX without inventing hidden frontend-only semantics.
