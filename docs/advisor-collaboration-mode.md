# Advisor Collaboration Mode

## Purpose

Layer 12 defines how Careero can eventually support trusted external help while
preserving privacy, user ownership, explicit consent, scoped visibility,
revocation, and auditability.

This document is readiness and design guidance only. It does not implement
hosted collaboration, advisor accounts, invitations, external sharing, public
links, comments, production auth, tenant isolation, or employer/recruiter
visibility.

Advisor collaboration must keep Careero job-seeker-first. STRIDE remains
advisory, source-grounded, explainable, and never deterministic truth. Private
strategy, internal fit evaluation, private notes, compensation reasoning,
recruiter intelligence, and hidden decision rationale must not become externally
visible by default.

## Current Status

Layer 12 status: future / readiness design started.

Careero currently has:

- No production auth.
- No tenant isolation.
- No persistent collaborator accounts.
- No hosted sharing.
- No public links.
- No comment APIs.
- No external send.
- No employer or recruiter visibility.

Any future implementation must start from a fresh LEAP Recon and explicit
approval for the relevant implementation surface.

## Core Rules

- Nothing is shared by default.
- The user must explicitly select what leaves the private workspace.
- Private strategy is separate from shareable material.
- Advisor-facing packets must be redacted by default.
- Employer-facing artifacts must never include internal STRIDE analysis, ATS
  risk notes, compensation strategy, company commentary, private notes, or
  private decision rationale.
- Advisor-facing materials may include sensitive analysis only if the user
  explicitly selects it in a future approved flow.
- No collaboration feature may bypass TruthGuard or source-grounding.
- No external sharing is allowed until auth, authorization, tenant isolation,
  revocation, audit, and privacy controls exist.
- Layer 12 must not introduce employer-first, marketplace-first,
  automation-first, sponsored-placement, or pay-to-rank behavior.

## Advisor Personas

| Persona | Purpose | Boundaries |
| --- | --- | --- |
| Career coach | Help the user reflect on positioning, opportunity fit, search behavior, and next actions. | Must not receive private strategy, compensation reasoning, or source material unless explicitly selected by the user in a future approved flow. |
| Resume reviewer | Review generated resume drafts and user-selected context. | Must see artifact lifecycle and truthfulness warnings; should not receive STRIDE rationale or raw source material by default. |
| Spouse/family advisor | Provide trusted personal feedback on tradeoffs, timing, commute, stress, and life fit. | Default packet should be narrow, plain-language, and redacted. |
| Mentor | Advise on role scope, career trajectory, negotiation posture, or interview preparation. | Should receive only user-selected context and questions. |
| Internal self-review persona | Let the user preview what an advisor packet would contain before anything leaves the workspace. | Safe near-term direction because it can stay local-only and owner-visible. |

Future recruiter or employer visibility is out of scope for Layer 12 and is
reserved for Layer 13 or later. Employer-side access must use a separate trust,
incentive, disclosure, and user-consent review.

## Shareable and Private Data Classes

Default visibility uses the future packet viewpoint: what an advisor packet
would include unless the user explicitly changes it in an approved flow.

