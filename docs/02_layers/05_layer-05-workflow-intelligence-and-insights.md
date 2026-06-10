# Layer 5 - Workflow Intelligence and Insights

Status: Stabilized for current local MVP scope  
Doc Type: Layer Spec  
Layer: Layer 5  
Source of Truth: Yes  
Last Reviewed: 2026-05-28  
Related Docs:
- docs/02_layers/05B_insight_data_contracts.md
- docs/02_layers/05C_insight_ui_stabilization.md
- docs/02_layers/05D_tests_docs.md
- docs/03_domain-design/workspace-intelligence.md
- docs/08_reports-and-audits/layer-recon-summaries/layer-5-insight-recon.md
- docs/01_strategy/00_product-strategy.md

## Purpose

Layer 5 turns saved opportunities, application workflow activity, COMPASS evaluations, generated artifacts, source metadata, compensation observations, and historical outcomes into advisory insight.

The layer exists to help job seekers understand what is working, what is stuck, what needs review, and what to do next without creating false certainty or employer-centered pressure.

## Current Architecture

Layer 5 uses computed insight surfaces rather than a durable generic `Insight` table. Current insight-like data is returned from analytics and dashboard endpoints for:

- search analytics and focus signals
- COMPASS search trends
- source intelligence
- compensation intelligence
- search health signals
- recommendations
- historical learning summaries
- artifact performance

Persisted source data still lives in the underlying product records: opportunities/roles, applications, COMPASS evaluations, generated artifacts, artifact performance records, workflow activity, notes, reminders, interviews, workspaces, and automation suggestions.

## Stabilization State

Layer 5 is stabilized for the current local MVP scope because:

- Insight data contracts now expose identity, category, basis, confidence, uncertainty, provenance, freshness, scope, visibility, and optional recommended actions.
- Backend service outputs use normalized governance metadata for current Layer 5 insight arrays.
- Dashboard insight UI renders metadata consistently and keeps details progressively disclosed.
- Tests cover canonical contract validation, backend governance behavior, service response shapes, dashboard rendering, empty/error/loading states, and internal-only advisor-packet boundaries.

Layer 5 is not complete for all future product scope. Durable insight snapshots, richer workspace switching UX, artifact lifecycle integration, advanced cross-track strategy, model usage accounting, and onboarding guidance remain later-layer work.

## Product Boundaries

Layer 5 insights are internal by default. They are decision support for the job seeker, not employer-facing artifact content.

Insight text must remain advisory, source-grounded, and transparent about uncertainty. It must not imply that Careero has external market knowledge, private recruiter knowledge, company-inside information, or deterministic truth unless that evidence exists in stored source data.

## Terminology

COMPASS is the current evaluation framework. Do not introduce legacy evaluation-framework terminology into new Layer 5 UI, contracts, tests, or docs.

## Deferred Work

- Layer 6: artifact lifecycle, submitted artifacts, artifact-source references, and review/submit/export UX.
- Layer 7: Opportunity compatibility surface and post-7C Role compatibility cleanup decisions.
- Layer 10: advanced search-track strategy and cross-track synthesis beyond current read-only MVP.
- Layer 14: model usage accounting, model routing, prompt architecture, and credit controls.
- Layer 16: guided onboarding and contextual help for users with thin search data.
