# Backend

The backend is a local FastAPI application for Careero. It now supports the local platform foundation, first-party local username/password auth, workspace-scoped role intake, COMPASS evaluation, artifact-generation foundations, application workflow persistence, and early analytics surfaces. It is still local-first and not production-auth-hardened.

## PostgreSQL

Create local development and test databases before running migrations. One simple local setup is:

```sql
CREATE ROLE careero WITH LOGIN PASSWORD 'careero';
CREATE DATABASE careero OWNER careero;
CREATE DATABASE careero_test OWNER careero;
```

If PostgreSQL is installed on Windows but `psql` is not on your `PATH`, run it from the PostgreSQL `bin` directory for your installed version.

## Setup

Run from this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edit `.env` for your local machine. The default values are:

```dotenv
CAREERO_APP_NAME=Careero API
CAREERO_ENVIRONMENT=local
CAREERO_DATABASE_URL=postgresql://careero:careero@localhost:5432/careero
CAREERO_TEST_DATABASE_URL=postgresql://careero:careero@localhost:5432/careero_test
CAREERO_ENABLE_AI_EVALUATIONS=false
CAREERO_ENABLE_AI_ROLE_PARSING=false
CAREERO_ENABLE_AI_RESUME_GENERATION=false
CAREERO_ENABLE_AI_COVER_LETTER_GENERATION=false
CAREERO_OPENAI_API_KEY=
CAREERO_OPENAI_DEFAULT_EVALUATION_MODEL=gpt-5-mini
CAREERO_OPENAI_DEFAULT_ROLE_PARSING_MODEL=gpt-5-mini
CAREERO_OPENAI_DEFAULT_RESUME_GENERATION_MODEL=gpt-5-mini
CAREERO_OPENAI_DEFAULT_COVER_LETTER_GENERATION_MODEL=gpt-5-mini
CAREERO_OPENAI_TIMEOUT_SECONDS=30
CAREERO_OPENAI_MAX_OUTPUT_TOKENS=2500
CAREERO_MAX_AI_EVALUATIONS_PER_SESSION=25
CAREERO_LOG_LEVEL=INFO
CAREERO_ENABLE_PASSWORD_AUTH=true
CAREERO_ALLOW_REGISTRATION=true
CAREERO_AUTH_SESSION_COOKIE_NAME=careero_session
CAREERO_AUTH_SESSION_DAYS=14
CAREERO_AUTH_COOKIE_SECURE=false
CAREERO_PASSWORD_MIN_LENGTH=12
```

`CAREERO_OPENAI_API_KEY` is intentionally empty in local setup. Do not commit real secrets.

## Migrate and Seed

Run migrations:

```powershell
python -m alembic upgrade head
```

Seed the default local user:

```powershell
python -m app.seed
```

The seed command is idempotent. It creates or updates `local-user@careero.local` and the canonical job sources, including `manual`, `linkedin_manual`, `recruiter_email`, `greenhouse`, `lever`, `ashby`, `workable`, and `other`.
It also creates a default active workspace used by local workflows when no explicit workspace is supplied.
The seeded local user is not assigned a password and is not a public login path.
Authenticated app use should create a local account through `/api/auth/register`
or the frontend `/register` page. Registered users receive their own workspace
ID; the fixed seeded default workspace ID remains reserved for the seeded local
user.

## Local Authentication API

Password auth is enabled locally by default. Passwords are hashed with
Argon2id via `argon2-cffi`. Sessions are stored server-side with only a
SHA-256 hash of the session token, and the raw token is returned only in an
HttpOnly `SameSite=Lax` cookie. `CAREERO_AUTH_COOKIE_SECURE=false` is the local
default; production-like environments must use HTTPS and harden cookie/session
settings before hosted use.

Routes:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

Google and LinkedIn SSO are not implemented. The frontend login page shows
disabled placeholders only. Account recovery, email verification, MFA, hosted
auth provider selection, and production tenant isolation certification remain
future work.

## Run

```powershell
uvicorn app.main:app --reload
```

