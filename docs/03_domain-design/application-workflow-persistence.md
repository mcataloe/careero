# Application Workflow Persistence

Layer 4 makes the existing `Application` row the workflow aggregate for a saved
role/opportunity and exposes workspace-aware service/API operations for list,
detail, ensure, state transition, and metadata update. It does not duplicate
role parsing, COMPASS evaluation, resume artifact generation, cover letter
generation, document export, automation, calendar, or email behavior.

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

Notes and external links are first-class workflow records. Notes support
`general`, `recruiter`, `compensation`, `follow_up`, and `interview` types.
External links support conventions such as `job_posting`, `company_careers`,
`recruiter_profile`, `application_portal`, `interview_prep`, `email_thread`,
and `other`. Deleting either record is a soft delete: active lists and counts
exclude deleted rows, while ActivityLog keeps a safe audit event for the
timeline.

`ActivityLog` remains a broad audit stream for events such as
`application.created` and `application.state_changed`. It is not the source of
truth for workflow rendering.

## Workspace Scope

Every application is linked to a workspace. New application workflows can only
be created for roles in active or paused workspaces. Archived and completed
workspaces remain inspectable, and migrated application history is preserved.

The application list endpoints are active-only by default. Use
`include_inactive=true` to include archived workflows. Use either
`GET /api/applications?workspace_id={workspace_id}` or
`GET /api/workspaces/{workspace_id}/applications` for workspace-scoped lists.

## Service And API Boundary

`POST /api/roles/{role_id}/application` is a safe ensure flow. It returns the
existing active workflow for the role when one exists, or creates one without
duplicating records.

`GET /api/applications` and workspace-scoped list endpoints return compact
summaries for the Applications page: role title, company, state, dates, latest
COMPASS summary/status, latest resume and cover letter artifact summaries, and
workflow counts for notes, external links, reminders, and interviews. They do
not return full COMPASS or artifact payloads and do not trigger generation.

`GET /api/applications/pipeline` and
`GET /api/workspaces/{workspace_id}/applications/pipeline` return the same
summary rows grouped by application workflow state. Archived workflows are
excluded unless `include_inactive=true` is supplied.

`GET /api/applications/{application_id}` returns richer detail, including the
canonical `ApplicationState` contract under `application_state`.

`GET /api/applications/{application_id}/timeline` returns a reverse
chronological timeline view. It aggregates existing typed workflow rows,
completed COMPASS evaluations, generated resume/cover-letter artifacts, and
selected ActivityLog entries. The timeline stores no rows of its own and must
not become the workflow source of truth.

Notes:

- `GET /api/applications/{application_id}/notes`
- `POST /api/applications/{application_id}/notes`
- `PATCH /api/applications/{application_id}/notes/{note_id}`
- `DELETE /api/applications/{application_id}/notes/{note_id}`

External links:

- `GET /api/applications/{application_id}/links`
- `POST /api/applications/{application_id}/links`
- `PATCH /api/applications/{application_id}/links/{link_id}`
- `DELETE /api/applications/{application_id}/links/{link_id}`

Reminders:

- `GET /api/applications/{application_id}/reminders`
- `POST /api/applications/{application_id}/reminders`
- `PATCH /api/applications/{application_id}/reminders/{reminder_id}`
- `POST /api/applications/{application_id}/reminders/{reminder_id}/complete`

Notes are not reminders and are not interview stages. External links are
manually attached resources such as job postings, portals, recruiter profiles,
and prep material. Email/calendar integrations and automatic imports remain out
of scope.

Reminders are local workflow records only. Creating, editing, and completing a
reminder can update `Application.next_action_at` based on the earliest open due
date, but it does not schedule background jobs, send notifications, create
calendar events, sync email, or trigger external automation.

`PATCH /api/applications/{application_id}` updates workflow metadata and dates.
It does not change `Application.current_state`; state changes must use the
state-transition operation.

## State Machine

Application workflow transitions are explicit and enforced by the backend:

- `discovered` -> `interested`, `withdrawn`, `archived`
- `interested` -> `applied`, `withdrawn`, `archived`
- `applied` -> `interviewing`, `rejected`, `withdrawn`, `archived`
- `interviewing` -> `offer`, `rejected`, `withdrawn`, `archived`
- `offer` -> `withdrawn`, `archived`
- `rejected` -> `archived`
- `withdrawn` -> `archived`

`archived` can move back to `discovered` or `interested` only when the
transition request includes `reactivate=true`. Every non-idempotent transition
updates `Application.current_state`, mirrors `applications.status`, appends a
typed state history row, and logs `application.state_changed`.

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
state history. Layer 9 automation guardrails must not silently mutate
application state.

## Timeline Event Types

Timeline event types are stable labels for rendering and filtering. Core events
include `application.created`, `application.state_changed`,
`application.archived`, `application.reactivated`, `note.created`,
`external_link.created`, `reminder.created`, `reminder.completed`,
`interview.created`, `interview.completed`, `compass.completed`,
`artifact.resume.created`, and `artifact.cover_letter.created`. ActivityLog may
enrich update/delete events such as `note.updated`, `note.deleted`,
`reminder.updated`, `external_link.updated`, and `external_link.deleted`, but it
does not replace typed workflow records.