| Data class | Default visibility | Can be included by user selection? | Required redaction or warning | Notes |
| --- | --- | --- | --- | --- |
| Opportunity title/company/basic role fields | Packet-eligible summary | Yes | Warn if company/source details reveal sensitive search activity. | Basic opportunity context is the safest default packet candidate. |
| Raw job description | Private | Yes, future approved flow only | Warn about proprietary/confidential posting text and source leakage. | Raw source content should not be included by default. |
| Parsed opportunity fields | Packet-eligible summary | Yes | Show parse confidence and reviewed/unreviewed status where available. | Prefer selected structured fields over raw posting text. |
| Application workflow state | Packet-eligible summary | Yes | Mark current state as user-maintained and local. | Current state can help an advisor understand timing. |
| Application state history | Private by default | Yes | Redact timestamps or sensitive event details when needed. | History can expose decision rationale and search behavior. |
| Generated resume artifact | Packet-eligible if user selects it | Yes | Must carry lifecycle, source-grounding, and truthfulness warnings until lifecycle is mature. | Drafts must not be treated as approved or submitted. |
| Generated cover-letter artifact | Packet-eligible if user selects it | Yes | Must carry lifecycle, source-grounding, and truthfulness warnings until lifecycle is mature. | Drafts must not be treated as approved or submitted. |
| Artifact lifecycle status | Packet-eligible summary | Yes | Warn when artifact is draft, unreviewed, unapproved, or not submitted. | Lifecycle status should travel with any selected artifact. |
| STRIDE score | Private by default | Yes, future approved flow only | Explain STRIDE is advisory, not deterministic truth. | A score without explanation can be misleading. |
| STRIDE explanation | Private by default | Yes, future approved flow only | Redact internal rationale, ATS notes, compensation strategy, and company commentary unless explicitly selected. | Must remain source-grounded and explainable. |
| ATS risk notes | Private by default | Yes, future approved flow only | Strong warning that ATS notes are internal strategy and not employer-facing. | Must never be included in employer-facing artifacts. |
| Compensation targets | Private by default | Yes, future approved flow only | Strong warning for negotiation sensitivity. | Excluded by default even for trusted advisors. |
| Compensation strategy | Private by default | Yes, future approved flow only | Strong warning; require explicit selection and preview. | Must never be employer-facing by default. |
| Private user notes | Private by default | Yes, future approved flow only | Require per-note selection and visible redaction status. | Advisor comments must remain separate from private notes. |
| Recruiter/source/contact metadata | Private by default | Yes, future approved flow only | Redact names, emails, phone numbers, referral details, and relationship context by default. | Recruiter intelligence is excluded by default. |
| Interview notes | Private by default | Yes | Redact interviewer names, contact details, and sensitive personal impressions. | May be useful for mentor prep only after user review. |
| Reminders | Private by default | Yes | Warn when reminder text reveals private priorities or deadlines. | Current reminder reconciliation remains incomplete. |
| External links | Packet-eligible if selected | Yes | Warn before exposing private docs, portals, tracking URLs, or account-specific links. | Links should be user-selected, not bulk-shared. |
| Career strategy synthesis | Private by default | No by default; future approved flow only | Strong warning that strategy is internal, advisory, and source-derived. | Excluded by default from advisor packets. |
| Resume/profile source material | Private by default | No by default; future approved flow only | Strong warning for raw personal data. | Source material is for grounding, not sharing by default. |
| AI prompts/outputs | Private by default | Yes, future approved flow only | Redact raw prompts, system instructions, private notes, and source text. | Store/share only if an audit/debug use case is explicitly approved. |
| Activity logs | Private by default | No by default; future approved flow only | Redact internal metadata and private content references. | Logs are audit records, not shareable domain truth. |
| Automation suggestions and approval logs | Private by default | No by default; future approved flow only | Strong warning; never expose hidden internal metadata or approval rationale by default. | Layer 9 remains suggestion-first with external actions disabled. |

Safe defaults:

- Basic opportunity, application, and artifact summaries may be packet-eligible.
- Private notes are excluded by default.
- Compensation targets and compensation strategy are excluded by default.
- Internal STRIDE explanation and ATS risk notes are excluded by default.
- Raw source materials are excluded by default.
- Recruiter/contact details are excluded by default.
- Career strategy synthesis is excluded by default.
- Any included generated artifact must carry lifecycle and truthfulness warnings
  until artifact lifecycle is mature.

## Advisor Packet Model

A future Advisor Packet is a user-selected, read-only, source-grounded bundle
for trusted review. It is not a shared workspace and not a public link.

It may eventually include:

- Opportunity summary.
- Application status summary.
- Selected generated artifacts.
- Selected notes or user-authored context.
- Selected questions for the advisor.
- Selected links.
- Explicit warnings about draft or unreviewed artifacts.
- Explicit redaction status.

It must not include by default:

- Full private notes.
- Compensation strategy.
- STRIDE internal rationale.
- ATS risk notes.
- Recruiter intelligence.
- Source resume/profile material.
- Career strategy synthesis.
- Automation approval logs.
- Hidden internal metadata.

The safest near-term packet behavior, if separately approved later, is local-only
owner preview/export with no hosted access, no invitations, no external send, and
no persistent collaborator records.

## Permission Model: Design Only

Future roles are conceptual only until production auth, account lifecycle,
server-side authorization, and tenant isolation are implemented.

| Role | Conceptual intent | Implementation status |
| --- | --- | --- |
| Owner | The job seeker who controls the workspace, packet contents, sharing, revocation, and deletion. | Future production implementation required. |
| Viewer | Can read a scoped packet or selected records. | Design only. |
| Commenter | Can leave comments on scoped packet material without editing user data. | Design only. |
| Reviewer | Can review selected artifacts or packet contents and provide structured feedback. | Design only. |
| Coach | Can receive broader user-selected context for coaching discussions. | Design only. |
| Future support/admin | Operational support role, if ever needed. | Not part of Layer 12 unless separately approved. |

These roles do not exist in code and must not be treated as enforced
permissions.

## Comment-Only Review Model: Design Only

Advisor comments must be separate from private user notes. They must not merge
into the user's private notes, internal rationale, STRIDE explanations, or
artifact content without explicit user action.

Comments require identity, permission, visibility rules, revocation behavior,
retention policy, and audit before implementation. This Build Unit does not
implement comments, comment APIs, comment UI, notifications, or shared review
threads.

