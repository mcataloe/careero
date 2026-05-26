# AI Usage and Cost Controls

## Purpose

This document defines Layer 11 readiness for AI usage metering, transparency,
and cost controls.

Layer 11.6 implements durable local-first provider-agnostic AI usage event
metering. It does not implement billing logic, credit wallets, paid quota
enforcement, model marketplaces, or production cost controls.

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

Layer 11.6 records local usage events for:

- Role parsing.
- COMPASS enrichment, including skipped/failed/cache-reused outcomes.
- Resume artifact generation.
- Cover-letter artifact generation.

The read-only local endpoint is `GET /api/usage/ai`, with a Settings page AI
usage panel for recent events and aggregate counts.

## Usage Event Taxonomy

Local metering now tracks provider-agnostic events:

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

Metadata includes workspace/account references where available, feature,
model/provider, prompt version, ruleset version, estimated input/output tokens,
latency, status, cache reuse, sanitized error class, content hash, and safe
metadata. It must not persist raw resumes, raw notes, raw prompts, API keys,
provider credentials, database URLs, or raw private content.

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

Current local UI shows:

- AI feature enabled/disabled state.
- Recent safe usage events and aggregate counts.
- Whether a result was requested, completed, failed, skipped, or cache-reused.
- Model/provider family if relevant.

Future UI may add remaining usage when quotas exist, cost estimates, and richer
artifact lifecycle context after credit/billing policy is approved.

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

## Remaining Future Work

- Credit wallet.
- Paid billing.
- Quota enforcement beyond existing local session caps.
- Model marketplace or user-selected model catalog.
- Production budget alerts and ops dashboards.
- Provider-specific cost accounting.
- Hosted account or tenant changes.
- Raw prompt storage.
