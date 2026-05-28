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

Before using opportunity intake, COMPASS evaluations, or resume/profile source settings, run the backend database setup:

```powershell
cd ..\backend
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Open `/register` to create a local email/password account, or `/login` to
sign in. The session is held in an HttpOnly backend cookie; the frontend does
not store session tokens in local storage. Google and LinkedIn buttons on the
login page are disabled "coming soon" placeholders only and do not trigger
OAuth or external redirects.

App shell navigation:

- Authenticated pages use a compact header with a hamburger button for the
  global Careero navigation.
- The floating global navigation contains only implemented top-level
  destinations: Dashboard, Career strategy, Opportunities, Applications, and
  Settings.
- Feature-specific navigation stays inside the feature workspace instead of
  taking permanent global sidebar width.
- Dashboard, Career strategy, Settings, opportunity detail, and application
  detail use deep-linkable local subsection routes with one focused detail panel
  visible at a time.

Dashboard workspace:

- Open `/dashboard` to enter the dashboard overview.
- Dashboard subsection routes use `/dashboard/:section` for overview, COMPASS,
  sources, compensation, search health, recommendations, automation, artifacts,
  and history.
- Each dashboard subsection loads its own analytics data when opened.

AI enrichment is controlled by backend configuration. The frontend works with the deterministic backend fallback when AI is disabled, missing, or unavailable.

Manual opportunity intake is available at:

```text
http://127.0.0.1:5173/opportunities/new
```

The Add opportunity page includes optional AI-assisted parsing:

- Paste a full job post into `Paste job description`.
- Optionally provide the posting URL and source.
- Click `Parse opportunity`.
- Review/edit the populated manual fields.
- Click `Create opportunity` to save.

Parsing fills empty fields only, does not auto-save, and keeps manual edits intact. The backend must have `CAREERO_ENABLE_AI_ROLE_PARSING=true` and an OpenAI API key configured for parsing to run.

COMPASS evaluation workflow:

- Open an opportunity at `/opportunities/:opportunityId`; it redirects to
  `/opportunities/:opportunityId/overview`.
- Opportunity detail subsection routes use
  `/opportunities/:opportunityId/:section` for overview, intelligence,
  description, edit, and COMPASS.
- Use `Run COMPASS evaluation` for an opportunity with no evaluation.
- Use `Re-run evaluation` to force a new latest evaluation.
- Use `View latest evaluation` to jump to the COMPASS section.
- The opportunity list shows a non-blocking evaluation indicator for each opportunity.
- A normal run may reuse the backend cache when opportunity/source/context inputs have not changed.
- Completed evaluations render through section blocks for summary, fit analysis, strengths, gaps, risks, ATS findings, compensation, remote fit, interview positioning, recommendations, and assumptions/confidence.
- Long COMPASS text uses the shared `ExpandableTextSection` pattern so the opportunity detail page stays scannable without hiding full content.

Resume/profile grounding source:

- Open `/settings/resume-source`.
- Create an active local `master_resume` source by pasting source text or importing a local file.
- File import supports `.txt`, `.md`, `.docx`, and text-based `.pdf` files up to 5 MB.
- Imported text is copied into the draft raw text field and is not saved until you submit the form.
- When an active source exists, the settings page is read-only by default. Use `Create new version` or `Import file` to enter draft editing.
- Canceling a draft restores the currently active source values. Saving an active-source draft creates and activates a new version; it does not mutate the existing version in place.
- The backend uses the active source to ground COMPASS evaluations when available.

Application workflow:

- Open `/applications` to view application workflows grouped by pipeline state.
- Open `/applications/:applicationId`; it redirects to
  `/applications/:applicationId/overview`.
- Application detail subsection routes use
  `/applications/:applicationId/:section` for overview, interviews, reminders,
  suggestions, advisor packet, notes, links, and timeline.
- Structured interview tracking is manual-only; calendar invites, meeting generation, email, and coaching are intentionally out of scope.
- Application detail includes a local-only advisor packet preview with Markdown export. It is redacted by default and does not create hosted sharing, advisor accounts, invitations, comments, or public links.
- Local reminder management is available from application detail for listing, creating, editing, and completing reminders. Reminders remain local workflow records only; hosted scheduling, notifications, calendar sync, and email delivery are not implemented.

Settings workspace:

- Open `/settings` to enter the runtime subsection.
- Settings subsection routes use `/settings/:section` for runtime, readiness,
  data export, account lifecycle, AI usage, plan, automation, and resume source.
- Settings subsections mount only the active panel, so readiness, usage,
  entitlement, export, lifecycle, automation, and resume-source APIs are not all
  called on entry.

Career strategy:

- Open `/strategy` to enter the read-only strategy workspace.
- Strategy subsection routes use `/strategy/:section` and workspace-scoped
  deep links use `/workspaces/:workspaceId/strategy/:section`.
- The local Career strategy sidebar routes between overview, retrospective,
  compensation, role positioning, skill gaps, career narrative, strategy
  signals, action candidates, uncertainty, and internal cross-track comparison.
- The right-hand detail panel displays only the selected subsection so the
  workspace does not expose every strategy section at once.
- Strategy synthesis is based only on stored Careero data. It does not export
  employer-facing content, mutate records, create automation suggestions, or use
  external market data.

Long and structured text:

- Read-only resume/profile, opportunity description, and COMPASS text uses expandable preview blocks so pages stay scannable without hiding full content.
- Markdown-like text is rendered safely as React text nodes. Basic headings, bullets, numbered lists, paragraphs, and fenced code blocks are displayed with lightweight structure.
- Editable long text fields use bounded autosizing instead of expanding without limit.

Careero does not run OCR, import Google Docs, create hosted/shared application packets, or perform automated discovery output from this UI phase. Backend local artifact export APIs exist for Markdown, DOCX, and PDF, and local-only advisor packet Markdown export exists from application detail, but dedicated frontend artifact generation, review, approval, archive, and export workflows are still future/incomplete.

Run component tests:

```powershell
npm run test
```

Build validation:

```powershell
npm run build
```

If PowerShell blocks `npm`, use `npm.cmd`.
