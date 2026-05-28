# Automation Guardrails

Status: Active  
Doc Type: Domain Design  
Layer: Layer 9  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/01_strategy/04_cross-layer-impact-map.md
- docs/06_operations/execution-drift-ledger.md
Layer 9 introduces local automation guardrails for Careero. Automation in this
layer means reviewable suggestions, local draft previews, readiness checks,
explicit approvals, dismissals, and audit records.

It does not mean external sending, external sync, background polling,
auto-apply, automated submission, or autonomous agents.

## MVP Boundary

Implemented Layer 9 automation is suggestion-first:

- Suggestions are durable records scoped to a workspace/search track.
- Approval logs are first-class audit records.
- Workspace automation preferences live in workspace preferences.
- Communication drafts remain local suggestion previews.
- Artifact readiness checks do not mark artifacts reviewed, submitted, archived,
  or exported.
- Workflow state suggestions do not mutate application state.
- External actions remain disabled.

## Data Ownership

`AutomationSuggestion` owns the proposed action, reason, basis, source inputs,
preview, status, and target references.

`AutomationApprovalLog` owns the user decision, actor, target, preview hash,
approval status, execution status, policy version, and timestamps.

`ActivityLog` may mirror high-level automation events, but it is not the source
of truth for approvals.

Application, Opportunity, Artifact, Reminder, and ActivityLog records remain the
owners of their existing domain state. Automation suggestions reference those
records; they do not replace them.

## Prohibited Behavior

Layer 9 must not implement:

- auto-apply
- auto-send
- Gmail, Outlook, calendar, or job-board mutation
- OAuth token storage
- background polling
- external sync
- batch approvals
- automatic submitted-artifact marking
- employer-facing content containing internal COMPASS, ATS, compensation, or
  strategy analysis
- destructive Role-to-Opportunity persistence rename

## Approval Behavior

Approving a suggestion records an approval log with `external_mutation=false`
and `execution_status=not_applicable` in the MVP. It does not execute an
external action or silently mutate application workflow state.

Future internal executors may be added only after they are explicitly scoped,
tested, and gated behind a fresh approval for each action.

