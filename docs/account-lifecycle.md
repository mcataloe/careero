# Account Lifecycle

## Purpose

This document defines Layer 11 account lifecycle readiness for Careero. It is
design-only. It does not implement authentication, authorization, account
registration, tenant isolation, data export, or account deletion.

## Current Local-First Account Reality

- Careero uses a seeded local user/workspace model for local development.
- The current local user is not production authentication.
- Existing workspace behavior is local-first and does not prove tenant
  isolation.
- Production account lifecycle, recovery, support, and deletion flows are not
  implemented.

## Production Account Lifecycle Target

A production account model must make it clear who owns each workspace, which
records belong to that owner, which collaborators can see or edit records, and
how the user can export, archive, or delete data.

## Account Creation

Future account creation must define:

- Identity provider or first-party credential strategy.
- Email verification requirements.
- Terms/privacy acknowledgement flow.
- Default workspace creation.
- Whether personal data is required at signup.
- Abuse prevention and rate limits.

Do not select a final auth provider until a future implementation prompt
explicitly approves one.

## Login/Auth Strategy Options

| Option | Fit | Risks | Decision status |
| --- | --- | --- | --- |
| First-party email/password | Direct control and simple product surface. | Password security, recovery, abuse prevention, compliance burden. | Future evaluation. |
| Managed auth provider | Faster hosted beta path with mature security controls. | Vendor lock-in, cost, data-processing review, integration complexity. | Future evaluation. |
| Local-only packaged identity | Good for local beta or single-user app. | Not sufficient for hosted SaaS or collaboration. | Possible local beta path. |
| OAuth-only social login | Lower password burden. | Provider dependency, account recovery edge cases, user trust concerns. | Future evaluation. |

## Workspace Ownership

- Every workspace/search track must have an account owner in hosted modes.
- Collaboration must be explicit, scoped, revocable, and audited.
- Workspace ownership transfer is future and should not be assumed.
- Deleting an account must define what happens to owned workspaces,
  collaborators, exports, and logs.

## Tenant Isolation Requirements

Hosted modes require:

- Account-scoped workspace access checks.
- Server-side authorization on every user data request.
- Tests proving users cannot access other users' records.
- Isolation for Opportunity/Role-backed records, applications, artifacts,
  notes, reminders, interviews, analytics, and automation logs.
- Operational logging that avoids leaking private content.

## Authorization Boundaries

Future permissions should separate:

- Owner.
- Optional collaborator/commenter.
- Optional advisor/reviewer.
- Future admin/support access.
- Future employer-facing share recipient.

Employer-side or marketplace access must not reuse internal user permissions.
It requires explicit user-controlled sharing design.

## Account Deletion

Production deletion design must define:

- Full account deletion.
- Workspace-level deletion.
- Selective source/opportunity/artifact deletion.
- Audit log retention or anonymization.
- Deletion timing and recovery window.
- Local exports and files outside app control.
- Provider-side AI/billing data implications.

## Data Export

Future export must include:

- Account/profile data.
- Workspaces/search tracks.
- Resume/profile sources and versions.
- Opportunities and Role-backed compatibility identifiers where relevant.
- STRIDE evaluations.
- Generated artifacts and export metadata.
- Applications, state history, notes, reminders, interviews, and links.
- Automation suggestions and approval logs.
- User-visible analytics/insights and their basis.

Export format is future. JSON plus user-readable Markdown is a likely candidate
but not approved here.

## Workspace Archival

Workspace archival should preserve historical search value without implying
active pursuit. Future design should define whether archived workspaces continue
to appear in strategy, analytics, exports, and AI grounding.

## Recovery/Reset

Future hosted modes need:

- Password or login recovery.
- Account lockout handling.
- Workspace restore behavior.
- Backup restore expectations.
- Support process and audit trail.

## Retention Windows

Retention windows are TBD and must be approved before private hosted beta.
Separate windows may be needed for active records, archived records, deleted
records, operational logs, AI run metadata, and billing records.

## Audit Expectations

Audit logs should capture lifecycle events and security-relevant actions without
storing secrets, API keys, raw prompts, raw resumes, or private notes in general
operational logs.

## Private Beta Requirements

- Real auth.
- Account-scoped workspaces.
- Server-side authorization checks.
- Export/delete design approved.
- Privacy and retention policy approved.
- Operational monitoring and support process.
- AI usage/cost limits.

## Production SaaS Requirements

- Hardened auth and recovery.
- Tested tenant isolation.
- Backup/restore.
- Incident response.
- User-visible privacy controls.
- Data export/delete implementation.
- Billing only after provider and policy approval.
- Monitoring, logging, cost controls, and support coverage.

## Stop Conditions Before Implementation

Stop before account implementation if the work would require choosing an auth
provider, adding auth dependencies, changing permission behavior, introducing
tenant isolation code, changing sensitive-data handling, or enabling external
account linking without a fresh approved scope.