Health checks:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/database
```

`/health/database` connects to the PostgreSQL database configured by `CAREERO_DATABASE_URL` and runs a lightweight probe.

## Role Intake API

Role intake is manual-only in this phase. Paste role details discovered from LinkedIn or another source into Careero; the backend does not scrape LinkedIn, poll job boards, or call OpenAI.
Roles belong to exactly one workspace. If `workspace_id` is omitted, Careero uses the current user's first active workspace; for seeded direct-service flows, that is the seeded default workspace.

## Workspace API

Workspaces scope career-search preferences, notes, tags, AI context summary, roles, evaluations, and generated artifacts. Registration creates a default active workspace for the new local account. The local seed also creates a default active workspace for compatibility with existing seed/direct-service flows.

Create a workspace:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/workspaces `
  -ContentType "application/json" `
  -Body '{
    "title": "Staff Engineer full-time search",
    "workspace_type": "full_time_individual_contributor",
    "preferences": {
      "targetTitles": ["Staff Engineer"],
      "preferredRemoteTypes": ["remote"],
      "targetKeywords": ["python", "platform"],
      "notes": "Prioritize senior IC platform roles."
    },
    "ai_context_summary": "Staff Engineer search focused on platform engineering.",
    "tags": ["staff", "platform"],
    "metadata": {
      "contextPreferences": {
        "employmentType": "full_time",
        "preferredIndustries": ["SaaS"],
        "preferredTechnologies": ["Python", "PostgreSQL"]
      }
    }
  }'
```

List active workspaces:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/workspaces
```

Include archived and completed workspaces:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/workspaces?include_inactive=true"
```

Update, archive, and reactivate:

```powershell
Invoke-RestMethod `
  -Method Patch `
  -Uri http://127.0.0.1:8000/api/workspaces/{workspace_id} `
  -ContentType "application/json" `
  -Body '{ "status": "paused", "tags": ["staff", "paused"] }'

Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/workspaces/{workspace_id}/archive
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/workspaces/{workspace_id}/reactivate
```

Archived and completed workspaces remain inspectable, but they are rejected for new roles, evaluations, and artifact generation.

Create a role from a LinkedIn manual paste:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/roles `
  -ContentType "application/json" `
  -Body '{
    "workspace_id": "optional-workspace-uuid",
    "title": "Senior Backend Engineer",
    "company": {
      "name": "Example Company",
      "website_url": "https://example.com"
    },
    "source": {
      "source_type": "linkedin_manual"
    },
    "job_url": "https://www.linkedin.com/jobs/view/example",
    "location": "Chicago, IL",
    "remote_type": "hybrid",
    "compensation_min": "120000.00",
    "compensation_max": "150000.00",
    "compensation_currency": "USD",
    "raw_description": "Paste the original job description here.",
    "normalized_description": null,
    "status": "found",
    "date_found": "2026-05-13",
    "date_posted": "2026-05-01"
  }'
```

List active roles:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/roles
```

Update a role:

```powershell
Invoke-RestMethod `
  -Method Patch `
  -Uri http://127.0.0.1:8000/api/roles/{role_id} `
  -ContentType "application/json" `
  -Body '{ "status": "interested", "remote_type": "remote" }'
```

Archive a role:

```powershell
Invoke-RestMethod -Method Delete http://127.0.0.1:8000/api/roles/{role_id}
```

Company intake accepts either an existing company ID or a name. When a name is supplied, Careero reuses an existing company for the current user using case-insensitive name matching or creates a new company if one does not exist.

### AI-Assisted Role Parsing

AI role parsing is optional and disabled by default. It accepts pasted job content and returns structured fields for user review. It never creates a role by itself.

Enable locally with:

```dotenv
CAREERO_ENABLE_AI_ROLE_PARSING=true
CAREERO_OPENAI_API_KEY=sk-...
CAREERO_OPENAI_DEFAULT_ROLE_PARSING_MODEL=gpt-5-mini
```

Parse a pasted job post:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/roles/parse `
  -ContentType "application/json" `
  -Body '{
    "rawText": "Paste messy LinkedIn, recruiter, job board, or company site content here.",
    "source": "linkedin_manual",
    "jobUrl": "https://example.com/jobs/123"
  }'
