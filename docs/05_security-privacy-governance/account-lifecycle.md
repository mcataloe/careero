# Account Lifecycle

Status: Active  
Doc Type: Governance  
Layer: Layer 11  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/05_security-privacy-governance/auth-provider-and-hosted-beta-evaluation.md
- docs/05_security-privacy-governance/privacy-data-governance.md

## Purpose

This document defines Layer 11 account lifecycle readiness for Careero. It is
design-first and partly implemented for local auth. It does not implement
production auth hardening, hosted authorization, tenant isolation certification,
account recovery, data export, or account deletion.

## Current Local-First Account Reality

- Careero now supports first-party local email/password registration and
  login backed by Argon2id password hashes and HttpOnly cookie sessions.
- Google and LinkedIn SSO appear as disabled login-page placeholders only.
  OAuth is not implemented and no provider configuration exists.
- The seeded local user/workspace model remains for seed, direct service, and
  auth-disabled test paths. It is not assigned a default password.
- Layer 11B adds a local-first current-user context abstraction so services can
  resolve the seeded user through one injectable boundary instead of scattering
  direct default-user lookups.
- Workspace, role/opportunity, and application services now have clearer
  owner-scoped service checks for local/test execution.
- Existing workspace behavior is local-first and does not prove tenant
  isolation.
- Production account lifecycle, recovery, support, and deletion flows are not
  implemented.
- Layer 11.4 adds a local-first JSON data export for the resolved current local
  user. This is a local owner export only and does not imply hosted account
  export, production auth, cloud backup, account recovery, deletion, retention
  enforcement, or legal compliance certification.
- Layer 11.5 adds local account lifecycle request tracking. The request records
  are local audit records for export, deletion, workspace/source/artifact
  deletion, and retention-review intent. They do not delete, anonymize, recover,
  or submit hosted support work.
- No hosted auth provider has been selected. No OAuth, JWT, password recovery,
  email verification, MFA, support impersonation, or hosted collaboration
  account behavior has been added.
- Layer 11.8 evaluates auth-provider and hosted-beta options while keeping the
  final provider choice deferred. It adds no hosted provider dependency, OAuth,
  JWT, account recovery, or passkey implementation.
- Layer 11A readiness reporting surfaces this status in the backend and
  Settings page, but it does not add account controls.

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
| First-party email/password | Direct control and simple product surface. | Password security, recovery, abuse prevention, compliance burden. | Local foundation implemented; production hardening remains future. |
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

Layer 11B prepares these boundaries locally by making current-user resolution
injectable and by adding service-level cross-user tests. This is boundary prep
only. It is not tenant isolation certification for hosted SaaS.

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

Layer 11.5 deletion requests are non-destructive. Recording an
`account_deletion` request requires explicit confirmation and returns language
that the request was recorded, data has not been deleted, and deletion
enforcement remains future.

Layer 11.4 adds `GET /api/data-export/local` and a Settings page download
control for local JSON export. It does not add hosted export queues, cloud
download links, deletion controls, deletion jobs, retention enforcement, or
account lifecycle APIs.

Layer 11.5 adds:

- `POST /api/account/lifecycle-requests`
- `GET /api/account/lifecycle-requests`
- `POST /api/account/lifecycle-requests/{request_id}/cancel`

These endpoints are local-first request tracking only. They use the resolved
current local user, record privacy-safe activity-log events, and do not perform
destructive deletion or anonymization.

## Data Export

Future export must include:

- Account/profile data.
- Workspaces/search tracks.
- Resume/profile sources and versions.
- Opportunities and Role-backed compatibility identifiers where relevant.
- COMPASS evaluations.
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

Future hosted modes still need:

- Password or login recovery.
- Email verification and reset-token lifecycle.
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

Layer 11.5 lifecycle request activity logs include request type/status/target
metadata and explicitly avoid raw request reasons or private content.

## Private Beta Requirements

- Production-hardened auth and account recovery.
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
- Hosted data export/delete implementation.
- Billing only after provider and policy approval.
- Monitoring, logging, cost controls, and support coverage.

## Stop Conditions Before Implementation

Stop before account implementation if the work would require choosing an auth
provider, adding auth dependencies, changing permission behavior, introducing
tenant isolation code, changing sensitive-data handling, or enabling external
account linking without a fresh approved scope.

Layer 11B does not remove those stop conditions. Hosted collaboration, advisor
accounts, employer/recruiter access, and support/admin access remain blocked
until production auth, authorization, revocation, audit, privacy, and lifecycle
work is explicitly scoped.

