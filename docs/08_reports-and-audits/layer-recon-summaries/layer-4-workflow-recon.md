# Layer 4A Application Workflow Recon

Status: Active  
Doc Type: Recon / Audit  
Layer: Layer 4  
Source of Truth: No  
Last Reviewed: 2026-05-28  
Branch Inspected: `main`  
Related Docs:
- `docs/01_strategy/07_revised-build-order-execution-plan.md`
- `docs/08_reports-and-audits/repo-reconciliation-recon.md`
- `docs/02_layers/04_layer-04-application-workflow.md`
- `docs/03_domain-design/application-workflow-persistence.md`
- `docs/03_domain-design/application-interview-tracking.md`

This report is recon-only audit evidence. It does not approve Layer 4B implementation, schema changes, route changes, UI redesigns, or feature work.

## 1. Executive Summary

Layer 4 is **Mostly implemented but needs hardening**.

The current repo has a substantial local application workflow foundation: saved opportunities can be converted into application workflows; `Application.current_state` is the authoritative workflow state; canonical transitions are enforced by a backend state machine; state history, notes, reminders, interviews, external links, timeline aggregation, and pipeline APIs exist; the frontend has routed application list/detail sections; and backend/frontend tests cover many workflow paths.

The main gaps are not basic CRUD availability. The remaining risks are workflow clarity and hardening: application overview is thin, dashboard surfaces do not directly answer all Layer 4 attention questions, next-action visibility is basic, workspace/search-track context is weak in application views, timeline is an aggregate read model rather than a standalone durable event table by design, and hosted reminder delivery, notifications, calendar sync, email sync, and production auth remain out of scope.

Layer 4B should therefore be scoped as a narrow state/timeline completion and confirmation pass, not a rebuild of the existing workflow system.

## 2. Layer 4 Feature Inventory