## Invitation, Access, Revocation, and Audit: Future Only

Future collaboration requires:

- Explicit invitation.
- Scoped packet, workspace, or opportunity access.
- Expiration.
- Revocation.
- Audit log of access and comments.
- No public anonymous access by default.
- No employer/recruiter visibility.
- Server-side authorization checks on every user-data request.
- Operational logs that do not leak private content.

Public links, anonymous packet access, email invitations, OAuth, external account
sync, and production auth/provider choices are outside this Build Unit.

## Relationship to Existing Layers

| Layer | Relationship to Layer 12 |
| --- | --- |
| Layer 0 Product Foundation | Collaboration must preserve job-seeker-first control, AI as advisor, source grounding, review-before-send, no-auto-apply, humane UX, and marketplace-last posture. |
| Layer 1 Local Platform Foundation | Hosted collaboration depends on real auth, tenant isolation, server-side authorization, and account ownership. Seeded local users are not production identity. |
| Layer 2 Intake, Parsing & Grounding | Resume/profile sources, raw job descriptions, and source versions are private grounding material by default. Packets should prefer reviewed summaries over raw sources. |
| Layer 3 STRIDE + Artifact Foundation | STRIDE and artifacts must remain source-grounded, explainable, reviewable, and separated from private strategy. TruthGuard cannot be bypassed. |
| Layer 4 Application Workflow | Application state, selected timeline facts, links, reminders, interviews, and user-authored context are packet candidates only after review and redaction. |
| Layer 5 Workflow Intelligence / Insights | Analytics and confidence signals must not overclaim. Insights should disclose basis and uncertainty before any advisor-visible use. |
| Layer 6 Advanced STRIDE + Artifact Lifecycle | Artifact lifecycle maturity is required before shared artifact workflows can be trusted. Draft/unreviewed warnings must travel with artifacts. |
| Layer 7 Opportunity Model Strategy | Layer 12 must stay compatible with Opportunity-facing language while persistence remains Role-backed. No destructive Role-to-Opportunity migration belongs in Layer 12. |
| Layer 8 Integrations | Layer 12 cannot introduce cloud sync, OAuth, external send, Gmail/Outlook, calendar, browser/share, or public-link behavior without separate approval. |
| Layer 9 Automation Guardrails | Collaboration cannot weaken suggestion-first, review-first, audit-first automation. No auto-send, auto-apply, batch approvals, or external mutation. |
| Layer 10 Advanced Search Tracks / Career Strategy | Strategy synthesis is read-only, advisory, source-grounded, and private by default. It is not packet-visible unless a future approved flow explicitly allows it. |
| Layer 11 Productization / Deployment / Monetization | Hosted collaboration is blocked by production auth, authorization, tenant isolation, privacy controls, export/delete, retention, revocation, audit, and account lifecycle. |
| Layer 13 Marketplace / Employer-Side Exploration | Employer/recruiter visibility remains separate and last. Layer 12 must not create a back door into employer-side sharing. |

## Safe Build Units

| Build Unit | Status |
| --- | --- |
| 12A Advisor collaboration strategy doc | Current docs-first Build Unit. |
| 12B Collaboration data-class/redaction matrix | Design-only, may refine this document or become a dedicated design doc. |
| 12C Permission model design | Design-only. |
| 12D Advisor packet model design | Design-only. |
| 12E Local-only packet preview/export scaffolding | Blocked until explicitly approved in a separate prompt. |
| 12F Comment-only workflow design | Design-only; implementation blocked. |
| 12G Revocation/audit design | Design-only; implementation blocked until account/auth decisions exist. |
| 12H UI trust copy | Design-only, no implementation without approval. |
| Hosted collaboration implementation | Blocked. |
| Advisor accounts/invitations | Blocked. |
| Employer/marketplace sharing | Blocked / Layer 13. |

## Stop Conditions Before Implementation

Stop before coding if a future prompt requires:

- Production auth.
- Tenant isolation.
- New permission model.
- Public links or external sharing.
- Email sending.
- OAuth or external account integration.
- Comments API.
- Artifact lifecycle changes.
- Exposing private STRIDE or compensation data.
- Employer/recruiter visibility.
- Destructive Role-to-Opportunity migration.
- New dependencies or migrations.
- Backend or frontend implementation not explicitly approved as a separate
  Build Unit.

## Product Stance

Layer 12 is user-controlled trusted help, not employer visibility.

The safest near-term implementation is docs/design and, only after a separate
approval prompt, possibly local-only packet preview/export. Hosted collaboration
requires a fresh LEAP Recon and explicit approval after production auth,
authorization, tenant isolation, privacy controls, revocation, audit, and
account lifecycle are implemented.
