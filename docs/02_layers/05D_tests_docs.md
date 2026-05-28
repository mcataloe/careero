# Layer 5D Insight Tests and Documentation

Status: Complete  
Doc Type: Implementation Summary  
Layer: Layer 5  
Source of Truth: No  
Last Reviewed: 2026-05-28  
Related Docs:
- 05_layer-05-workflow-intelligence-and-insights.md
- 05B_insight_data_contracts.md
- 05C_insight_ui_stabilization.md
- ../08_reports-and-audits/layer-recon-summaries/layer-5-insight-recon.md

## Purpose

Layer 5D closes the insight stabilization pass with focused verification and documentation. It does not add a new insight engine, persistence model, route, migration, or feature surface.

Careero insights remain job-seeker-first decision support: advisory, source-grounded, transparent about uncertainty, and separate from employer-facing artifacts.

## Current Insight Architecture

Layer 5 currently computes most insights on demand from stored Careero data:

- opportunities/roles and parsed opportunity metadata
- applications, state transitions, reminders, interviews, notes, and timeline activity
- COMPASS evaluations
- generated artifacts and artifact performance records
- workspace/search-track preferences and status
- source metadata and compensation observations

The system does not persist a generic `Insight` table. Persisted insight-like records still live on their owning product objects, including COMPASS evaluations, generated artifacts, artifact performance records, automation suggestions, and workflow/activity records.

## Contract Summary

The Layer 5B contract is the current shape for insight-like arrays. Important fields include:

- `id`, `category`, `label`, `message`, and `basis`
- `confidence`, `confidence_level`, and `confidence_explanation`
- `known_uncertainty`, `warnings`, `severity`, and `priority`
- `generation_method` and `visibility`
- `scope`, `source_references`, and `source_inputs`
- `freshness`
- optional `recommended_action`

The API-facing frontend and backend contracts use snake_case. The shared package canonical contract uses camelCase for Zod and JSON Schema generation.

## Provenance Model

Insights should expose the data they are based on through `basis`, `source_inputs`, and `source_references`. Source references may point to opportunities, raw job descriptions, parsed fields, COMPASS evaluations, resume/source material, artifacts, user notes, application events, workspaces, or other future source types.

Provenance is strongest when an insight can name both the source class and the specific field or record. Some current computed insights still use source inputs without exhaustive source references; that is a known limitation, not a reason to overstate certainty.

## Confidence and Uncertainty Rules

Confidence is displayed as a human label while `confidence_level` carries the machine-readable value. Weak or insufficient-data signals should stay advisory and should explain their limitations through uncertainty and warnings.

Layer 5 should avoid false precision. It should not infer public market data, recruiter behavior, company operating reality, or causality from local correlation unless the user has stored evidence for that claim.

## UI Rendering Rules

Layer 5C introduced shared insight rendering for dashboard insight rows. UI rules:

- show severity with text and icon, not color alone
- show confidence, scope, generation method, freshness, basis, uncertainty, warnings, and source references where present
- keep longer provenance detail behind progressive disclosure
- render recommended actions as links only when a real `route_path` exists
- use calm empty states for thin data
- keep loading and error states recoverable through existing app patterns

## Internal Boundary

Layer 5 insights default to `visibility="internal"`. Internal COMPASS rationale, private strategy notes, compensation strategy, recruiter/contact details, raw source text, and private workflow notes must not be inserted into employer-facing resume or cover-letter content.

Advisor packet preview remains local-only and redacted by default. It can show that private fields exist and why they are redacted, but it must not become a hosted sharing surface in Layer 5.

## COMPASS Terminology

COMPASS is the active framework name. Current Layer 5 UI, contracts, tests, and docs should not introduce legacy evaluation-framework terminology.

## Known Limitations

- No durable generic insight snapshot table exists.
- Source references are not yet exhaustive across every service.
- Workspace filtering exists in backend services but runtime workspace switching UX remains limited.
- Artifact lifecycle is not mature enough to make artifact insight provenance complete.
- DB-backed ownership and endpoint response-shape tests depend on `CAREERO_TEST_DATABASE_URL`.

## Deferred Work

- Layer 6: artifact lifecycle, submitted artifact tracking, artifact provenance, review/edit/submit/archive, comparison, and export UX.
- Layer 7: Opportunity compatibility surface and any future Role-to-Opportunity persistence migration.
- Layer 10: advanced search-track strategy and deeper cross-track comparison.
- Layer 14: model usage accounting, model routing, prompt architecture, and credit controls.
- Layer 16: guided onboarding and contextual help for users with thin search data.

## Validation Plan

Layer 5D validation should include:

- shared contract validation and generated JSON Schema checks
- backend pure service tests for governance and Layer 5 insight response shapes
- frontend component/page tests for metadata, provenance, empty/loading/error states, action links, and advisor-packet boundaries
- frontend build/typecheck

DB-backed insight endpoint and ownership tests should be run when `CAREERO_TEST_DATABASE_URL` is available. If it is unavailable, record the blocker rather than hiding it.

## Validation Results - 2026-05-28

- Contracts: `npm.cmd run validate` in `packages/contracts` passed. Build, JSON Schema generation, and tests completed with 2 test files and 33 tests passing.
- Frontend: `npm.cmd run test -- InsightMeta.test.tsx DashboardPage.test.tsx RoleDetail.test.tsx ApplicationDetailPage.test.tsx AutomationSuggestionsPanel.test.tsx CompassEvaluationDetail.test.tsx` passed with 6 test files and 31 tests passing.
- Frontend build: `npm.cmd run build` passed. Vite still reports the existing large-chunk warning for the main JavaScript bundle.
- Backend pure Layer 5 tests: `.\.venv\Scripts\python.exe -m pytest tests\test_insight_governance.py tests\test_compass_insights.py tests\test_artifact_performance.py tests\test_recommendations.py tests\test_search_health.py tests\test_compensation_intelligence.py tests\test_source_intelligence.py tests\test_historical_learning.py` passed with 20 tests passing.
- DB-backed endpoint and ownership tests were not run because `CAREERO_TEST_DATABASE_URL` was unset in this environment.