| Feature | Expected behavior | Current frontend state | Current backend/API state | Current data model state | Current test state | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Opportunity save/list/detail | User can save opportunities, list them, inspect detail, and attach workflow state. | `frontend/src/App.tsx` routes `/opportunities`, `/opportunities/new`, and `/opportunities/:opportunityId/:section`; `RoleDetailPage.tsx` uses Opportunity language. | `backend/app/api/opportunities.py` exposes Opportunity-facing endpoints backed by Role service; application ensure exists at `/api/opportunities/{opportunity_id}/application`. | `Role` remains the persisted Opportunity-compatible table with `workspace_id`, `user_id`, and listing `status`. | Role/opportunity and application alias tests exist, including opportunity application alias coverage in `backend/tests/test_application_workflows.py`. | Partially implemented | Product-facing Opportunity language exists, but persistence remains Role-backed by design until Layer 7 compatibility work. |
| Opportunity status | Listing status should not be confused with application workflow state. | Opportunity detail shows `role.status`; application views show `current_state`. | Opportunity APIs expose Role status; application APIs expose workflow state. | `RoleStatus` has `found`, `interested`, `applied`, `archived`; `ApplicationWorkflowState` has workflow-specific states. | Contract and application tests cover both surfaces indirectly. | Implemented with terminology risk | Docs correctly say `Role.status` is compatibility/listing state; UI should keep this distinction visible. |
| Application status | Application workflow should have canonical states and current state display. | `ApplicationsPage.tsx` groups by state; `ApplicationDetailPage.tsx` shows current state badge. | `/api/applications`, `/api/applications/{id}`, `/api/applications/pipeline`, and transition endpoints return current state. | `Application.current_state` is authoritative; legacy `Application.status` mirrors it. | `test_application_state_machine.py` and `test_application_workflows.py` cover states. | Implemented | Existing state set is adequate for Layer 4; do not introduce `SAVED/REVIEWING/APPLYING` unless a later recon proves a specific gap. |
| Status transition behavior | State changes should be explicit, validated, scoped, and history-producing. | Pipeline cards show available next-state buttons and pass `reactivate` for archived workflows. | `ApplicationWorkflowService.transition_state` enforces `application_state_machine.py`; alias and canonical transition routes exist. | `application_state_history` records state changes; `archived_at` and `reactivated_at` are tracked. | Tests cover valid matrix, invalid transitions, idempotent same-state, reactivation, API transition validation, and pipeline. | Implemented | Transition UX exists mostly on pipeline cards; detail page has state badge but no full state-management affordance. |
| Notes | User can create, edit, delete, and view application notes. | `ApplicationNotesPanel` supports add/edit/delete and empty state. | Notes CRUD endpoints exist under `/api/applications/{id}/notes`. | `ApplicationNote` is scoped by application, user, and workspace; delete is soft delete. | Backend and component tests cover CRUD, soft delete, counts, scoping, and activity/timeline behavior. | Implemented | Timeline excludes deleted note body from canonical deleted events. |
| Reminders | User can create, edit, complete, and view local reminders; local next action can update. | `ApplicationRemindersPanel` supports add/edit/complete and empty state. | Reminder list/create/update/complete endpoints exist. | `ApplicationReminder` has `due_at`, `completed_at`, user/workspace scope; `Application.next_action_at` is updated from earliest open due date. | Backend and component tests cover CRUD, completion, next-action sync, and timeline events. | Implemented locally | Hosted notification delivery, background jobs, calendar sync, and email reminders are absent and should remain later-layer work. |
| Interviews | User can track structured interview stages. | `ApplicationInterviewPanel` supports add, complete, cancel, delete, empty state, and state-transition suggestion. | Interview list/create/update/complete/cancel/delete endpoints exist. | `ApplicationInterviewStage` stores stage type, status, scheduling/completion fields, notes, prep/outcome fields, and user/workspace scope. | Backend and component tests cover CRUD, validation, completion, cancel/no-show, suggestion, timeline, and scoping. | Implemented | Interview activity does not silently mutate application state, which matches automation-boundary guidance. |
| Timeline/history events | User can inspect meaningful workflow history. | `ApplicationDetailPage.tsx` has routed `timeline` section using `ApplicationTimeline`. | `/api/applications/{application_id}/timeline` returns reverse chronological aggregate events. | Durable sources include `ApplicationStateHistory`, typed child tables, `ActivityLog`, `CompassEvaluation`, and `GeneratedArtifact`; no standalone timeline table exists. | Tests cover creation, state changes, archive/reactivate, typed children, evaluations, artifacts, API retrieval, and safe metadata. | Implemented as aggregate | This is intentional per docs. 4B should only add a durable timeline table if a specific analytics/reporting need justifies changing the model. |
| Archive/reactivate | User can archive and explicitly reactivate workflows. | Applications pipeline can include archived workflows and passes `reactivate` from archived state. | State machine allows archived to discovered/interested only with `reactivate=true`; role archive endpoint exists. | `Application.archived_at` and `reactivated_at` exist; `ApplicationStateHistory` marks transitions. | Tests cover archive/reactivate semantics and timeline event types. | Implemented with UX hardening gap | Reactivation is available through pipeline state moves, but the application detail page does not make archive/reactivate workflow especially prominent. |
| Dashboard summaries | User should answer active work, attention, recent updates, due reminders, upcoming interviews, archived roles, search track, next action. | Dashboard has routed sections for overview, COMPASS, sources, compensation, search health, recommendations, automation, artifacts, and history. Applications page provides pipeline counts/cards. | Search analytics, search health, recommendations, historical learning, and application pipeline APIs exist. | Analytics use persisted workflow, artifact, COMPASS, and activity records. | Dashboard and analytics tests exist outside the core Layer 4 tests; Layer 4 test focus is stronger on application workflows. | Partially implemented | Dashboard is useful but not yet a Layer 4 command center for due reminders/upcoming interviews/recent workflow updates. |
| Workspace/search-track filtering | Workflow should stay tied to workspace/search-track context. | Application routes do not carry a workspace route prefix; dashboard has no obvious global workspace context indicator. | Application list/pipeline APIs accept `workspace_id`; workspace-scoped routes exist. | Application, child records, Role, COMPASS, artifacts, and logs carry `workspace_id`. | Backend tests cover workspace scoping and inactive filtering. | Partially implemented | Data/API support is stronger than frontend context. Workspace switching/management UX remains immature. |
| Ownership/access control | Users should not access another user's workflow records. | Frontend assumes current local user context. | Services resolve current user and use ownership helpers such as `require_user_role` and `require_user_application`. | Layer 4 tables carry `user_id` and `workspace_id`. | `backend/tests/test_local_user_boundaries.py` covers workspace, role, application, and child record scoping. | Implemented locally | Production auth/tenant hardening remains Layer 11 readiness work. |
| Empty states | Empty workflow areas should be understandable and calm. | Applications, notes, reminders, interviews, links, and timeline have empty states. | APIs return empty lists where appropriate. | No special model needed. | Component/page tests cover several empty states. | Partially implemented | Empty states exist, but many are terse and do not consistently answer "what do I do next?" |
| Next action surfacing | User should know what to do next. | Pipeline cards show `Next action` when `next_action_at` exists; reminders update detail data after mutations. | `Application.next_action_at` is updated from local open reminders and exposed in summaries/details. | `Application.next_action_at` is indexed. | Reminder tests cover next-action sync. | Partially implemented | Next action is present but basic; no unified attention queue or dashboard due/upcoming view exists. |

