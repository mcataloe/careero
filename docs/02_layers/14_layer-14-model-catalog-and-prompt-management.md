# Layer 14 â€” Model Catalog, Prompt Architecture & Credit Controls

Status: Draft  
Doc Type: Layer Spec  
Layer: Layer 14  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/04_ai-and-compass/prompt-management.md
- docs/04_ai-and-compass/ai-usage-cost-controls.md

## Status

Future / appended strategic layer.

Layer 14 replaces the model-related portions of the older combined Layer 14 planning concept. It should remain focused on model choice, Careero-owned prompt architecture, model routing, quality checks, usage accounting, and credit controls.

API job-source ingestion, official ATS/job-board adapters, imported job snapshots, and managed deltas now belong to **Layer 15 â€” API Job Sources, Import Pipelines & Managed Deltas**.

Layer 14 may be pulled forward with Layer 11 productization work when model usage, AI cost controls, billing boundaries, and credit economics are actively scoped. It does not require employer-side or marketplace work to be complete.

## Purpose

Give Careero a flexible but controlled model-selection system so users can choose different AI models for different product components while Careero preserves consistent prompt behavior, source grounding, truthful artifact generation, quality checks, cost visibility, and credit controls.

The strategic goal:

> Careero owns the prompt architecture, model catalog, source grounding, output contracts, quality checks, usage accounting, and credit policy. Users choose model and budget inside those guardrails.

Layer 14 should make model choice useful without turning the product into a loose prompt playground.

## Core Product Principle

Users should be able to choose models by user-facing value and task fit, not by raw provider jargon alone.

Good model-choice language:

- Fast + affordable.
- Best writing balance.
- Premium reasoning.
- Prompt-only export.
- Default Careero recommendation.

The product can expose technical details for power users, but the main UX should explain what the choice means in plain language: expected quality, cost, latency, context capacity, and recommended use.

## Candidate User-Selectable Components

Layer 14 should eventually support user-selected model defaults for:

- Job / opportunity parsing.
- COMPASS evaluation enrichment.
- Resume artifact generation.
- Cover-letter artifact generation.
- Interview preparation.
- Career strategy synthesis.
- Company research summarization when Layer 15 or a later company-research source layer provides source-governed facts.
- Prompt-only export for users who want to run the compiled prompt in an external model themselves.

Initial implementation should not support every component at once. Start with the components where model quality and cost matter most:

1. Resume generation.
2. Cover-letter generation.
3. COMPASS enrichment / fit analysis.
4. Prompt-only export.

## Careero Prompt Architecture

Careero should compile prompts from structured, versioned modules rather than constructing ad hoc freeform prompts throughout the codebase.

Recommended prompt modules:

- `identity_context`
- `source_material_context`
- `opportunity_context`
- `company_context_reference`
- `artifact_rules`
- `task_contract`
- `model_adapter`
- `truth_policy`
- `ats_policy`
- `quality_rubric`
- `output_contract`
- `prompt_version`
- `source_reference_manifest`

The prompt architecture should separate:

- Product policy.
- User source facts.
- Opportunity facts.
- Company or job-source context.
- Artifact-specific rules.
- Model-specific formatting.
- Output validation.
- Quality checks.

This separation matters because model choice should not create different truth standards. A premium model may reason better, but it must not be allowed to invent credentials, metrics, employment history, dates, certifications, clearance levels, tools, responsibilities, or compensation claims.

## Prompt Spec Contract

A compiled prompt spec should include:

- Prompt spec ID.
- Prompt spec version.
- Task type.
- Artifact type, when applicable.
- Target model/provider.
- Model adapter instructions.
- User profile/source resume facts.
- Opportunity facts.
- Optional company/job-source facts with source references.
- Output contract.
- Truth policy.
- ATS/readability policy, when applicable.
- Quality rubric.
- Source reference manifest.
- Guardrails.
- Estimated cost tier.
- Prompt-only export eligibility.

Prompt specs should be durable enough that Careero can answer:

- Which prompt version generated this artifact?
- Which model was used?
- Which source facts were included?
- Which opportunity facts were included?
- Which quality checks ran?
- Which user-visible artifact resulted from the run?

## Model Catalog Architecture

The model catalog should describe available providers and models in a product-safe, refreshable way.

Candidate tables / records:

- `model_provider`
- `model_catalog_entry`
- `model_price_snapshot`
- `model_task_capability`
- `model_task_default`
- `model_availability_policy`
- `prompt_spec`
- `prompt_spec_version`
- `prompt_run`
- `prompt_run_source_reference`
- `quality_check_result`
- `usage_event`
- `artifact_usage_record`
- `credit_wallet`
- `credit_transaction`

The model catalog should track:

- Provider.
- Model name.
- Display name.
- Task suitability.
- Enabled / disabled state.
- Quality tier.
- Latency tier.
- Context-window tier.
- Input/output pricing snapshot.
- Pricing snapshot freshness.
- Supported capabilities.
- Default task mappings.
- Known limitations.
- Internal notes for admin/operator use.

Do not hard-code model choices throughout generation services. Product code should ask for the model selected for the task, then use the gateway/prompt compiler to assemble the run.

## Model Gateway

The model gateway should provide a thin controlled boundary around provider calls.

Candidate responsibilities:

- Resolve selected model for a task.
- Validate model is enabled and allowed for the user/plan.
- Compile prompt spec.
- Estimate cost before the run.
- Reserve credits if credit enforcement is active.
- Call provider adapter.
- Normalize provider response metadata.
- Run output contract validation.
- Run quality checks.
- Debit/refund credits according to policy.
- Persist usage event and artifact usage record.
- Return a reviewable result to the application layer.

Initial provider candidates:

- OpenAI.
- Anthropic.
- Google.
- Future model gateway/router if product and security boundaries justify it.

