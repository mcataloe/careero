# Layer 6 Artifact Lifecycle Completion Summary

Status: Complete for Current Local MVP Scope  
Doc Type: Implementation Summary  
Layer: Layer 6  
Source of Truth: No  
Last Reviewed: 2026-05-28

## Scope Completed

Layer 6 now has a local artifact lifecycle built around `draft`, `reviewed`,
`submitted`, and `archived`.

Implemented scope:

- First-class lifecycle columns, version metadata, source artifact linkage,
  evaluation/source references, and lifecycle timestamps on `GeneratedArtifact`.
- Central lifecycle state transition service.
- Resume and cover-letter generation persistence normalized to draft lifecycle
  records.
- Lifecycle API for draft creation, detail/list retrieval, draft edit, review,
  submit, archive, and application/opportunity/workspace scoped lists.
- Submitted artifact protected-edit behavior: editing a submitted artifact creates
  a new draft revision linked to the submitted source artifact.
- Application timeline reviewed/submitted/archived artifact events.
- Application artifact UX with status display, separated resume/cover-letter
  lists, detail preview, draft edit, submitted/final messaging, archive toggle,
  and opportunity-detail artifact entry point.
- Employer-facing content boundary: artifact body content remains separate from
  COMPASS rationale, ATS notes, compensation strategy, private decision rationale,
  user notes, and generation metadata.

## Verification

Passing checks run during Layer 6B-6E:

- `backend`: `.\.venv\Scripts\python.exe -m pytest tests\test_artifact_lifecycle.py`
- `backend`: `.\.venv\Scripts\python.exe -m compileall app tests\test_artifact_lifecycle.py tests\test_artifact_workflows.py`
- `packages/contracts`: `npm.cmd test -- --run tests\contracts.test.ts`
- `frontend`: `npm.cmd run test -- ApplicationDetailPage.test.tsx RoleDetailPage.test.tsx`
- `frontend`: `npm.cmd run test -- ApplicationDetailPage.test.tsx`
- `frontend`: `npm.cmd run build`
- repository whitespace check: `git diff --check`

Blocked locally by environment:

- DB-backed backend lifecycle/workflow tests require `CAREERO_TEST_DATABASE_URL`.
  Without that environment variable, pytest fails in `backend/tests/conftest.py`
  before test code runs. This was treated as an environment block rather than a
  product regression.

## Known Limitations

- No standalone workspace-wide artifact browser is implemented yet.
- Frontend export/download controls remain Layer 8 work, though backend artifact
  export endpoints exist and use the selected artifact record.
- Artifact comparison and richer evidence-map UX remain future Layer 6 expansion.
- Hosted multi-user permission hardening remains Layer 11/productization work.

## Follow-Up Candidates

- Layer 7 should keep Role-backed Opportunity compatibility explicit and avoid a
  destructive rename unless separately approved.
- Layer 8 can attach frontend export/download controls to exact artifact
  versions now that lifecycle and submitted-state identity exist.
- Layer 12 advisor collaboration can depend on artifact lifecycle status, but
  hosted sharing remains blocked by auth, permission, revocation, and audit work.
