# Application Reminders

Application reminders are **local workflow records** attached to a Careero application. They help users track follow-ups, deadlines, interview preparation, thank-you notes, status checks, and revisit actions without introducing external automation.

## Lifecycle

A reminder is created for one application in one workspace with:

- `title` and optional `notes`
- timezone-aware `due_at`
- optional `completed_at`
- `reminder_type` such as `follow_up`, `deadline`, `next_action`, `interview_prep`, `thank_you`, `status_check`, `revisit`, or `submit_application`
- `priority` (`low`, `normal`, `high`)
- free-form `metadata`

Completing a reminder sets `completed_at`; it does **not** delete the reminder. Reopening a reminder clears `completed_at`. Deleting a reminder archives it with `deleted_at` so it no longer appears in active reminder lists or next-action derivation.

Reminder create, update, complete, reopen, and archive actions append application timeline entries and ActivityLog records.

## Boundaries

Layer 4 reminders are local-first application workflow data only. They intentionally do not implement:

- calendar sync
- email reminders
- push notifications
- background jobs
- automations
- automatic application state transitions

Future calendar, email, notification, or automation layers may read from reminders, but this layer does not perform those integrations.

## Upcoming and overdue logic

The backend is authoritative for reminder status queries:

- Overdue reminders are incomplete, unarchived reminders whose `due_at` is before the backend's current timezone-aware UTC time.
- Upcoming reminders are incomplete, unarchived reminders whose `due_at` is at or after the backend's current timezone-aware UTC time.
- Completed reminders are excluded from workspace upcoming and overdue summaries.
- Workspace reminder queries are scoped to the default local user and requested workspace.

Default reminder sorting is incomplete first, overdue first, soonest due date, then completed reminders later.

`applications.next_action_at` is derived from the earliest open, unarchived reminder due date for the application.