Provider adapters should be boring on purpose. The intelligence belongs in Careero prompt architecture and product workflow, not in scattered provider-specific conditionals.

## Prompt-Only Export

Prompt-only export is a first-class Layer 14 capability.

Purpose:

- Let users copy a Careero-compiled prompt into ChatGPT, Claude, Gemini, or another external model.
- Preserve Careero's source-grounded prompt structure even when Careero is not making the provider call.
- Reduce cost and support burden for users who prefer their own AI subscriptions.
- Provide a low-risk bridge before managed multi-provider routing is fully built.

Boundaries:

- Exported prompts should include clear user-facing instructions.
- Exported prompts must not include secrets, internal API keys, database IDs, hidden risk notes, or private system-only policy text.
- Exported prompts may include user-approved source facts and opportunity facts needed for the task.
- Careero cannot verify external model output unless the user pastes the result back for review.

## Credit Wallet, Usage Metering & Cost Controls

Credits belong in Layer 14 because model choice and prompt runs create real cost and productization pressure.

Credits should represent Careero work units, not raw tokens.

Internal principle:

> Credits = model cost + complexity + quality-check cost + margin buffer + abuse buffer.

Layer 15 API-job-source usage may later feed API costs into the same usage/credit ledger, but Layer 15 owns job-source ingestion architecture. Layer 14 owns the common model-run and credit-control foundation.

Candidate credit events:

- `grant`
- `reserve`
- `debit`
- `refund`
- `expire`
- `adjustment`
- `topup_purchase`
- `rollover`

Required boundaries:

- Do not reduce credit balance without a durable ledger entry.
- Do not treat a mutable `credit_balance` column as the source of truth.
- Do not hide premium model multipliers.
- Do not auto top-up without explicit opt-in and a visible spending cap.
- Do not implement paid credit expiration without legal/product review.
- Do not charge users for failed generation attempts unless the failure policy explicitly allows a partial charge and the user was told in advance.
- Do not let provider price changes silently destroy margins; price snapshots must be refreshable.

## Quality Checks

A generated output should pass a quality-check layer before being treated as usable.

Candidate checks:

- Factual drift.
- Fabricated experience.
- Unsupported credentials.
- Unsupported metrics.
- Missing job alignment.
- ATS/readability issues.
- Tone mismatch.
- Length mismatch.
- Output contract violations.
- Employer-facing leakage of internal strategy notes.
- Compensation or negotiation commentary appearing in employer-facing artifacts.

Quality checks should produce reviewable warnings, not merely pass/fail booleans.

## Required Boundaries

Layer 14 must not:

- Let model-specific prompt logic leak across the product.
- Let job descriptions, imported job postings, company pages, or uploaded documents override Careero prompt policy.
- Invent employment history, tools, certifications, clearance levels, dates, metrics, responsibilities, or compensation claims.
- Implement bring-your-own-key until account security, key storage, provider limits, billing interactions, and support burden are designed.
- Implement API job-source ingestion, ATS provider adapters, source snapshots, managed deltas, or external job-data imports. Those belong to Layer 15.
- Implement scraping, restricted-source extraction, browser-driven collection, or terms-sensitive data collection.
- Expose hidden system rules or internal prompt policy in user-facing prompt-only export.

## Relationship to Other Layers

### Layer 3 and Layer 6

Layer 14 powers better artifact generation, but it does not replace artifact lifecycle. Layer 6 still owns review, approval, submitted artifacts, comparisons, and artifact retrieval.

### Layer 7

Layer 14 consumes Opportunity facts. It should not restart Opportunity semantics.

### Layer 8

Layer 14 may use integration outputs as source references, but it does not own integration account linking or external source ingestion.

### Layer 11

Layer 14 is closely related to productization. Credits, model selection, plan limits, cost estimation, and usage controls should align with Layer 11 monetization and entitlement boundaries.

### Layer 15

Layer 15 can call Layer 14 for AI-assisted extraction, summarization, or classification after Layer 14 exists. Layer 15 owns source-provider adapters, imported job snapshots, managed deltas, and review-before-save flows.

## Recommended LEAP Recon Questions

- Which tasks should expose model choice first?
- What default model should Careero recommend per task?
- What model metadata must be stored in the catalog?
- What provider adapters should be supported first?
- What is the minimum viable prompt spec?
- Which prompt modules are shared across all tasks?
- Which prompt modules are task-specific?
- Which prompt modules are model-specific?
- What prompt-only export experience is required?
- What quality checks are required before a generated artifact is considered usable?
- How should model price snapshots be stored and refreshed?
- How should usage events map to credit reservations, debits, and refunds?
- What should happen when generation fails or quality checks fail?
- Which user-facing cost explanation is required before and after a run?
- What must remain future until billing, security, or account boundaries mature?

## Recommended Implementation Order

1. Layer 14 Recon focused only on model catalog, prompt architecture, and credits.
2. Careero Prompt Architecture design.
3. Prompt spec and prompt module contract.
4. Model provider/catalog/price snapshot design.
5. Task-default model selection design.
6. Usage event and credit ledger design.
7. Prompt-only export.
8. First managed model adapter.
9. Post-generation quality-check pipeline.
10. Credit reservation/debit/refund implementation.
11. User-facing model choice UX.
12. Admin/operator model catalog management.

## Exit Criteria

Layer 14 is implementation-ready when:

- Prompt architecture is defined.
- Model catalog schema is defined.
- Model task defaults are defined.
- Prompt-only export behavior is defined.
- Credit ledger semantics are defined.
- Quality-check behavior is defined.
- User-facing model-choice UX is defined.
- Non-goals are explicit.
- Layer 15 job-source ingestion is clearly out of scope for this layer.