## 3. Application State Model Audit

`Application.current_state` is the authoritative application workflow state. The legacy `applications.status` column remains as a compatibility mirror and should not be treated as a second state model.

Current workflow states:

- `discovered`
- `interested`
- `applied`
- `interviewing`
- `offer`
- `rejected`
- `withdrawn`
- `archived`

Current transition behavior is defined in `backend/app/services/application_state_machine.py`:

- `discovered` -> `interested`, `withdrawn`, `archived`
- `interested` -> `applied`, `withdrawn`, `archived`
- `applied` -> `interviewing`, `rejected`, `withdrawn`, `archived`
- `interviewing` -> `offer`, `rejected`, `withdrawn`, `archived`
- `offer` -> `withdrawn`, `archived`
- `rejected` -> `archived`
- `withdrawn` -> `archived`
- `archived` -> `discovered` or `interested` only with explicit `reactivate=true`

The current state model is adequate for Layer 4. It already covers saved/not-applied, applied, interview, offer, closed, withdrawn, and archive semantics. It is also compatible with later analytics because state history is typed, timestamped, scoped to user/workspace, and indexed.

Known state-model risks:

- `Role.status` and `Application.current_state` can still confuse users or implementers because both may show status-like values.
- `Workspace.status` has `paused` and `completed`, but application state intentionally does not. This should remain documented so "paused search" does not become a per-application state without intent.
- Detail-page status management is weaker than pipeline status management.
- Application state labels are raw-ish in some places; UX refinement should map them to calm product labels without changing persisted values.

Minimal recommendation for 4B: preserve the existing state set and transition matrix. Add only targeted fixes if recon-follow-up finds missing state history, response-shape, or UI wiring gaps.

## 4. Timeline and History Audit

Timeline retrieval is implemented at `GET /api/applications/{application_id}/timeline`. It is a reverse-chronological aggregate read model, not a separate durable `TimelineEvent` table. Durable inputs are:

- `Application.created_at`
- `ApplicationStateHistory`
- active `ApplicationNote` rows
- active `ApplicationReminder` rows and completion timestamps
- active `ApplicationInterviewStage` rows and completion timestamps
- active `ApplicationExternalLink` rows
- selected `ActivityLog` events
- completed `CompassEvaluation` records
- generated resume and cover-letter artifacts

Covered event types include application created, state changed, archived, reactivated, note created, external link created, reminder created, reminder completed, interview created, interview completed, COMPASS completed, resume artifact created, cover-letter artifact created, and selected update/delete activity events.

Missing or partial history semantics:

- Parsed/saved opportunity history is not clearly surfaced as first-class application timeline context beyond role/application creation and activity records.
- Artifact submitted/reviewed/approved/archive lifecycle events are not complete because Layer 6 lifecycle is incomplete.
- User decision rationale is not a first-class workflow event type unless captured in notes.
- Timeline filtering is not exposed in the UI.
- Timeline events are good for rendering but not a standalone event-sourcing ledger; that is acceptable unless Layer 5/6 analytics require event-table semantics.

