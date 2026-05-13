# Frontend

The frontend is a local React + Vite + TypeScript application for Careero. It uses Mantine for UI components and talks to the backend through the Vite `/api` proxy.

Run from this directory:

```powershell
npm install
npm run dev
```

The frontend expects the backend at:

```text
http://127.0.0.1:8000
```

Before using role intake, STRIDE evaluations, or resume/profile source settings, run the backend database setup:

```powershell
cd ..\backend
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

AI enrichment is controlled by backend configuration. The frontend works with the deterministic backend fallback when AI is disabled, missing, or unavailable.

Manual role intake is available at:

```text
http://127.0.0.1:5173/roles/new
```

STRIDE evaluation workflow:

- Open a role at `/roles/:roleId`.
- Use `Run STRIDE evaluation` for a role with no evaluation.
- Use `Re-run evaluation` to create a new latest evaluation.
- Use `View latest evaluation` to jump to the evaluation section.
- The role list shows a non-blocking evaluation indicator for each role.

Resume/profile grounding source:

- Open `/settings`.
- Create an active local `master_resume` source by pasting source text.
- When an active source exists, submit a new version to replace the active version.
- The backend uses the active source to ground STRIDE evaluations when available.

Careero does not generate resumes, cover letters, application packets, or automated discovery output from this UI phase.

Run component tests:

```powershell
npm run test
```

Build validation:

```powershell
npm run build
```

If PowerShell blocks `npm`, use `npm.cmd`.
