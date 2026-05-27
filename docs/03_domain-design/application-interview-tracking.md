# Application Interview Tracking

Status: Active  
Doc Type: Domain Design  
Layer: Layer 4  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/03_domain-design/application-workflow-persistence.md
Layer 4G stores interview activity as structured application interview stages. Interview stages are part of the local application workflow record and should be used instead of relying on freeform notes as the only source of interview truth.

## Model

Each interview stage belongs to one application, user, and workspace. The persisted fields are:

- `stage_type`: one of `recruiter_screen`, `hiring_manager`, `technical`, `system_design`, `behavioral`, `panel`, `final`, `offer_discussion`, or `other`.
- `title`: user-facing label for the stage.
- `scheduled_at`: timezone-aware scheduled date/time, or `null` for unscheduled planned stages.
- `completed_at`: timezone-aware completion date/time, or `null` until completed/no-show.
- `status`: one of `planned`, `scheduled`, `completed`, `canceled`, or `no_show`.
- `interviewer_names`: structured list of interviewer names.
- `location_or_meeting_link`: manually-entered address or existing meeting URL.
- `notes`: general interview notes.
- `preparation_notes`: manual preparation notes for the stage.
- `outcome_notes`: notes about completion, cancellation, no-show, or next steps.
- `metadata`: extension object for local-first metadata.

Active interviews (`planned`, `scheduled`) sort by `scheduled_at` ascending, with unscheduled stages last. Completed/canceled/no-show stages sort reverse chronologically.

## State and Status Behavior

Creating an interview stage derives a default status:

- `completed` when `completed_at` is provided.
- `scheduled` when `scheduled_at` is provided.
- `planned` otherwise.

Completing a stage sets `status` to `completed` and fills `completed_at` if omitted. The complete endpoint also accepts `no_show` for manual no-show tracking. Canceling a stage sets `status` to `canceled`; the cancel endpoint also accepts `no_show`.

Creating or scheduling an interview does **not** silently mutate the application workflow state. If the application can transition to `interviewing`, API responses may expose a `state_transition_suggestion` so the UI can prompt the user to make an explicit workflow transition.

## Timeline and Activity Log

Interview creation and completion are first-class application timeline events. Updates, cancellations, and deletes are captured through activity log events and are timeline-aware without exposing deleted interview body content as the canonical interview record.

## Boundaries

Layer 4G is manual interview tracking only. It intentionally does not:

- Create or modify calendar events.
- Generate video meeting links.
- Send email invites or reminders.
- Provide mock interview coaching or automated interview preparation.

Those capabilities belong to later layers and should integrate with these structured interview stages rather than replacing them with freeform notes.

