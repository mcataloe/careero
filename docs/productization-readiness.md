# Productization Readiness

## Purpose

This is the primary Layer 11 source of truth for Careero productization readiness.
Layer 11 currently means readiness and boundary design, not production launch.

Careero remains a local-first career operations application. It is not
production-ready.

## Current Status

Careero has meaningful local workflow value across intake, COMPASS evaluation,
artifact generation foundations, application workflow, analytics, automation
guardrails, and read-only career strategy synthesis.

Layer 11A adds a local-first productization readiness surface:

- Backend endpoint: `GET /api/productization/readiness`.
- Frontend surface: Settings page Product readiness panel.
- Scope: reports environment, readiness stage, local-first status, local
  workflow indicators, coarse database health, AI feature flags, auth/tenant
  boundary prep, billing, export/delete, retention, usage metering, deployment,
  hosted collaboration, marketplace status, and known blockers.
- Safety boundary: the response must not expose secrets, database URLs, OpenAI
  API keys, private user data, resumes, notes, prompts, job descriptions,
  artifacts, or compensation targets.

Layer 11A is not production deployment. It adds reporting only.

It now has a local-first first-party username/password auth foundation:
registration, login with username or email, Argon2id password hashing,
server-side session records, HttpOnly cookie sessions, `/api/auth/me`, logout,
and frontend app-route protection. Google and LinkedIn SSO are visible disabled
placeholders only. OAuth is not implemented.

It does not yet have production auth hardening, account recovery, production
authorization, hosted tenant isolation certification, billing, hosted
deployment, account deletion/export, retention enforcement, or production
privacy controls. Existing seeded local user behavior is not a public password
or hosted auth path.

Layer 11B adds local-first current-user boundary prep: a small injectable
current-user context resolves the seeded local user by default, and selected
workspace, role/opportunity, and application services now make owner-scoped
service checks more explicit. This preserves local operation and does not
implement production auth.

Layer 11.4 adds a local-first data export foundation:

- Backend endpoint: `GET /api/data-export/local`.
- Frontend surface: Settings page Local data export panel.
- Scope: returns a structured JSON package for records owned by the resolved
  current local user, including user-owned private content where appropriate.
- Safety boundary: no cloud storage, public links, hosted account export,
  production account support, legal compliance certification, runtime secrets,
  database URLs, API keys, provider credentials, or unrelated users' records.

Layer 11.5 adds local-first account lifecycle request tracking:

- Backend endpoints: `POST /api/account/lifecycle-requests`,
  `GET /api/account/lifecycle-requests`, and
  `POST /api/account/lifecycle-requests/{request_id}/cancel`.
- Frontend surface: Settings page Account lifecycle requests panel.
- Scope: records local request/audit rows for data export, deletion, targeted
  deletion, and retention-review intent.
- Safety boundary: deletion requests are non-destructive and explicitly state
  that data has not been deleted and deletion enforcement remains future.

Layer 11.6 adds local-first AI usage metering:

- Backend endpoint: `GET /api/usage/ai`.
- Frontend surface: Settings page AI usage panel.
- Scope: records provider-agnostic local usage events for role parsing, COMPASS
  enrichment, resume artifacts, and cover-letter artifacts.
- Safety boundary: events contain safe metadata only and do not persist raw
  prompts, resumes, private notes, job descriptions, provider credentials,
  database URLs, API keys, or billing events.

Layer 11.7 adds a local-first entitlement boundary model:

- Backend endpoint: `GET /api/entitlements/current`.
- Frontend surface: Settings page Local plan panel.
- Scope: reports the `local_free` plan, enabled local baseline features,
  future-only paid/collaboration/cloud features, and monetization guardrails.
- Safety boundary: no Stripe, checkout, subscriptions, invoices, payment
  details, credit wallet, upgrade buttons, or paid enforcement.

Layer 11.8 adds
[`auth-provider-and-hosted-beta-evaluation.md`](auth-provider-and-hosted-beta-evaluation.md).
This is evaluation only. It does not select a hosted auth provider, add OAuth
dependencies, implement SSO/account recovery, or claim hosted readiness.

