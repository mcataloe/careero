# Productization Readiness

## Purpose

This is the primary Layer 11 source of truth for Careero productization readiness.
Layer 11 currently means readiness and boundary design, not production launch.

Careero remains a local-first career operations application. It is not
production-ready.

## Current Status

Careero has meaningful local workflow value across intake, STRIDE evaluation,
artifact generation foundations, application workflow, analytics, automation
guardrails, and read-only career strategy synthesis.

It does not yet have production authentication, production authorization,
tenant isolation, billing, hosted deployment, account deletion/export,
retention enforcement, or production privacy controls. Existing seeded local
user behavior is not production auth.

## Productization Stages

| Stage | Definition | Current fit |
| --- | --- | --- |
| Local POC | Developer-run local app proving the core job-seeker workflow. | Current primary stage. |
| Local beta | Local-first app stable enough for repeated personal use with clear data boundaries and recovery notes. | Near-term target after workflow and artifact lifecycle stabilization. |
| Private hosted beta | Limited hosted environment for invited users with auth, privacy controls, tenant isolation, support process, and operational monitoring. | Future. |
| Production SaaS | Public paid or free hosted product with production-grade privacy, security, operations, billing, support, and lifecycle controls. | Future. |
| Future marketplace/employer-side mode | Optional employer, recruiter, or marketplace capabilities with explicit user-controlled sharing and strict disclosure. | Future and last. |

## Stage Gates

| Gate | Local POC | Local beta | Private hosted beta | Production SaaS | Marketplace/employer-side |
| --- | --- | --- | --- | --- | --- |
| Core workflow | Manual local workflow works. | Application, reminders, artifacts, analytics, and strategy are coherent. | Hosted workflows are stable for invited users. | Public workflows are supportable and observable. | User-side workflow remains the product center. |
| Identity | Seeded local user is acceptable. | Local user assumptions are documented. | Real auth and account recovery are implemented. | Auth is hardened and supportable. | Sharing identity model is explicit and user-controlled. |
| Authorization | Local-only boundary. | No false tenant claims. | Workspace/account authorization is enforced. | Tenant isolation is tested and monitored. | Employer access is scoped, revocable, and audited. |
| Privacy | Local data expectations documented. | Data classes, export, deletion, and retention designs exist. | Export/delete and retention controls are implemented. | Privacy controls are operationally supportable. | No employer visibility without explicit user sharing. |
| AI governance | Source-grounded AI and TruthGuard checks. | Usage transparency and reviewability are clear. | Usage metering and cost controls are implemented. | Abuse, cost, and quality controls are monitored. | AI never sells attention or hides sponsored steering. |
| Deployment | Local scripts only. | Local beta packaging/runbook can be documented. | Hosted deployment runbook exists. | Backup, restore, rollback, monitoring, incident process exist. | Additional operational and compliance review required. |
| Monetization | None. | Pricing principles only. | Provider-agnostic billing design may be validated. | Billing provider may be implemented after approval. | Employer money cannot distort user recommendations. |

## Explicit Production Blockers

- Production authentication is not implemented.
- Production authorization and tenant isolation are not implemented.
- Data export, account deletion, and retention enforcement are not implemented.
- Billing, subscriptions, invoices, checkout, and payment flows are not implemented.
- AI usage metering and durable cost controls are not implemented.
- Production deployment architecture is not implemented.
- Artifact lifecycle UX remains incomplete.
- Reminder API/UI reconciliation remains a production readiness blocker.
- Opportunity remains Role-backed internally.
- External integrations and external automation are intentionally disabled.

## What Can Be Built Now

- Docs-first productization readiness.
- Privacy, data governance, account lifecycle, deployment, cost-control, and
  monetization boundaries.
- Local beta runbooks and non-destructive readiness checklists.
- User-facing clarity that Careero is local-first and not production-ready.
- Future implementation prompts that preserve job-seeker-first trust.

## What Must Stay Future

- Production auth and account registration.
- Production authorization and tenant isolation implementation.
- Hosted production deployment.
- Billing provider integration, including Stripe or equivalent providers.
- Subscriptions, checkout, invoices, and payment flows.
- OAuth token storage, background sync, external account linking, and external
  account mutation.
- Auto-apply, auto-send, batch external actions, and unreviewed automation.
- Marketplace, employer-side, recruiter-side, sponsored placement, or
  pay-to-rank work.

## Relationship to Layers 1-10

Layer 11 depends on Layers 1-10 becoming truthful, stable, and reviewable:

- Layer 1 must eventually add production identity, authorization, secrets, and environment hardening.
- Layer 2 must keep source material reviewable and provenance-aware.
- Layer 3 and Layer 6 must keep generated artifacts grounded, traceable, reviewable, and separated from private strategy.
- Layer 4 reminders and workflow records must be reconciled before production readiness.
- Layer 5 analytics must explain confidence and avoid overstating weak signals.
- Layer 7 must preserve Opportunity-facing compatibility while Role-backed persistence remains explicit.
- Layer 8 must keep local/manual integrations first and defer OAuth/cloud sync.
- Layer 9 must keep automation suggestion-first, review-first, and audit-first.
- Layer 10 must remain advisory and source-grounded.

## Relationship to Layers 12-13

Layer 12 local-only advisor packet preview/export can exist as owner-visible,
redacted scaffolding. Hosted advisor/collaboration mode still requires
privacy-scoped sharing, account roles, comment boundaries, revocation, account
lifecycle, and tenant isolation design before implementation.

Layer 13 marketplace/employer-side exploration remains last. It requires strict
user control, disclosure, auditability, and separation from core recommendation
ranking. No employer-side visibility exists today.

## Exit Criteria Before Productization Implementation

- Local workflow value is proven through repeated use.
- Layer 4 reminder/workflow reconciliation is resolved.
- Layer 6 artifact lifecycle is mature enough to support paid or shared artifact workflows.
- Privacy/data governance decisions are approved.
- Account lifecycle and auth/provider direction are approved.
- Deployment target and operational requirements are approved.
- AI usage metering and cost controls are designed and approved.
- Monetization boundaries are approved and remain job-seeker-first.
- A fresh LEAP Recon confirms implementation scope and non-goals.

## Productization Stance

Layer 11 readiness docs define gates and boundaries so future agents do not
confuse local-first readiness with production readiness. Implementation remains
future until the blockers above are resolved.