Recommended direction: keep timeline as an aggregate unless a specific downstream reporting need proves a dedicated table is necessary. Add missing event coverage through the existing typed records and `ActivityLog` pattern first.

## 5. Notes, Reminders, and Interviews Audit

Notes:

- CRUD exists in backend API and frontend panel.
- Notes are scoped to application, user, and workspace.
- Soft delete prevents deleted notes from appearing in active lists/counts.
- Activity/timeline behavior is covered by tests.
- Gap: notes do not include a dedicated "decision rationale" type beyond existing note categories.

Reminders:

- List/create/update/complete exist in backend API and frontend panel.
- Due dates and completion state exist.
- `Application.next_action_at` syncs to the earliest open reminder due date.
- Timeline includes reminder created/completed; activity log includes update events.
- Gaps: no hosted notifications, background scheduling, calendar sync, email sync, snooze semantics, or global due-reminder queue.

Interviews:

- Structured stage tracking exists with stage type, status, scheduled/completed timestamps, interviewer names, location/link, notes, prep notes, outcome notes, and metadata.
- Create/update/complete/cancel/delete exist.
- The UI can suggest a move to `interviewing` without silently mutating workflow state.
- Timeline includes create/complete; activity log covers update/cancel/delete.
- Gaps: no calendar integration, no generated meeting links, no automatic invite handling, and no full interview-prep automation.

## 6. Dashboard Audit

Current users can partially answer:

- What opportunities are active? Yes, primarily through `/applications` pipeline and opportunity lists.
- What requires attention? Partially, through next-action dates on application cards and recommendation/automation/dashboard surfaces.
- What did I recently update? Partially, through application timeline and dashboard history surfaces.
- What reminders are due? Partially, per application and next-action date; no global due-reminder dashboard view.
- What interviews are upcoming? Partially, per application; no global upcoming-interview dashboard view.
- Which roles are archived? Partially, with include-archived pipeline and role archive state.
- Which search track am I in? Partially in data/API; weak as persistent UI context in application views.
- What should I do next? Partially; no unified Layer 4 action queue.

Dashboard and Applications are complementary, but the dashboard is not yet a complete Layer 4 operations cockpit. Layer 4C should decide whether to add a focused workflow dashboard section, strengthen Applications as the command center, or add workspace-aware attention summaries.

## 7. UX Structure Audit

Strengths:

- Major pages now use routed sub-sections rather than one long un-routed page.
- Application detail has sections for overview, interviews, reminders, suggestions, advisor packet, notes, links, and timeline.
- Applications page groups workflows by canonical state and exposes available transitions.
- Empty, loading, and error states exist across many Layer 4 components.

Weaknesses:

- Application overview is thin: counts and job posting link do not provide enough workflow orientation.
- Application detail status is mostly a badge; state-change action is more discoverable in the pipeline than in the detail view.
- Pipeline cards can become dense because counts, dates, and transition buttons all live in compact cards.
- Dashboard pages remain dense routed workspaces with many card/table sections; Layer 4 attention questions are spread across dashboard, applications, and application detail.
- Workspace/search-track context is not consistently visible in application views.
- Empty states are calm but often terse; they do not consistently offer the next useful action.
- Dismissible feedback and optimistic mutation states exist only in local component patterns, not as a unified workflow convention.

Layer 4C should focus on clarity, not visual redesign: stronger overview, next-action cues, workspace context, due/upcoming summaries, and detail-page status actions.

## 8. API and Data Contract Audit

API support is strong for local Layer 4:

- Application ensure/list/detail/update/pipeline endpoints exist.
- Workspace-scoped list and pipeline endpoints exist.
- Transition endpoints validate state changes and support explicit reactivation.
- Notes, reminders, interviews, and external links have CRUD-style endpoints.
- Timeline retrieval exists.
- Ownership checks are enforced through current-user context and service ownership helpers.

Data support is strong for local Layer 4:

