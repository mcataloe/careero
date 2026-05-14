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

The Add Role page includes optional AI-assisted parsing:

- Paste a full job post into `Paste job description`.
- Optionally provide the posting URL and source.
- Click `Parse role`.
- Review/edit the populated manual fields.
- Click `Create role` to save.

Parsing fills empty fields only, does not auto-save, and keeps manual edits intact. The backend must have `CAREERO_ENABLE_AI_ROLE_PARSING=true` and an OpenAI API key configured for parsing to run.

STRIDE evaluation workflow:

- Open a role at `/roles/:roleId`.
- Use the compact section navigation near the top of the role detail page to jump between overview, descriptions, edit controls, STRIDE evaluation, and major STRIDE sections.
- Use `Run STRIDE evaluation` for a role with no evaluation.
- Use `Re-run evaluation` to force a new latest evaluation.
- Use `View latest evaluation` to jump to the evaluation section.
- The role list shows a non-blocking evaluation indicator for each role.
- A normal run may reuse the backend cache when role/source/context inputs have not changed.
- Completed evaluations render through section blocks for summary, fit analysis, strengths, gaps, risks, ATS findings, compensation, remote fit, interview positioning, recommendations, and assumptions/confidence.
- Long STRIDE text uses the shared `ExpandableTextSection` pattern so the role detail page stays scannable without hiding full content.

Resume/profile grounding source:

- Open `/settings`.
- Create an active local `master_resume` source by pasting source text or importing a local file.
- File import supports `.txt`, `.md`, `.docx`, and text-based `.pdf` files up to 5 MB.
- Imported text is copied into the editable raw text field and is not saved until you submit the form.
- When an active source exists, submit a new version to replace the active version.
- The backend uses the active source to ground STRIDE evaluations when available.

Careero does not run OCR, import Google Docs, generate resumes, cover letters, application packets, or automated discovery output from this UI phase.

Run component tests:

```powershell
npm run test
```

Build validation:

```powershell
npm run build
```

If PowerShell blocks `npm`, use `npm.cmd`.