```

The response contains `parsed` role fields and `metadata` with `parserVersion` and model. Missing values are `null`. Compensation, company URLs, dates, and remote type are only returned when explicitly present in the pasted content. Invalid AI output returns `502`; disabled or unconfigured parsing returns `503`.

When a user saves a parsed role, the frontend sends `parse_metadata` with parser version, model, parse timestamp, warnings, confidence, extracted skills, and fields edited after parsing. The original pasted content is preserved in `raw_description`; normalized text is stored separately in `normalized_description`.

## Resume/Profile Source API

Careero can store a local master resume or profile source for grounded COMPASS evaluation and artifact generation. Source text can be pasted manually or imported from a local file for preview. File import extracts text only; it does not persist uploaded files or create a source until the user explicitly saves one. This API does not import external profiles, extract profile facts, generate resumes, or generate cover letters.

Import a local resume/profile file:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/resume-sources/import `
  -Form @{ file = Get-Item .\resume.pdf }
```

Supported import formats are `.txt`, `.md`, `.docx`, and text-based `.pdf` files up to `5 MB`. PDFs must contain embedded selectable text. Scanned/image-only PDFs fail with a clear error because OCR is not implemented. Import rejects unsupported extensions, unsupported MIME types, oversized files, and files with no readable text. The response includes extracted text, file name, file type, content type, size, character count, and warnings.

Document parsing uses lightweight Python dependencies: `python-docx` for `.docx`, `pypdf` for text-based PDFs, and `python-multipart` for FastAPI multipart uploads.

Google Docs import is a future backlog item. It requires Google OAuth, Drive/Docs scope selection, document export, token handling, permission review, and a security design.

Create a master resume source with an active initial version:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/resume-sources `
  -ContentType "application/json" `
  -Body '{
    "name": "Master Resume",
    "source_type": "master_resume",
    "version_label": "v1",
    "raw_text": "Paste the master resume or profile text here.",
    "normalized_summary": "Optional concise summary of the profile.",
    "is_active": true
  }'
```

List sources:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/resume-sources
```

Get the active source version:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/resume-sources/active
```

Create a new version:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/resume-sources/{source_id}/versions `
  -ContentType "application/json" `
  -Body '{
    "version_label": "v2",
    "raw_text": "Updated master resume or profile text.",
    "normalized_summary": "Updated optional summary.",
    "is_active": false
  }'
```

Activate a version:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/resume-sources/{source_id}/versions/{version_id}/activate
```

Update source metadata:

```powershell
Invoke-RestMethod `
  -Method Patch `
  -Uri http://127.0.0.1:8000/api/resume-sources/{source_id} `
  -ContentType "application/json" `
  -Body '{ "name": "Updated Master Resume", "source_type": "profile" }'
```

Only one resume source version can be active for the current user. COMPASS evaluation can still run without an active source, but OpenAI enrichment includes the active source when present.

## COMPASS Evaluation API

COMPASS evaluation support always starts with deterministic local rules. The deterministic score remains the canonical baseline. Optional OpenAI enrichment can add grounded structured analysis, but it does not replace the baseline score, infer resume facts, generate resumes or cover letters, scrape jobs, poll sources, or perform external research.

COMPASS uses the target role's workspace context. Workspace preferences are merged into evaluation context, and explicit request `user_context` values override workspace defaults for that run. Workspace context is included in prompt metadata and the evaluation input hash so cache results do not bleed across searches.

The first-pass dimensions are equally weighted:

- strategic fit
- technical alignment
- seniority alignment
- compensation alignment
- remote/location alignment
- company signal
- role clarity
- application effort
- ATS/resume alignment
- risk flags

Overall scores are `0` to `100`. Recommendation thresholds are intentionally conservative:

- `apply`: score `75+`, medium or high confidence, and no severe risk flags
- `monitor`: score `55-74` with acceptable risk
- `needs_review`: score `40-54`, low confidence, or conflicting signals
- `skip`: score below `40` or severe risk flags

Confidence is based on input completeness. A high-confidence baseline needs title, company, description, location or remote information, compensation, enough description text, and request-scoped context. Missing context lowers confidence instead of inventing a mismatch.

The create request can include optional `user_context` hints:

```json
{
  "preferred_remote_type": "remote",
  "target_compensation_min": "130000",
  "target_seniority": "senior",
  "target_keywords": ["python", "postgresql", "fastapi"],
  "avoid_keywords": ["php"],
  "preferred_locations": ["chicago"]
}
```

