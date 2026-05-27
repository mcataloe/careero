# Username Deprecation Audit

Status: Active  
Doc Type: Audit  
Layer: Layer 1  
Source of Truth: No  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/05_security-privacy-governance/account-lifecycle.md
Date: 2026-05-27

## Decision

Careero does not use usernames, handles, screen names, aliases, public names,
user slugs, or profile slugs as core identity.

The active auth identity model is:

- Email: unique login and account recovery identifier.
- Password: retained for email/password authentication.
- First name and last name: required at signup.
- Display name: derived from first name plus last name.
- Salutation, pronouns, and headshot URL: optional profile metadata.

## Findings And Classification

| Area | References audited | Classification | Outcome |
| --- | --- | --- | --- |
| Backend auth service/API | `backend/app/services/auth.py`, `backend/app/api/auth.py` | Replace with firstName/lastName and email login | Registration now accepts `email`, `firstName`, `lastName`, and `password`; login accepts `email` and `password`; current-user response returns `firstName`, `lastName`, derived `displayName`, `salutation`, `pronouns`, and `headshotUrl`. |
| Frontend auth contract and pages | `frontend/src/types/auth.ts`, `frontend/src/pages/LoginPage.tsx`, `frontend/src/pages/RegisterPage.tsx`, `frontend/src/auth/AuthProvider.tsx` | Replace with firstName/lastName and display-name helper | Login UI is email-only. Registration UI requires first and last name. Frontend `AuthUser` no longer includes `username`. |
| App shell session user display | `frontend/src/components/AppShellLayout.tsx` | Replace with display-name helper | Header uses `displayName`, then first/last name, then email. |
| Database user model | `backend/app/models.py`, Alembic revisions | Remove entirely from active schema; keep temporarily in historical migration/downgrade only | `users.username` and `users.username_normalized` are dropped by `0018_username_deprecation`. Historical `0012_password_auth.py` and the `0018` downgrade still mention username because migration history must be reversible. |
| Seed user | `backend/app/seed.py`, `backend/app/services/current_user.py` | Replace with firstName/lastName | Seeded local user has first name `Local`, last name `User`, and derived display name `Local User`; no username fields are seeded. |
| Tests and mock users | Backend and frontend auth/session tests | Replace with firstName/lastName or display-name helper | Active tests no longer post or assert usernames. Migration tests assert username columns are absent from the final schema. |
| Data export current user | `backend/app/services/data_export.py`, `frontend/src/types/dataExport.ts` | Replace with firstName/lastName plus optional metadata | Export metadata now includes first name, last name, display name, salutation, pronouns, and headshot URL. |
| Documentation and readiness copy | README and productization docs | Replace wording | User-facing docs now describe local email/password auth. |
| `handle` search hits | React `handleSubmit`, `handleDownload`, service handler names | Remove entirely | False positives; these are event/function names, not identity handles. |
| `avatar` and `initials` search hits | Repository-wide search | Remove entirely | No active references found. |
| JWT payload search hits | Repository-wide search | Remove entirely | No active JWT payload exists; auth uses HttpOnly server-side session cookies. |
| Stable URL slug dependency | Repository-wide search | Document as follow-up if found | No existing route requires a username-like slug. |

## Remaining Compatibility References

The only remaining `username` references are intentionally outside the active
signup/auth/profile path:

- `backend/alembic/versions/0012_password_auth.py`: historical migration that
  introduced the old nullable username columns.
- `backend/alembic/versions/0018_username_deprecation.py`: upgrade drops the
  old username columns; downgrade recreates them for migration reversibility.
- `backend/tests/test_migrations.py`: negative assertions that username columns
  are not present in the final schema.

These are compatibility/history references, not product identity fields.

