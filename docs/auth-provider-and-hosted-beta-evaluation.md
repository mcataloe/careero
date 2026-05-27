# Auth Provider and Hosted Beta Evaluation

## Purpose

This document evaluates future auth-provider and hosted-beta direction after
Layer 11A, Layer 11B, Layer 11C, and local-first Layer 11.4 through 11.7
foundations.

It is evaluation only. It does not choose a final auth provider, add
hosted auth dependencies, implement OAuth/SSO, create JWTs/passkeys, or claim
hosted readiness.

## 1. Current Local-First Identity Reality

Careero currently supports first-party local email/password registration and
login backed by Argon2id password hashes, server-side session records, and
HttpOnly cookie sessions. It also keeps the seeded local user/workspace for
seed, direct service, and auth-disabled test paths, and has local-first data
export, lifecycle request records, AI usage event metering, and entitlement
boundary reporting.

This is not production authentication. It is not hosted tenant isolation. It
does not provide account recovery, OAuth, SSO, passkeys, email verification,
support/admin access, or production multi-user identity.

## 2. Auth Provider Options

| Option | Fit for Careero | Complexity | Privacy/security implications | Support burden | Vendor lock-in | Local-first compatibility | Hosted beta suitability | Production SaaS suitability | Risks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed auth provider | Strong candidate for private hosted beta because security and recovery controls arrive faster. | Medium. Requires provider integration, callback handling, tenant mapping, and policy review. | User identity data is processed by a vendor; provider configuration becomes security-critical. | Lower than first-party passwords, but support still owns recovery expectations. | Medium to high. | Good if local mode remains separate. | Good after provider/privacy review. | Good if costs, export, deletion, and recovery policies are approved. | Misconfiguration, vendor outage, pricing changes, and overclaiming tenant isolation. |
| First-party email/password | Maximum control and no auth vendor dependency; local foundation already exists. | High for hosted use. Requires recovery, abuse controls, email verification, rate limits, monitoring, and security response beyond the local foundation. | Careero becomes directly responsible for credential security. | High. | Low. | Compatible with local-first operation. | Weak unless security work is prioritized. | Possible but costly. | Security burden is easy to underestimate. |
| OAuth-only social login | Simple user-facing entry and avoids password storage. | Medium. Requires provider apps, callbacks, account linking policy, and recovery rules. | External identity providers learn login activity; user may distrust social auth for career data. | Medium. | Medium. | Compatible if optional for hosted mode only. | Possible for narrow private beta. | Risky as only production option without recovery alternatives. | Provider dependency and account recovery ambiguity. |
| Passkeys/passwordless | Strong security and modern UX. | Medium to high. Requires WebAuthn/passkey flows, fallback recovery, and device-edge-case support. | Good security properties if implemented correctly; recovery policy is critical. | Medium to high during beta. | Low to medium. | Hosted mode only. | Better after auth provider decision. | Strong long-term candidate with support maturity. | Recovery/support complexity and implementation nuance. |
| Local packaged identity | Good for a local packaged app where data stays on one machine. | Low to medium. | Device security is user-managed; no hosted identity claim. | Medium due to local install and data-location support. | Low. | Excellent. | Not sufficient for multi-user hosted beta. | Not sufficient for SaaS. | Could delay necessary hosted auth decisions if treated as equivalent. |
| Staged local-to-cloud account model | Matches Careero's local-first values and lets users opt into hosting later. | High. Requires migration, account linking, data export/import, and conflict handling. | Can preserve trust if migration is explicit and reversible. | Medium to high. | Depends on chosen hosted auth provider. | Excellent if local remains fully useful. | Good after export/lifecycle expectations stabilize. | Good long-term if tenant isolation and support mature. | Data migration mistakes and confusing ownership semantics. |

## 3. Hosted Beta Target Options

| Target | Prerequisites | Already implemented | Blockers | Operational burden | Privacy risk | Support burden | Recommended timing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Local packaged app | Packaging, local database/data-location guidance, backup/restore notes, migration UX. | Local app, local export, local lifecycle requests, local usage events, local entitlement boundaries. | Packaging, backup/restore, upgrade path, and local recovery docs. | Low to medium. | Data stays local by default; device risk remains user-managed. | Medium. | Best near-term hosted alternative after workflow/artifact lifecycle stabilizes. |
| Single-user hosted app | Auth for one owner, hosted DB, secrets management, backup/restore, monitoring, export/delete policy. | Local current-user abstraction, local password auth, and local owner boundaries prepare some service seams. | Account recovery, hosted deployment, backups, monitoring, incident process, and auth hardening. | Medium. | Private career data leaves local device. | Medium. | Optional controlled experiment after explicit user decision. |
| Private hosted beta | Real auth hardening, account recovery, tenant isolation tests, support process, monitoring, export/delete/retention policy, backups. | Local password auth, local export, lifecycle requests, usage metering, entitlement boundaries, readiness reporting. | Production auth hardening, tenant isolation certification, retention enforcement, deletion enforcement, backup/restore, monitoring, support, legal/privacy review. | Medium to high. | High unless access boundaries and logging are hardened. | Medium to high. | After local value and lifecycle expectations are stable. |
| Production multi-tenant SaaS | Hardened auth, authorization, tenant isolation, billing if paid, incident response, support, legal/privacy review, backup/restore. | Local-first foundations only. | Most hosted operations, auth, billing, tenant isolation, compliance, deletion, retention, and support controls. | High. | High. | High. | Future after private beta proves durable value. |

## 4. Required Gates Before Hosted Beta

- Hosted auth provider or hardened first-party auth decision.
- Account recovery decision and support path.
- Tenant isolation tests across workspaces, opportunities, applications,
  artifacts, notes, reminders, interviews, automation logs, lifecycle requests,
  AI usage events, and exports.
- Data export verified in hosted context.
- Deletion and retention policy approved.
- AI usage metering verified.
- Entitlement and billing boundary approved.
- Backup and restore plan.
- Monitoring and logging plan.
- Incident response plan.
- Support process.
- Privacy policy and legal review.
- No hosted collaboration until sharing, revocation, and audit exist.

## 5. Recommendation

Continue local-first productization before choosing a final auth provider.

Recommended staged path:

1. Validate the local export, lifecycle request, usage metering, and entitlement
   foundations through real local use.
2. Stabilize artifact lifecycle and core workflow enough that hosted support
   obligations are worth taking on.
3. Decide whether the next hosted target is a single-user hosted experiment or
   private hosted beta.
4. Choose a hosted auth provider, or explicitly harden first-party auth, only
   after account lifecycle expectations, recovery posture, and data ownership
   policy are stable.
5. Prefer private hosted beta before public production SaaS.
6. Keep employer marketplace and employer-funded flows last.

Do not make a final auth-provider selection from this document alone.

## 6. Human Checkpoints Before Implementation

The user must decide:

- First hosted target.
- Hosted auth provider or hardened first-party auth path.
- Account recovery expectations.
- Deletion and retention policy.
- Support posture.
- Billing timing.
- Privacy/legal review path.
- Whether a single-user hosted experiment is desired before a multi-user beta.
- Whether local packaged app work should precede hosted work.

## Explicit Non-Implementation Statement

This document adds no hosted auth dependency, OAuth flow, SSO provider,
passkey flow, account recovery, hosted tenant isolation claim, billing
integration, or hosted deployment infrastructure.