Rule-based concerns currently detect missing compensation, unclear seniority, hybrid/on-site mismatch, vague responsibilities, excessive technology sprawl, and suspiciously generic descriptions. The full scoring breakdown is stored in `raw_evaluation_json`.

### Optional OpenAI Enrichment

AI enrichment is disabled by default. To enable it locally, set:

```dotenv
CAREERO_ENABLE_AI_EVALUATIONS=true
CAREERO_OPENAI_API_KEY=sk-...
CAREERO_OPENAI_DEFAULT_EVALUATION_MODEL=gpt-5-mini
CAREERO_OPENAI_TIMEOUT_SECONDS=30
CAREERO_OPENAI_MAX_OUTPUT_TOKENS=2500
CAREERO_MAX_AI_EVALUATIONS_PER_SESSION=25
```

When enabled, Careero uses the OpenAI Responses API with structured output validation. The prompt includes only stored role fields, the deterministic baseline, COMPASS rules, request `user_context`, and the active resume/profile source version when one exists. If OpenAI is unavailable, times out, or returns invalid structured output, the evaluation still succeeds with deterministic results and stores `ai_status` as `failed` or `skipped` in `raw_evaluation_json`.

`CAREERO_MAX_AI_EVALUATIONS_PER_SESSION` is a simple local cost control. It limits OpenAI-backed evaluation attempts per backend process and resets when the backend restarts. Cached evaluations, AI-disabled runs, and missing-key skipped runs do not consume the counter.

AI output stores grounding details in `raw_evaluation_json.ai_result`, including `evidence_matches`, `evidence_gaps`, `positioning_opportunities`, and `unsupported_claim_warnings`. The prompt requires the model to distinguish `strong_match`, `partial_match`, `no_evidence`, and `insufficient_data`.

### Evaluation Audit Metadata and Caching

Each COMPASS evaluation stores audit metadata:

- `model_used`, `prompt_version`, and `ruleset_version`
- input/output token estimates when usage is available or can be approximated
- `latency_ms`, `ai_enabled`, `ai_status`, and sanitized `error_message`
- `role_content_hash`, `source_hash`, and `evaluation_input_hash`

The cache key uses stable role content, active resume/profile source content, request notes/context, prompt version, ruleset version, AI enabled state, and model name. If those inputs have not changed, `POST /api/roles/{role_id}/evaluations` returns the cached latest completed evaluation with HTTP `200`. To explicitly re-run and create a new row, send `"force": true`.

Careero logs evaluation lifecycle activity for `compass_evaluation.started`, `compass_evaluation.completed`, `compass_evaluation.failed`, and `compass_evaluation.cached_result_reused`. Logs and stored errors must not include API keys, full prompts, raw job descriptions, or full resume/profile text.

Create a baseline evaluation for a role. If AI enrichment is enabled and configured, the same endpoint also stores grounded AI analysis:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/roles/{role_id}/evaluations `
  -ContentType "application/json" `
  -Body '{
    "user_notes": "Baseline review before AI enrichment.",
    "force": false,
    "user_context": {
      "preferred_remote_type": "remote",
      "target_compensation_min": "130000",
      "target_seniority": "senior",
      "target_keywords": ["python", "postgresql", "fastapi"]
    }
  }'
```

Force a re-run even when the same inputs have already been evaluated:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/roles/{role_id}/evaluations `
  -ContentType "application/json" `
  -Body '{ "force": true }'
```

Get the latest evaluation for a role:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/roles/{role_id}/evaluations/latest
```

List evaluations:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/compass-evaluations
Invoke-RestMethod "http://127.0.0.1:8000/api/compass-evaluations?evaluation_status=completed"
```

Get one evaluation by ID:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/compass-evaluations/{evaluation_id}
```

Inspect activity log entries for an evaluation:

```powershell
Invoke-RestMethod `
  "http://127.0.0.1:8000/api/activity-log?entity_type=compass_evaluation&entity_id={evaluation_id}"
```

The activity log is scoped to the authenticated current user when password auth is enabled, and to the seeded default local user only in seed/direct-service/auth-disabled test paths. It supports optional `entity_type`, `entity_id`, `action`, and `limit` query parameters. The default limit is `50`; the maximum is `200`.

