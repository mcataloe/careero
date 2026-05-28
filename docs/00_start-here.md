# Start Here

Status: Active  
Doc Type: Strategy  
Layer: N/A  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/01_strategy/00_product-strategy.md
- docs/01_strategy/07_revised-build-order-execution-plan.md
- docs/02_layers/00_layer-index.md
- docs/07_prompts/00_prompt-index.md

Careero is a local-first career operations application for managing a personal job search, evaluating opportunity fit, preparing application materials, and tracking application workflow. It is organized around LEAP layers and a COMPASS-powered evaluation model.

## Documentation Map

- [Strategy](01_strategy/00_product-strategy.md): product direction, principles, roadmap posture, layer status, monetization boundary, and productization readiness.
- [Revised build order execution plan](01_strategy/07_revised-build-order-execution-plan.md): operational LEAP/LHS prompt sequence, readiness gates, pull-forward rules, and scope discipline.
- [Layers](02_layers/00_layer-index.md): canonical LEAP layer specs and layer capsules. Layer specs are source-of-truth design docs.
- [Domain Design](03_domain-design/00_domain-index.md): opportunity, workspace, application workflow, artifact, automation, and advisor collaboration models.
- [AI and COMPASS](04_ai-and-compass/00_ai-compass-index.md): COMPASS, AI usage controls, AI governance, and prompt-management guidance.
- [Security, Privacy, Governance](05_security-privacy-governance/00_security-privacy-index.md): auth, account lifecycle, privacy/data governance, and canonical contract boundaries.
- [Operations](06_operations/00_operations-index.md): local deployment, deployment readiness, and execution drift memory.
- [Prompts](07_prompts/00_prompt-index.md): generated LEAP Recon requests, LHS prompts, and Codex execution artifacts. Prompts are not source-of-truth product specs.
- [Reports and Audits](08_reports-and-audits/00_reports-index.md): pressure tests, audits, and non-canonical findings.
- [Archive](99_archive/00_archive-index.md): historical or superseded docs retained for context only.

## New Contributor Reading Order

1. This file.
2. [Product strategy](01_strategy/00_product-strategy.md).
3. [Revised build order execution plan](01_strategy/07_revised-build-order-execution-plan.md).
4. [Layer index](02_layers/00_layer-index.md).
5. [Domain index](03_domain-design/00_domain-index.md).
6. [AI and COMPASS index](04_ai-and-compass/00_ai-compass-index.md).
7. [Local deployment](06_operations/local-deployment.md).
8. [Execution drift ledger](06_operations/execution-drift-ledger.md) before planning implementation work.

## Source-of-Truth Rules

The canonical strategy lives in [docs/01_strategy/00_product-strategy.md](01_strategy/00_product-strategy.md).

The operational revised build-order execution guide lives in [docs/01_strategy/07_revised-build-order-execution-plan.md](01_strategy/07_revised-build-order-execution-plan.md).

Canonical layer specs live under [docs/02_layers/](02_layers/00_layer-index.md).

Generated prompts, LEAP Recon requests, LHS prompts, Codex prompts, and filled prompt templates live under [docs/07_prompts/](07_prompts/00_prompt-index.md). Do not treat prompts as canonical design docs.

Archived and superseded material lives under [docs/99_archive/](99_archive/00_archive-index.md). Use it only for historical comparison unless a task explicitly says otherwise.

Active Careero documentation uses COMPASS. STRIDE is legacy terminology and should only appear in archived or historical context unless explicitly explained.
