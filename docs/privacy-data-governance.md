# Privacy and Data Governance

## Purpose

This document defines Careero's Layer 11 privacy and data governance readiness
model. It is design guidance only. It does not claim legal compliance, implement
retention enforcement, or create production privacy controls.

Careero is job-seeker-first. User source material remains the ground truth, and
no employer-side visibility exists without future explicit user-controlled
sharing design.

## Core Rules

- Employer-facing artifacts must never include internal COMPASS notes, ATS risk
  notes, compensation strategy, company commentary, or private decision
  rationale.
- AI outputs must remain traceable, reviewable, and grounded in user-provided
  source material, opportunity content, or stored Careero records.
- No employer-side visibility is allowed without future explicit
  user-controlled sharing design.
- Automation remains review-before-send, no-auto-apply, and external actions
  disabled.
- Monetization must not use private job-search data to steer hidden sponsored
  recommendations or sell user attention.

## Data Classification Table

| Data class | Owner | Sensitivity | Retention expectation | Export behavior | Deletion behavior | Audit/logging expectation | AI use | Monetization use |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Account/profile data | User | High | Retain while account/workspace exists; production window TBD. | Export account profile fields. | Delete or anonymize on account deletion after approved retention window. | Log account lifecycle events without secrets. | Only for personalization if explicitly scoped. | May support account tier eligibility, not targeting. |
| Workspace/search-track data | User | Medium | Retain while active or archived. | Export workspace/search-track records. | Delete with workspace or account deletion. | Log create/update/archive. | Yes, for workspace-scoped insights. | Aggregate plan limits only. |
| Resume/profile sources | User | High | Retain while user keeps the source/version. | Export raw and normalized source text plus metadata. | Delete all versions and derived references when requested, subject to approved audit policy. | Log source lifecycle without raw text in logs. | Yes, only as grounding source. | Not sold, ranked, or shared. |
| Source material versions | User | High | Retain version history until deleted or pruned by future policy. | Export version text, hashes, labels, and timestamps. | Delete versions or all source lineage when requested. | Log version lifecycle and hashes, not raw content. | Yes, as traceable grounding. | Not used for hidden monetization. |
| Raw job descriptions | User | Medium | Retain with target opportunity. | Export raw posting text and source metadata. | Delete with opportunity/workspace/account. | Log hashes/source IDs, not raw text. | Yes, for parsing, COMPASS, artifacts, and strategy. | May inform user-visible usage value, not sponsored ranking. |
| Parsed opportunity fields | User | Medium | Retain with opportunity. | Export structured fields. | Delete with opportunity/workspace/account. | Log changes at field summary level. | Yes, after review-before-save. | No hidden ranking or sale of attention. |
| Opportunity/Role-backed records | User | Medium | Retain while opportunity exists. | Export Opportunity-facing fields and Role-backed compatibility metadata where needed. | Delete/archive according to approved opportunity lifecycle. | Log create/update/archive and compatibility target IDs. | Yes, as source-grounded input. | Usage limits may count records; no employer-paid prioritization. |
| COMPASS evaluations | User | High | Retain while user keeps evaluation history. | Export score, recommendation, evidence, model metadata, and warnings. | Delete with opportunity or account; future selective deletion TBD. | Log evaluation lifecycle, hashes, model status, and versions. | Yes, as advisory analysis. | Not employer-facing and not sold. |
| Generated artifacts | User | High | Retain until user deletes or archives. | Export content, metadata, lineage, and truthfulness warnings. | Delete artifact revisions according to future lifecycle design. | Log generation/revision/lifecycle transitions. | Yes, as output and future grounding only when user approves. | May support paid artifact quotas, not hidden targeting. |
| Artifact exports | User | High | Retain export metadata; local files are user-controlled. | Export metadata and generated file references where available. | Delete metadata with artifact/account; local file deletion is outside app unless future packaged app controls it. | Log export event and format, not private content in logs. | No, except metadata for lifecycle insight. | May count against paid export/artifact features later. |
| Application workflow state/history | User | Medium | Retain with application/opportunity. | Export states, timestamps, notes references, and history. | Delete with application/opportunity/account. | Log state transitions and actor. | Yes, for analytics and strategy. | Aggregate usage only; no employer steering. |
| Notes | User | High | Retain until user deletes or parent record is deleted. | Export note content and metadata. | Delete with note or parent lifecycle. | Log note lifecycle without content in operational logs. | Only if user explicitly includes notes in synthesis. | Not monetized directly. |
| Reminders | User | Medium | Retain until completed, deleted, or parent record is deleted; future cleanup policy TBD. | Export reminder fields and completion status. | Delete with reminder or parent lifecycle. | Log create/update/complete/delete. | Yes, for workflow guidance after reconciliation. | Not monetized directly. |
| Interviews | User | Medium | Retain with application. | Export interview stages, dates, notes, and outcomes. | Delete with application/account. | Log lifecycle changes. | Yes, for workflow and strategy insights. | Not sold or shared. |
| External links | User | Medium | Retain with parent record. | Export URL, label, type, and metadata. | Delete with link or parent lifecycle. | Log link lifecycle, not external account access. | Yes, as context if user supplied. | Not used for hidden sponsorship. |
| Compensation targets | User | High | Retain while workspace/profile target exists. | Export compensation fields and assumptions. | Delete with workspace/account or target record. | Log target changes without sensitive detail in operational logs. | Yes, for user-side strategy and fit. | Never employer-facing without explicit sharing. |
| Recruiter/source/contact metadata | User | Medium to high | Retain while user keeps source/contact context. | Export source/contact labels, notes, and provenance. | Delete with source/contact/opportunity/account. | Log lifecycle and references. | Yes, for source quality and provenance. | Not sold to recruiters or employers. |
| AI prompts | User/system | High | Store only when needed for audit/debug and with redaction policy; current retention policy TBD. | Export if stored and user-specific. | Delete with related AI run/account subject to future audit policy. | Log prompt version, hashes, and model metadata; avoid raw prompt logs by default. | Sent to provider only when AI feature is enabled. | Not monetized as content. |
| AI outputs | User | High | Retain with generated/evaluation records. | Export outputs and trace metadata. | Delete with related record/account. | Log lifecycle, model, prompt/ruleset versions, warnings. | May be reused only as traceable, reviewable context. | May count usage, not steer hidden sponsorship. |
| Activity logs | User/system | Medium | Retain for audit window TBD. | Export user-visible activity. | Delete/anonymize under account deletion policy after approved retention window. | Source of audit summaries, not source of domain truth. | Limited use for analytics and strategy. | Aggregate operational metrics only. |
| Automation suggestions | User/system | Medium to high | Retain while useful for audit and workflow; window TBD. | Export suggestion, reason, target, status, and preview metadata. | Delete with workspace/account or future cleanup policy. | Log suggestion lifecycle. | Yes, for local suggestions only. | Not used for employer-paid steering. |
| Automation approval logs | User/system | High | Retain as audit records under approved retention window. | Export approval decision, target, actor, and status. | Delete/anonymize according to future account deletion policy. | First-class audit record. | Limited use for safety analytics. | Not monetized. |
| Analytics/insight data | User/system | Medium | Retain derived summaries while source data exists. | Export user-visible insight summaries and basis where available. | Recompute or delete when source records are deleted. | Log generation/version metadata. | Yes, if source-grounded and confidence-labeled. | May support paid analytics tiers only with transparent limits. |

## Governance Expectations

- Data export/delete must be designed before production implementation.
- Retention windows must be explicit before private hosted beta.
- Logs must avoid raw resumes, prompts, private notes, API keys, and raw job
  descriptions unless an approved diagnostic mode exists.
- AI use must be opt-in where provider calls are involved.
- Future collaboration and employer-side modes require separate sharing,
  revocation, audit, and disclosure design.