## Productization Stages

| Stage | Definition | Current fit |
| --- | --- | --- |
| Local POC | Developer-run local app proving the core job-seeker workflow. | Current primary stage. |
| Local beta | Local-first app stable enough for repeated personal use with clear data boundaries and recovery notes. | Blocked until workflow, artifact lifecycle, and readiness gates are clearer. |
| Private hosted beta | Limited hosted environment for invited users with auth, privacy controls, tenant isolation, support process, and operational monitoring. | Future. |
| Production SaaS | Public paid or free hosted product with production-grade privacy, security, operations, billing, support, and lifecycle controls. | Future. |
| Future marketplace/employer-side mode | Optional employer, recruiter, or marketplace capabilities with explicit user-controlled sharing and strict disclosure. | Future and last. |

## Stage Gates

| Gate | Local POC | Local beta | Private hosted beta | Production SaaS | Marketplace/employer-side |
| --- | --- | --- | --- | --- | --- |
| Core workflow | Manual local workflow works. | Application, reminders, artifacts, analytics, and strategy are coherent. | Hosted workflows are stable for invited users. | Public workflows are supportable and observable. | User-side workflow remains the product center. |
| Identity | Local username/password auth is available; seeded local user remains for seed/test paths. | Local user and bootstrap assumptions are documented. | Hardened auth and account recovery are implemented. | Auth is hardened and supportable. | Sharing identity model is explicit and user-controlled. |
| Authorization | Local-only boundary. | No false tenant claims. | Workspace/account authorization is enforced. | Tenant isolation is tested and monitored. | Employer access is scoped, revocable, and audited. |
| Privacy | Local data expectations documented. | Data classes, export, deletion, and retention designs exist. | Export/delete and retention controls are implemented. | Privacy controls are operationally supportable. | No employer visibility without explicit user sharing. |
| AI governance | Source-grounded AI and TruthGuard checks. | Usage transparency and reviewability are clear. | Usage metering and cost controls are implemented. | Abuse, cost, and quality controls are monitored. | AI never sells attention or hides sponsored steering. |
| Deployment | Local scripts only. | Local beta packaging/runbook can be documented. | Hosted deployment runbook exists. | Backup, restore, rollback, monitoring, incident process exist. | Additional operational and compliance review required. |
| Monetization | None. | Pricing principles only. | Provider-agnostic billing design may be validated. | Billing provider may be implemented after approval. | Employer money cannot distort user recommendations. |

## Explicit Production Blockers

- Production auth hardening, account recovery, email verification, MFA, and SSO are not implemented.
- Production authorization and tenant isolation are not implemented.
- Layer 11B service-level ownership checks are local boundary prep only and do
  not certify hosted tenant isolation.
- Local-first JSON data export exists for the current local user.
- Hosted account export, destructive account deletion, anonymization, and
  retention enforcement are not implemented.
- Credits, paid billing, quota enforcement, model marketplaces, and production
  cost controls are not implemented.
- Entitlement boundaries exist locally, but live billing and paid plan
  enforcement are not implemented.
- Billing, subscriptions, invoices, checkout, and payment flows are not implemented.
- AI usage metering and durable cost controls are not implemented.
- Production deployment architecture is not implemented.
- Layer 11A readiness reporting exists, but it is only a status surface.
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
- Local readiness endpoint/UI improvements that continue to avoid secrets and
  private content.
- Local-first current-user context and service-level boundary tests that prepare
  future auth injection without selecting an auth provider.
- Local-first owner export surfaces that avoid cloud storage and runtime
  secrets.
- Local-first AI usage visibility that avoids private content and billing
  claims.
- Future implementation prompts that preserve job-seeker-first trust.

## What Must Stay Future

- Production auth hardening, account recovery, and SSO.
- Hosted auth-provider selection and OAuth dependencies.
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

Layer 11B does not unblock hosted collaboration, advisor accounts, employer
access, recruiter access, or support/admin access.

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

Layer 11 readiness docs and the Layer 11A readiness endpoint/UI define and
report gates so future agents do not confuse local-first readiness with
production readiness. Production implementation remains future until the
blockers above are resolved.