## Layer 2 Local Flow

1. Create a role manually with `POST /api/roles`.
2. Create and activate a resume/profile source with `POST /api/resume-sources`.
3. Run COMPASS evaluation with `POST /api/roles/{role_id}/evaluations`.
4. Open `http://127.0.0.1:5173/roles/{role_id}` to view the evaluation.
5. Run the same request again to reuse the cached evaluation, or send `"force": true` to create a new run.
6. Inspect lifecycle events with `GET /api/activity-log`.

The original Layer 2 local flow does not add automated discovery, generated application packets, or application submission. Local username/password auth now exists separately from those intake workflows. Backend resume and cover-letter artifact generation foundations now exist separately as draft-only services; frontend rendering, review/approval lifecycle, and submission remain future work. Local Markdown/DOCX/PDF export is available for stored generated artifacts.

## Resume Artifact Generation

Resume artifact generation is optional and disabled by default. It creates a validated canonical `ResumeArtifact` draft for a supplied `workspace_id`, target role/opportunity, COMPASS evaluation, and active or requested resume source version. The supplied workspace must exist, be active or paused, and own the target role/opportunity. It does not render resumes in the frontend.

Enable locally with:

```dotenv
CAREERO_ENABLE_AI_RESUME_GENERATION=true
CAREERO_OPENAI_API_KEY=sk-...
CAREERO_OPENAI_DEFAULT_RESUME_GENERATION_MODEL=gpt-5-mini
```

Generate a tailored resume artifact:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/opportunities/{opportunity_id}/resume-artifacts `
  -ContentType "application/json" `
  -Body '{
    "workspace_id": "22222222-2222-4222-8222-222222222222",
    "evaluation_id": "optional-compass-evaluation-uuid",
    "source_version_id": "optional-resume-source-version-uuid"
  }'
```

If `evaluation_id` is omitted, Careero uses the latest COMPASS evaluation for the role. If `source_version_id` is omitted, it uses the active resume source version. Missing role/evaluation/source references return `404`. Disabled or unconfigured AI resume generation returns `503` and persists no artifact. Provider failures, invalid structured output, canonical schema failures, and truthfulness violations return `502` and persist no artifact.

The legacy `/api/roles/{role_id}/resume-artifacts` route remains available as a compatibility alias while persistence is Role-backed.

The generated resume is stored in `generated_artifacts`, with the complete canonical artifact in `metadata.contract`. Source lineage, target evaluation linkage, revision metadata, generation metadata, and content hashes are preserved. The prompt and validation layers enforce the non-fabrication rule: employers, roles, technologies, metrics, accomplishments, credentials, and experience must come from the supplied resume/profile source or explicit user-provided inputs.

## Cover Letter Artifact Generation

Cover letter artifact generation is optional and disabled by default. It creates a validated canonical `CoverLetterArtifact` draft for a supplied `workspace_id` and target role/opportunity. The supplied workspace must exist, be active or paused, and own the target role/opportunity. COMPASS evaluation and resume/profile source inputs are used when available, but missing evaluation or missing source does not block generation; the artifact records warnings in generation metadata.

The default tone is `direct`, which maps to Careero's neutral, forward-looking professional standard for cold applications. Generated openings must avoid overly enthusiastic phrasing such as "I'm excited to apply."

Enable locally with:

```dotenv
CAREERO_ENABLE_AI_COVER_LETTER_GENERATION=true
CAREERO_OPENAI_API_KEY=sk-...
CAREERO_OPENAI_DEFAULT_COVER_LETTER_GENERATION_MODEL=gpt-5-mini
```

Generate a cover letter artifact:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/opportunities/{opportunity_id}/cover-letter-artifacts `
  -ContentType "application/json" `
  -Body '{
    "workspace_id": "22222222-2222-4222-8222-222222222222",
    "evaluation_id": "optional-compass-evaluation-uuid",
    "source_version_id": "optional-resume-source-version-uuid",
    "tone": "direct"
  }'
```

