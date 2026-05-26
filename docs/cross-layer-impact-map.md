# Cross-Layer Impact Map

## Purpose

This map records how Layer 11 productization readiness depends on and constrains
the rest of Careero. It should guide future LEAP Recon and implementation
prompts so local-first readiness is not confused with production readiness.

| Layer | What Layer 11 depends on | What Layer 11 must not override | Readiness blockers | Future implementation notes |
| --- | --- | --- | --- | --- |
| Layer 0 Product Foundation | Job-seeker-first posture, AI as advisor, source grounding, marketplace last. | User trust, review-before-send, no-auto-apply, monetization caution. | Any drift toward employer-first incentives. | Productization must preserve Layer 0 principles before pricing or hosting. |
| Layer 1 Local Platform Foundation | FastAPI, React/Vite, PostgreSQL, Alembic, local scripts, seeded local workspace, Layer 11B local current-user context. | Local-first iteration pace or claims that seeded local user equals auth. | Production auth, authorization, tenant isolation, secrets, and environment model. | Hosted modes require fresh auth/tenancy design and tests; Layer 11B service boundaries are prep only. |
| Layer 2 Intake, Parsing & Grounding | Review-before-save parsing, raw/source material, provenance, active source grounding. | User review, source truth, and manual/local import boundaries. | Parser confidence UX and richer provenance remain incomplete. | Production privacy/export must include raw and parsed source records. |
| Layer 3 COMPASS + Artifact Foundation | COMPASS evaluation, prompt/ruleset metadata, generated artifact persistence, TruthGuard checks. | COMPASS advisory nature or private strategy separation. | Artifact lifecycle and review UX are incomplete. | Paid artifact/AI tiers should wait for lifecycle clarity. |
| Layer 4 Application Workflow | Application state machine, history, notes, external links, interviews, reminder foundations. | Application state ownership or reviewable workflow state. | Reminder API/UI reconciliation and count validation. | Production readiness requires coherent workflow records and exports. |
| Layer 5 Workflow Intelligence / Insights | Analytics, recommendations, compensation/source/search health, historical learning. | Confidence limits or source-basis explanation. | Workspace filtering, deterministic validation, and calibration. | Paid analytics must be transparent and avoid overclaiming. |
| Layer 6 Advanced COMPASS + Artifact Lifecycle | Artifact lifecycle direction, evidence mapping, submitted artifact tracking goals. | Employer-facing artifact safety boundaries. | Review/edit/approve/archive, submitted tracking, and frontend export UX. | Monetization should wait until artifacts are durable product objects. |
| Layer 7 Opportunity Model Strategy | Opportunity-facing compatibility and Role-backed persistence documentation. | Destructive Role-to-Opportunity persistence rename. | Compatibility debt and broad `role_id` consumers. | Hosted exports/deletion must account for Role-backed Opportunity records until migration is approved. |
| Layer 8 Integrations | Local export boundary and future integration constraints. | Deferral of OAuth, token storage, background sync, and external account linking. | Frontend artifact export workflow and integration privacy design. | Hosted integrations require auth, secrets, consent, revocation, and audit design. |
| Layer 9 Automation Guardrails | Suggestions, approval logs, workspace preferences, disabled external actions. | Suggestion-first, review-first, audit-first automation. | No external executors, batch approvals, or state-changing automation are approved. | Production automation requires fresh approval and safety review per action class. |
| Layer 10 Advanced Search Tracks / Career Strategy | Read-only strategy synthesis from stored Careero evidence. | Advisory, source-grounded, non-mutating strategy behavior. | Strategy depends on Layer 4/5/6 data maturity. | Strategy may inform paid power-user value only after confidence is calibrated. |
| Layer 11 Productization / Deployment / Monetization | Readiness docs, privacy/account/deployment/cost/monetization gates, local-first current-user boundary prep in workspace/role/application services. | The fact that production auth, hosted tenant isolation, billing, deployment, and collaboration implementation remain future. | Auth, billing, deployment, export/delete, retention, metering, and operations. | Implementation requires new LEAP Recon and explicit approvals; auth-provider selection remains deferred. |
| Layer 12 Advisor / Collaboration Mode | Advisor collaboration readiness design in `docs/advisor-collaboration-mode.md`, local-only redacted packet preview/export scaffolding, deterministic redaction metadata, future account roles, scoped packets, comment boundaries, revocation, and audit. | Privacy boundaries, user ownership, COMPASS advisory/source-grounded limits, and separation of private strategy from shareable material. | No production auth, sharing model, tenant permissions, artifact lifecycle maturity, revocation implementation, or audit implementation. | Hosted collaboration remains blocked; current packet preview/export is local-only and creates no accounts, invitations, comments, public links, external sharing, persisted share records, or permission enforcement claims. |
| Layer 13 Marketplace / Employer-Side Exploration | Future user-controlled visibility and strict disclosure. | Marketplace last, no pay-to-rank, no hidden sponsored steering. | No employer-side model, sharing controls, or trust review. | Employer-side work requires a separate trust and incentive review after user-side value is proven. |

## Productization Impact Rules

- Layer 11 readiness can document gates but must not implement production auth,
  billing, deployment, tenant isolation, or external integrations.
- Layer 11B local current-user context is injectable boundary prep, not login,
  signup, OAuth, session management, JWTs, or hosted tenant isolation
  certification.
- Productization cannot make employer-facing artifacts include internal COMPASS,
  ATS risk, compensation strategy, company commentary, or private rationale.
- Billing and AI quotas must not create hidden sponsored prioritization.
- Opportunity-facing language must keep Role-backed persistence explicit until a
  separate destructive migration is approved.
- Marketplace/employer-side work stays last.
