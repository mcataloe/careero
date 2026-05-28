# Layer 4 - Application Workflow

Status: Active  
Doc Type: Layer Spec  
Layer: Layer 4  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/03_domain-design/application-workflow-persistence.md
- docs/03_domain-design/application-interview-tracking.md

Layer 4 covers application state, state history, notes, links, reminders, timeline behavior, and interview tracking.

Canonical details live in [application workflow persistence](../03_domain-design/application-workflow-persistence.md) and [application interview tracking](../03_domain-design/application-interview-tracking.md).

Layer 4C UX completion makes `/applications` the workflow command center and
uses routed application detail sections for overview, interviews, reminders,
suggestions, advisor packet, notes, links, and timeline. Users can see workspace
context, current state, next actions, workflow counts, status controls, safe
timeline metadata, and non-destructive archive/reactivate behavior without
changing the Layer 4B state model or timeline persistence design.

Remaining hardening belongs to Layer 4D: broader regression tests, final docs
cleanup, and any small accessibility or copy corrections discovered after usage.