If `evaluation_id` is omitted, Careero uses the latest COMPASS evaluation when one exists. If `source_version_id` is omitted, it uses the active resume source version when one exists. Explicit missing role/evaluation/source references return `404`. Disabled or unconfigured AI cover letter generation returns `503` and persists no artifact. Provider failures, invalid structured output, canonical schema failures, tone violations, and truthfulness violations return `502` and persist no artifact.

The legacy `/api/roles/{role_id}/cover-letter-artifacts` route remains available as a compatibility alias while persistence is Role-backed.

The generated cover letter is stored in `generated_artifacts`, with the complete canonical artifact in `metadata.contract`. Opportunity linkage, optional source lineage, optional target evaluation linkage, tone metadata, generation metadata, and revision metadata are preserved.

## Local Artifact Export

Stored generated artifacts can be exported locally without OAuth, cloud storage, or external account linking. Export returns a generated file and records local export metadata on the stored artifact contract.

```powershell
Invoke-WebRequest `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/artifacts/{artifact_id}/exports/md `
  -OutFile artifact.md

Invoke-WebRequest `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/artifacts/{artifact_id}/exports/docx `
  -OutFile artifact.docx

Invoke-WebRequest `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/artifacts/{artifact_id}/exports/pdf `
  -OutFile artifact.pdf
```

Export is local-only. It does not send email, write to Google Docs, sync cloud storage, or mutate external systems.

## Local Advisor Packet Preview

Layer 12 advisor packet preview is local-only and owner-visible. It returns a
redacted packet summary for an existing application workflow and can export that
summary as Markdown. It does not create hosted access, advisor accounts,
invitations, comments, public links, external sharing, or employer/recruiter
visibility.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/applications/{application_id}/advisor-packet

Invoke-WebRequest `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/applications/{application_id}/advisor-packet/exports/md `
  -OutFile advisor-packet.md
```

Default packet output includes basic opportunity/application summaries and
artifact lifecycle summaries only. Private notes, raw job descriptions, COMPASS
rationale, ATS risk notes, compensation strategy, recruiter/contact details,
source resume/profile material, career strategy synthesis, activity logs,
automation approval logs, and generated artifact content are excluded by
default.

Explicit local preview options use a non-persisted POST body:

```powershell
Invoke-RestMethod `
  -Method Post `
  -ContentType "application/json" `
  -Uri http://127.0.0.1:8000/api/applications/{application_id}/advisor-packet/preview `
  -Body '{"artifact_ids":[],"external_link_ids":[],"interview_stage_ids":[],"reminder_ids":[],"advisor_context":"Review positioning only."}'
```

## Career Strategy API

Layer 10 strategy synthesis is read-only and workspace-scoped. It uses stored
Careero evidence only and does not create strategy tables, automation
suggestions, external market data, or employer-facing artifacts.

```text
GET http://127.0.0.1:8000/api/strategy/workspaces/{workspace_id}
GET http://127.0.0.1:8000/api/strategy/workspaces?include_cross_track=true
```

The response includes summary, basis, confidence, sample size, source inputs,
known uncertainty, insufficient-data reasons, strategy signals, compensation
alignment, skill-gap themes, role positioning, career narrative themes,
retrospective text, advisory action candidates, and warnings.

## Application Workflow Persistence

Application workflow builds on saved roles. `Role.status` remains a lightweight opportunity status for existing role lists, while `Application.current_state` is the workflow authority and uses the canonical states `discovered`, `interested`, `applied`, `interviewing`, `offer`, `rejected`, `withdrawn`, and `archived`.

Create or return the workflow for a role:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/roles/{role_id}/application
```

List workflows:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/applications
Invoke-RestMethod "http://127.0.0.1:8000/api/applications?include_inactive=true"
Invoke-RestMethod "http://127.0.0.1:8000/api/applications?workspace_id={workspace_id}"
Invoke-RestMethod http://127.0.0.1:8000/api/workspaces/{workspace_id}/applications
```

List workflows grouped for the Applications pipeline:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/applications/pipeline
Invoke-RestMethod "http://127.0.0.1:8000/api/applications/pipeline?include_inactive=true"
Invoke-RestMethod http://127.0.0.1:8000/api/workspaces/{workspace_id}/applications/pipeline
```

Get workflow detail:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/applications/{application_id}
```

Get the application timeline:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/applications/{application_id}/timeline
```

