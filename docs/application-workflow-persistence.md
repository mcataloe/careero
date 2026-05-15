# Application Workflow Persistence

Layer 4A makes the existing `Application` row the workflow aggregate for a
saved role/opportunity. It does not duplicate role parsing, STRIDE evaluation,
resume artifact generation, cover letter generation, document export,
automation, calendar, or email behavior.

## Role And Application

`Role` remains the current backend name for the canonical Opportunity concept.
`Role.status` stays as a lightweight opportunity-listing status for compatibility
with existing role intake screens and tests.

`Application.current_state` is the authoritative application workflow state. It
uses the canonical values:

- `discovered`
- `interested`
- `applied`
- `interviewing`
- `offer`
- `rejected`
- `withdrawn`
- `archived`

The legacy `applications.status` column is retained as a compatibility mirror
of `current_state` in this layer. It is not a second workflow state.

## Typed Workflow Data

Application workflow data is stored in typed relational tables:

- `application_state_history` records every state change.
- `application_notes` stores user-visible workflow notes.
- `application_reminders` stores due dates and completion state.
- `application_interview_stages` stores structured interview steps.
- `application_external_links` stores posting, portal, and related links.

`ActivityLog` remains a broad audit stream for events such as
`application.created` and `application.state_changed`. It is not the source of
truth for workflow rendering.

## Workspace Scope

Every application is linked to a workspace. New application workflows can only
be created for roles in active or paused workspaces. Archived and completed
workspaces remain inspectable, and migrated application history is preserved.

## Migration Behavior

Existing roles are backfilled into application workflows when no active
application row exists:

- `found` maps to `discovered`
- `interested` maps to `interested`
- `applied` maps to `applied`
- `archived` maps to `archived`

Existing `applications.notes` content is copied into `application_notes`.
Every migrated application receives an initial state history row with
`changed_by="system"` and migration metadata.

## Automation Boundary

AI and future automation layers may suggest workflow actions, but user-visible
state changes must go through backend workflow persistence and append typed
state history. Layer 7 automation must not silently mutate application state.
