# Monetization Boundary

Status: Active  
Doc Type: Strategy  
Layer: Layer 11  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/01_strategy/06_productization-readiness.md
- docs/04_ai-and-compass/ai-usage-cost-controls.md

## Purpose

This document defines Careero's Layer 11 monetization posture. It is
provider-agnostic design guidance with a local-first boundary implementation.
It does not implement billing, subscriptions, checkout, invoices, payment
links, or usage-meter billing.

Layer 11.7 adds a local entitlement boundary model through
`GET /api/entitlements/current` and a Settings page Local plan panel. The
current plan is `local_free`, billing status is `not_configured`, and payment
provider is `none`.

## Layer 0 Trust Principles

Careero is job-seeker-first. It should help the user understand, prioritize,
prepare, and execute their search without selling their attention or distorting
recommendations for employer benefit.

AI is an advisor, not a fabricator. User source material remains the ground
truth. Review-before-send, no-auto-apply, and source-grounded AI are product
trust boundaries, not optional settings.

## Job-Seeker-First Monetization Posture

Monetization may eventually support sustainability, but it must not compromise:

- User control over private job-search data.
- Clear separation between internal strategy and employer-facing artifacts.
- Transparent recommendation basis.
- Reviewable artifacts and automation.
- Local-first value before paid conversion.
- Marketplace last.

## Candidate Tiers

| Candidate tier | Possible value | Readiness requirement |
| --- | --- | --- |
| Free useful baseline | Manual opportunities, workflow tracking, deterministic COMPASS, limited local artifacts/analytics. | Must be genuinely useful. |
| Paid individual/power-user tier | Higher volume, richer analytics, advanced workflow, better artifact lifecycle. | Requires stable user-side workflow value. |
| Paid AI/artifact quota tier | More AI generations, export convenience, higher monthly AI limits. | Requires usage transparency and cost controls. |
| Future coach/advisor collaboration tier | Scoped reviewer/advisor access and comments. | Requires account lifecycle, permissions, and privacy sharing. |
| Future institutional partnership tier | Trust-preserving support for schools, programs, or coaching orgs. | Must preserve user ownership and avoid employer-first steering. |

## What Should Remain Free or Low-Friction

- Basic opportunity capture and organization.
- Review-before-save local intake.
- Deterministic COMPASS-style guidance where feasible.
- Basic application workflow tracking.
- Notes, links, and essential search organization.
- Clear export/delete expectations before hosted modes.
- Transparency about AI and product limitations.

The local entitlement model keeps these baseline features enabled locally:

- Opportunity capture.
- Workspace/search-track organization.
- Application workflow.
- Notes, links, reminders, and interviews.
- Deterministic COMPASS where available.
- Local data export visibility.
- Local lifecycle request tracking.
- Local AI usage visibility.

## What May Be Paid Later

- Higher AI usage quotas.
- Advanced artifact lifecycle, comparison, and export convenience.
- Richer analytics after confidence and source basis are stable.
- Power-user workflow scale.
- Advisor/collaboration mode after privacy controls exist.
- Institution-supported plans that keep user data user-controlled.

## What Must Never Be Monetized in the MVP

- Hidden sponsored role prioritization.
- Pay-to-rank listings.
- Selling user attention.
- Employer-funded recommendation steering without disclosure.
- Access to private COMPASS notes, compensation strategy, company commentary,
  or decision rationale.
- Essential organization locked behind expensive tiers before value is proven.
- Auto-apply, auto-send, or unreviewed external automation.

## Explicitly Prohibited

- Employer-sponsored role prioritization as the core model.
- Pay-to-rank listings.
- Selling user attention.
- Hidden sponsored recommendations.
- Steering users toward employer-funded roles without disclosure.
- Locking essential organization behind expensive tiers before value is proven.

## Billing-Provider-Agnostic Design

Future billing design should first define:

- Product tiers.
- Entitlements.
- Usage units.
- Free limits.
- Upgrade/downgrade behavior.
- Cancellation behavior.
- Refund/support expectations.
- Data retention after cancellation.
- How billing state maps to account/workspace access.

Stripe or any other provider integration is future and not in scope.

Layer 11.7 intentionally adds no upgrade button, checkout link, billing
provider, subscription, invoice, payment detail collection, credit wallet, or
paid enforcement.

## Monetization Readiness Gates

- Local workflow value is proven.
- Artifact lifecycle is reviewable, retrievable, and clear.
- AI usage metering and transparency are designed.
- Privacy/data governance is approved.
- Account lifecycle is approved.
- Billing provider and legal/compliance implications are approved.
- No employer-first, marketplace-first, or hidden sponsorship incentives are
  introduced.