- `Application`, `ApplicationStateHistory`, `ApplicationNote`, `ApplicationReminder`, `ApplicationInterviewStage`, and `ApplicationExternalLink` provide typed records.
- All core workflow records carry user/workspace scope.
- Indexes exist for state, workspace/state, next action, reminder due/completion, interview scheduled/completed/status, and deleted children.

Contract and coupling risks:

- `Role` remains the persistence name for product Opportunity, which continues to be Layer 7 compatibility debt.
- Frontend application API types live in `frontend/src/types/applications.ts`; package contracts define canonical `ApplicationState`, but runtime API responses are not fully generated from contracts.
- Timeline event shape is service-defined rather than a shared package contract.
- Layer 5 dashboards depend on workflow data quality but do not yet have a single Layer 4 attention feed.
- Artifact timeline events exist only for generated artifacts; submitted/reviewed/approved lifecycle semantics belong to Layer 6.

## 9. Recommended Implementation Plan

### Layer 4B - Application State and Timeline Completion

Likely files:

- `backend/app/services/application_state_machine.py`
- `backend/app/services/applications.py`
- `backend/app/api/applications.py`
- `backend/tests/test_application_state_machine.py`
- `backend/tests/test_application_workflows.py`
- `frontend/src/api/applications.ts`
- `frontend/src/types/applications.ts`
- `frontend/src/pages/ApplicationDetailPage.tsx`
- `frontend/src/pages/ApplicationsPage.tsx`
- Layer 4 docs under `docs/02_layers` and `docs/03_domain-design`

Scope:

- Confirm the existing state model and transition matrix as canonical.
- Patch only proven gaps in state transition responses, history creation, timeline event coverage, or detail-page status/timeline wiring.
- Preserve the aggregate timeline design unless a concrete downstream need requires a durable timeline-event table.
- Keep hosted reminders, artifact lifecycle, insights, integrations, automation, and productization out of scope.

Risks:

- Accidentally duplicating `Role.status` and `Application.current_state` semantics.
- Overbuilding timeline storage beyond current need.
- Pulling Layer 6 artifact lifecycle into Layer 4.

Acceptance criteria:

- Existing states and transitions remain validated.
- Meaningful state changes create history and visible timeline events.
- Archive/reactivate remains explicit.
- Timeline retrieval remains ownership-scoped and safe.
- Tests cover any corrected behavior.

### Layer 4C - Workflow UX Completion

Likely files:

- `frontend/src/pages/ApplicationsPage.tsx`
- `frontend/src/pages/ApplicationDetailPage.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- Layer 4 workflow components in `frontend/src/components`

Scope:

- Improve application overview and detail-page state action discoverability.
- Add clearer next-action, due-reminder, and upcoming-interview surfacing.
- Improve workspace/search-track context indicators in workflow views.
- Strengthen empty states with concrete next actions.
- Keep UI calm and routed; do not redesign the whole app shell.

Risks:

- Creating another dense dashboard instead of clarifying workflow actions.
- Hiding important state transitions behind too much progressive disclosure.

Acceptance criteria:

- User can tell current state, next action, due reminders, upcoming interviews, and workspace context from workflow surfaces.
- Empty states guide the next useful local action.
- Existing tests are updated or added for changed UX behavior.

### Layer 4D - Tests and Docs Hardening

Likely files:

- `backend/tests/test_application_workflows.py`
- `backend/tests/test_application_state_machine.py`
- `backend/tests/test_local_user_boundaries.py`
- Frontend page/component tests for Applications and Application Detail
- `packages/contracts/tests/contracts.test.ts`
- Layer 4 docs and reports

Scope:

- Backfill regression tests for any 4B/4C changes.
- Reconfirm ownership/access, archive/reactivate, notes, reminders, interviews, timelines, dashboard queries, and empty states.
- Update docs to distinguish local workflow support from hosted notification/productization work.

Risks:

- Treating local workflow completeness as production readiness.
- Letting docs drift back into claiming hosted reminders or marketplace/employer behavior.

Acceptance criteria:

- Layer 4 tests cover the implemented workflow surface.
- Docs match code reality and preserve Layer 11 readiness boundaries.
- No productization, integration, automation, or marketplace scope is introduced.

