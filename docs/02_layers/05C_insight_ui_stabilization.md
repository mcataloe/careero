# Layer 5C Insight UI Stabilization

## Summary

Layer 5C stabilizes insight presentation without changing backend routes, persistence, or Layer 5B data contracts. The UI now treats the Layer 5B `Insight` contract as the rendering source for dashboard-facing insight lists, while preserving existing metrics, tables, and routed dashboard sections.

## UI Contract Usage

Current insight rows render the following contract fields when available:

- `label`, `message`, `category`, `severity`, and `priority` for hierarchy.
- `confidence`, `confidence_level`, and `confidence_explanation` for uncertainty.
- `generation_method`, `scope`, `basis`, `source_references`, and `source_inputs`-adjacent labels for explainability.
- `freshness.generated_at`, `source_updated_at`, `is_stale`, and `refresh_reason` for recency.
- `known_uncertainty` and `warnings` behind progressive disclosure.
- `recommended_action.route_path` as the only source of clickable next-step routing.

The dashboard continues to show computed insight data only. No new persisted insight model, migration, route, or backend generation behavior was added in this layer.

## Stabilized Surfaces

- Dashboard overview focus signals now use typed insight rendering instead of loose string casting.
- COMPASS, compensation, search-health, and recommendations panels share consistent metadata and uncertainty rendering.
- Source intelligence and artifact performance panels now show narrative insight messages in addition to their existing metric tables.
- Historical learning keeps its observed-answer table while exposing insight metadata for confidence and provenance.
- Opportunity intelligence keeps its existing deterministic signal data and improves confidence/basis visibility without introducing a new opportunity insight engine.

## Boundaries

Layer 5C keeps insight UI internal to job-search decision support. It does not expose private COMPASS analysis or internal strategy notes inside employer-facing artifact/advisor-packet content. Application suggestions remain local review workflow controls, not external actions.

## Deferred Work

- Layer 5D should add broader component-level coverage for insight metadata permutations and stale/refresh states.
- Layer 6 should decide how artifact lifecycle events become insight source references.
- Layer 10 can add higher-order strategy synthesis once the base insight rendering contract is stable.
- Layer 16 can add onboarding-specific explanation for users who have not yet generated enough search data.
