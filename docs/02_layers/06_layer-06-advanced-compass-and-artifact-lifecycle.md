# Layer 6 - Advanced COMPASS and Artifact Lifecycle

Status: Draft  
Doc Type: Layer Spec  
Layer: Layer 6  
Source of Truth: Yes  
Last Reviewed: 2026-05-28
Related Docs:
- docs/04_ai-and-compass/compass-evaluation-model.md
- docs/03_domain-design/resume-artifact-generation.md

Layer 6 extends COMPASS and artifacts into lifecycle, evidence mapping, history, review, export, and submitted-artifact tracking.

The canonical local artifact lifecycle states are:

- `draft`: generated or user-edited material that is not yet reviewed.
- `reviewed`: user has reviewed the employer-facing content.
- `submitted`: user marked this exact artifact version as the one used for an application or equivalent submission.
- `archived`: retained for history but inactive by default.

Legacy `approved` and `exported` lifecycle metadata should be normalized as compatibility metadata, not treated as current lifecycle states. Export history remains separate from lifecycle status.

This remains a partially built next lifecycle layer. Use this capsule with [product strategy](../01_strategy/00_product-strategy.md) before implementation prompts.