The timeline is a read-only view over typed workflow persistence. It includes
application creation, state history, notes, reminders, interview stages,
completed COMPASS evaluations, generated resume and cover-letter artifacts, and
selected ActivityLog update/delete events. It does not store duplicate timeline
rows and does not expose raw prompts, source resume text, generated document
content, or raw model payloads.

Manage workflow notes:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/applications/{application_id}/notes

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/applications/{application_id}/notes `
  -ContentType "application/json" `
  -Body '{
    "note_type": "recruiter",
    "body": "Ask about team scope and hiring timeline."
  }'

Invoke-RestMethod `
  -Method Patch `
  -Uri http://127.0.0.1:8000/api/applications/{application_id}/notes/{note_id} `
  -ContentType "application/json" `
  -Body '{ "note_type": "follow_up", "body": "Follow up next week." }'

Invoke-RestMethod `
  -Method Delete `
  -Uri http://127.0.0.1:8000/api/applications/{application_id}/notes/{note_id}
```

Supported note types are `general`, `recruiter`, `compensation`, `follow_up`,
and `interview`. Notes are for freeform workflow context; reminders and
interview stages remain separate typed concepts.

Manage external links:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/applications/{application_id}/links

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/applications/{application_id}/links `
  -ContentType "application/json" `
  -Body '{
    "label": "Application portal",
    "url": "https://example.com/apply",
    "type": "application_portal"
  }'

Invoke-RestMethod `
  -Method Patch `
  -Uri http://127.0.0.1:8000/api/applications/{application_id}/links/{link_id} `
  -ContentType "application/json" `
  -Body '{ "label": "Updated portal", "type": "application_portal" }'

Invoke-RestMethod `
  -Method Delete `
  -Uri http://127.0.0.1:8000/api/applications/{application_id}/links/{link_id}
```

Suggested link types are `job_posting`, `company_careers`,
`recruiter_profile`, `application_portal`, `interview_prep`, `email_thread`,
and `other`. Link URLs are validated. Deleting notes or links soft-deletes the
row: active lists and counts exclude the record, while safe create/update/delete
events remain available in the timeline.

List endpoints return compact summaries for the Applications page: role title,
company, current state, application dates, latest COMPASS status, latest resume
and cover letter artifact summaries, and note/reminder/interview counts. They do
not return full COMPASS or artifact payloads and do not trigger generation.

Update workflow metadata or dates without changing state:

```powershell
Invoke-RestMethod `
  -Method Patch `
  -Uri http://127.0.0.1:8000/api/applications/{application_id} `
  -ContentType "application/json" `
  -Body '{
    "workflow_metadata": { "priority": "high" },
    "next_action_at": "2026-05-20T15:00:00Z"
  }'
```

Change workflow state:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/applications/{application_id}/state-transitions `
  -ContentType "application/json" `
  -Body '{ "state": "interviewing", "reason": "Recruiter screen scheduled." }'
```

Allowed workflow transitions are enforced by the backend:
`discovered -> interested|withdrawn|archived`,
`interested -> applied|withdrawn|archived`,
`applied -> interviewing|rejected|withdrawn|archived`,
`interviewing -> offer|rejected|withdrawn|archived`,
`offer -> withdrawn|archived`, `rejected -> archived`, and
`withdrawn -> archived`. Reactivating an archived workflow requires
`"reactivate": true` and can move only to `discovered` or `interested`.

Applications are workspace-scoped. New workflows can only be created for roles in active or paused workspaces; archived/completed workspaces remain inspectable with `include_inactive=true`. State history, notes, reminders, interview stages, and external links use typed tables. `ActivityLog` records broad audit events and note/link update-delete events but does not replace workflow persistence. Existing role statuses are backfilled into application workflows during migration, and existing application notes are copied into typed notes.

Future automation may suggest application workflow changes, but it must not silently mutate `Application.current_state`.

## Test

Run tests:

```powershell
$env:CAREERO_TEST_DATABASE_URL="postgresql://careero:careero@localhost:5432/careero_test"
pytest
```

Database-backed tests run Alembic migrations against `CAREERO_TEST_DATABASE_URL` and reset the known Careero schema in that test database.
