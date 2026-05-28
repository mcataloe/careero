# Layer 4D Workflow Readiness Summary

Status: Active  
Doc Type: Audit  
Layer: Layer 4  
Source of Truth: No  
Last Reviewed: 2026-05-28  
Related Docs:
- ../../01_strategy/07_revised-build-order-execution-plan.md
- ../../02_layers/04_layer-04-application-workflow.md
- ../../03_domain-design/application-workflow-persistence.md
- layer-4-workflow-recon.md

## Summary

Layer 4 is complete for the current MVP scope after the 4B state/timeline pass,
the 4C workflow UX pass, and the 4D hardening pass. This means the local
application workflow foundation is ready to support Layer 5 insight
stabilization. It does not mean Careero is production-ready or hosted-ready.

Layer 4 now covers saved opportunity workflow entry, application state,
validated transitions, state history, aggregate timeline, notes, external links,
local reminders, interviews, archive/reactivate behavior, workspace/search-track
context, application pipeline views, and dashboard workflow attention.

## Test Inventory

Backend/API coverage:

- `backend/tests/test_application_state_machine.py` covers canonical workflow
  transitions, rejected transitions, idempotent same-state transitions,
  reactivation rules, and available transitions.
- `backend/tests/test_application_workflows.py` covers application ensure/list/
  detail/update, opportunity aliases, status transitions, timeline retrieval,
  archive/reactivate, notes, links, reminders, interviews, workspace filtering,
  inactive workspace behavior, validation errors, and not-found behavior.
- `backend/tests/test_local_user_boundaries.py` covers local current-user
  ownership boundaries for workspaces, roles/opportunities, applications, child
  workflow records, and opportunity-scoped application aliases.

Frontend coverage:

- `ApplicationDetailPage.test.tsx` covers routed application overview,
  workspace context, timeline success/empty/error states, status transitions,
  failed transition feedback, and archive confirmation.
- `ApplicationsPage.test.tsx` covers empty/error states, pipeline grouping,
  command-center indicators, status transitions, failed transitions, and
  archived workflow visibility.
- `RoleDetailPage.test.tsx` covers opportunity workflow summary, untracked
  opportunity empty state, track-as-application flow, load errors, and
  dismissible success feedback.
- `DashboardPage.test.tsx` covers the overview workflow attention panel while
  preserving routed Layer 5 dashboard sections.
- `ApplicationTimeline`, `ApplicationNotesPanel`, `ApplicationRemindersPanel`,
  `ApplicationInterviewPanel`, and `ApplicationLinksPanel` component tests cover
  empty/populated states, safe metadata rendering, CRUD interactions where
  supported, reminder status labels, interview grouping, and outbound link
  safety.

## Current Capabilities

- `Application.current_state` is authoritative; `Application.status` remains a
  compatibility mirror.
- Supported states remain `discovered`, `interested`, `applied`,
  `interviewing`, `offer`, `rejected`, `withdrawn`, and `archived`.
- Timeline is an aggregate read model over durable workflow records, COMPASS
  evaluations, generated artifacts, and selected activity logs. It is not a
  separate event-sourcing table.
- Opportunity-facing application reads are Role-backed compatibility aliases and
  do not create workflows from `GET` requests.
- The Applications page is the main Layer 4 command center; Dashboard only
  exposes compact workflow attention signal.

## Known Limitations

- Local reminders do not send hosted notifications, create calendar events, sync
  email, or run background jobs.
- Artifact lifecycle review/approve/archive/submitted tracking remains Layer 6.
- Layer 5 insight stabilization must validate workspace filters, confidence,
  basis strings, thin-data behavior, and actionability using the hardened Layer 4
  workflow data.
- Opportunity persistence remains Role-backed until Layer 7 strategy approves a
  compatibility or migration path.
- Production auth, account lifecycle, billing, deployment, support, and tenant
  hardening remain Layer 11 readiness work.

## Layer 4D Validation

Completed checks on 2026-05-28:

- `cd backend; .\.venv\Scripts\python.exe -m pytest tests\test_application_state_machine.py`
  passed: 22 tests.
- `cd frontend; npm.cmd test -- ApplicationDetailPage.test.tsx ApplicationsPage.test.tsx RoleDetailPage.test.tsx DashboardPage.test.tsx ApplicationTimeline.test.tsx ApplicationNotesPanel.test.tsx ApplicationRemindersPanel.test.tsx ApplicationInterviewPanel.test.tsx ApplicationLinksPanel.test.tsx`
  passed: 9 files, 34 tests.
- `cd frontend; npm.cmd run build` passed. Vite reported the existing large
  chunk warning for the production bundle.
- DB-backed backend tests for `test_application_workflows.py` and
  `test_local_user_boundaries.py` were skipped locally because
  `CAREERO_TEST_DATABASE_URL` is not configured.

## Recommendation

Proceed to Layer 5 insight stabilization once DB-backed backend workflow tests
can be run in an environment with `CAREERO_TEST_DATABASE_URL`. Treat Layer 4 as
complete for local MVP workflow scope, not as production-ready hosted workflow
infrastructure.
