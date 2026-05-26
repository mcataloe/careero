# AI Usage and Cost Controls

## Purpose

This document defines Layer 11 readiness for AI usage metering, transparency,
and cost controls. It is provider-agnostic design guidance only. It does not
implement counters, database tables, billing logic, or rate limiting.

## Why AI Cost Controls Matter

AI features can create variable cost, privacy risk, quality risk, and trust
risk. Careero must keep AI source-grounded, user-visible, reviewable, and
bounded before any hosted beta or paid tier.

## Current AI Usage Surfaces

| Surface | Current posture | Readiness note |
| --- | --- | --- |
| Job parsing | Optional AI-assisted parsing, review-before-save. | Track attempts, fallback, confidence, and user acceptance later. |
| COMPASS enrichment | Optional OpenAI enrichment grounded in role and active resume/profile source. | Current process-level attempt cap exists locally; durable metering is future. |
| Resume generation | Draft generation grounded in source, opportunity, and COMPASS evaluation. | Must stay TruthGuard checked and user reviewed. |
| Cover-letter generation | Draft generation grounded in opportunity and optional source/evaluation. | Must stay draft-only until lifecycle is mature. |
| Career strategy synthesis | Current MVP is read-only and based on stored Careero evidence. | Optional AI summarization remains future. |
| Integration summarization | Future only. | Requires integration privacy and token handling design first. |
| Automation suggestions | Local suggestions and approval logs exist. | External actions remain disabled. |

## Usage Event Taxonomy

Future metering should track provider-agnostic events:

- `ai.parse_opportunity.requested`
- `ai.parse_opportunity.completed`
- `ai.compass_enrichment.requested`
- `ai.compass_enrichment.completed`
- `ai.resume_artifact.requested`
- `ai.resume_artifact.completed`
- `ai.cover_letter_artifact.requested`
- `ai.cover_letter_artifact.completed`
- `ai.strategy_summary.requested`
- `ai.integration_summary.requested`
- `ai.automation_suggestion.requested`
- `ai.failure`
- `ai.cache_reused`
- `ai.skipped_disabled`
- `ai.skipped_quota`

Suggested metadata: workspace, account, feature, model/provider, prompt version,
ruleset version, estimated input/output tokens, latency, status, cache hit,
error class, content hashes, and safety warnings. Do not log raw resumes, raw
notes, raw prompts, API keys, or raw private content in operational logs.

## Provider-Agnostic Metering Model

Metering should separate:

- User-visible usage units.
- Provider cost estimates.
- Internal diagnostic metadata.
- Billing events, if billing is later approved.

Possible unit types:

- AI request count.
- Generated artifact count.
- Evaluated opportunity count.
- Token estimate bands.
- Workspace-level monthly quota.
- Feature-specific daily limits.

Billing provider integration is future and not part of this design.

## Rate-Limit and Quota Concepts

- Per-account daily AI request limit.
- Per-workspace monthly AI request limit.
- Feature-specific artifact generation limit.
- Burst limit for repeated retries.
- Lower limit for anonymous/local demo modes.
- Admin kill switch for hosted environments.
- Provider budget cap per environment.
- Cache reuse that does not consume quota unless approved otherwise.

## Candidate Tier Boundaries

| Tier candidate | Possible boundary | Notes |
| --- | --- | --- |
| Free useful baseline | Manual workflow, local records, deterministic COMPASS, limited AI attempts. | Must remain useful before paid conversion. |
| Paid individual/power-user | Higher saved record volume, richer analytics, artifact lifecycle depth. | Should not lock essential organization behind an expensive tier before value is proven. |
| Paid AI/artifact quota | More AI generations, higher monthly caps, export convenience. | Transparent usage limits required. |
| Future collaboration tier | Advisor/reviewer access and comments. | Requires account lifecycle and sharing design first. |

## Cost-Risk Controls

- Feature flags for AI surfaces.
- Environment-level provider budgets.
- Per-user and per-workspace quotas.
- Request deduplication and cache reuse.
- Timeouts and max output token caps.
- Structured output validation.
- Truthfulness checks before persistence.
- Clear fallback behavior when AI is disabled or quota is exhausted.
- Redaction and logging limits.

## User-Visible Usage Transparency

Future UI should show:

- AI feature enabled/disabled state.
- Remaining usage when quotas exist.
- Whether a result was deterministic, cached, or AI-enriched.
- Model/provider family if relevant.
- Warnings and grounding sources.
- Whether an artifact is draft, reviewed, approved, exported, or submitted.

## Admin/Ops Visibility Requirements

Future hosted operations need aggregate views for:

- Cost by environment, feature, and provider.
- Error rate and latency.
- Quota exhaustion.
- Abuse patterns.
- Safety validation failures.
- Cache hit rates.

Admin views must not expose private content unless a narrowly scoped support
mode is separately approved and audited.

## Monetization Guardrails

Careero must not use AI cost controls as a cover for hidden steering, employer
paid prioritization, pay-to-rank listings, selling attention, or undisclosed
sponsored recommendations.

## Stop Conditions Before Metering Implementation

Stop before implementation if the scope requires new database tables, billing
events, provider-specific payment logic, auth/tenant changes, raw prompt
storage, external account linking, or a new dependency without explicit approval.
