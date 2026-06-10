# Opportunity Model Strategy

Status: Active  
Doc Type: Domain Design  
Layer: Layer 7  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/05_security-privacy-governance/canonical-domain-model.md
- docs/02_layers/00_layer-index.md
Layer 7A design artifact.

This document defines Careero's Opportunity model strategy before any destructive persistence migration. It is the source of truth for Layer 7B compatibility work and later Layer 7C migration decisions.

Layer 7B status: the Opportunity-facing compatibility surface is hardened for the current local MVP scope. `/api/opportunities` and frontend `/opportunities` routes are the canonical outward surfaces, while `/api/roles` and legacy `/roles` frontend paths remain compatibility surfaces. Persistence remains Role-backed for now, and the destructive Layer 7C persistence migration remains deferred.

## 1. Purpose

Layer 7 exists because Careero's next strategic bottleneck is not external ingestion. The bottleneck is the durable model for the thing a user evaluates, pursues, pauses, archives, compares, and learns from.

Today, the backend and UI mostly call that thing a `Role`. Product strategy now needs a broader `Opportunity` object before Layer 8 integrations begin. Integrations will introduce recruiter leads, referrals, job-board saves, email-derived leads, calendar context, imported postings, and possible duplicates. Those inputs need a stable local object that can preserve source truth, parse confidence, provenance, workflow links, and historical intelligence without confusing application state or artifact lifecycle state.

Opportunity should become Careero's central durable intelligence object.

## 2. Current Implementation Reality

- `Role` is the current backend and persistence object.
- The `roles` table currently stores job/opportunity-like records.
- `/api/opportunities` now provides Opportunity-facing aliases for intake, parse, list, detail, update, opportunity intelligence refresh, and archive behavior.
- `/api/opportunities/parse` and `/api/roles/parse` share the same parser and safe AI usage-event recording path.
- `/api/roles` remains available as a compatibility surface for existing local workflows and tests.
- Frontend `/opportunities`, `/opportunities/new`, and `/opportunities/:opportunityId` routes are canonical; legacy `/roles` routes redirect to the Opportunity routes.
- `role_id` is currently used by COMPASS evaluations, Applications, GeneratedArtifacts, artifact performance records, analytics, source intelligence, and historical learning services.
- `OpportunitySchema` already exists in `packages/contracts/src/opportunity.ts`.
- `OpportunityStatusSchema`, `ApplicationWorkflowStateSchema`, and `ArtifactLifecycleStatusSchema` already exist in `packages/contracts/src/enums.ts`.
- `OpportunityIntelligenceService` already exists in the backend, but it is currently Role-backed and stores intelligence under `Role.parse_metadata["opportunityIntelligence"]`.
- User-visible primary intake/list/detail labels now use Opportunity language, while internal component/type names may remain Role-backed during the compatibility phase.
- Frontend Opportunity types are explicit aliases over the temporary Role-backed response shapes.

## 3. Opportunity Definition

An Opportunity is any role, contract, consulting engagement, recruiter lead, referral, job posting, or professional possibility that the user may evaluate, track, pursue, pause, archive, compare, or learn from.

Opportunity is broader than a job posting and broader than an application. A user can save an Opportunity before applying, evaluate it without applying, create artifacts for it, attach an application workflow to it, revisit it later, compare it with other opportunities, or archive it as historical search intelligence.

## 4. Opportunity Responsibilities

Opportunity owns:

- Raw source content.
- Normalized role/opportunity fields.
- Company or employer context.
- Compensation, location, remote mode, and employment type.
- Source and provenance metadata.
- Recruiter and source intelligence when known.
- Parse confidence and parse warnings.
- Deduplication and similarity signals.
- Opportunity/listing status.
- Links to COMPASS evaluations.
- Links to application workflows.
- Links to generated artifacts.
- Historical intelligence metadata used for analytics and retrospectives.

## 5. Opportunity Non-Responsibilities

Opportunity does not own:

- Application workflow state transitions.
- Application state history.
- Reminder completion lifecycle.
- Interview stage lifecycle.
- Artifact lifecycle state.
- Submitted or exported artifact records.
- Automation approvals.
- External communication sending.
- Marketplace or employer-side visibility.

Those responsibilities belong to Application, Artifact, Automation Approval, integration adapters, or future employer-side product surfaces.

## 6. Boundary Matrix

| Object | Owns | Must Not Own | Current Implementation Object | Migration Notes |
| --- | --- | --- | --- | --- |
| Workspace/Search Track | Career objective context, preferences, AI memory summary, search-track lifecycle, scoped analytics context | Individual opportunity parsing details, application state transitions, artifact lifecycle | `workspaces` table and workspace contracts | Keep as parent context for opportunities; do not move opportunity facts into workspace memory. |
| Opportunity | Saved professional possibility, raw and normalized content, company/source/provenance, listing status, parse warnings, dedupe signals, links outward | Application state history, interview/reminder lifecycle, artifact review/submit/archive lifecycle, sending actions | `Role` model and `roles` table; `OpportunitySchema` contract exists | Canonical product language should become Opportunity; current physical storage can remain `roles` during staged migration. |
| Application | Pursuit workflow, current state, state history, notes, reminders, interview stages, application-specific external links and timeline | Raw posting truth, dedupe identity, artifact lifecycle, COMPASS scoring internals | `Application` model with `role_id` | Keep one active workflow per opportunity unless a future requirement justifies multiple workflows. Rename FK later only after API/UX transition is stable. |
| COMPASS Evaluation | Fit/risk evaluation output, ruleset and prompt metadata, input hashes, recommendation, explainability | Source parsing, application workflow state, artifact approval state | `CompassEvaluation` model with `role_id` | It should link to Opportunity, but evaluation semantics do not change during naming migration. |
| Resume/Cover Letter Artifact | Generated draft content, source grounding, truthfulness checks, contract metadata, lifecycle status | Opportunity source truth, application state, export/submission records | `GeneratedArtifact` model with `role_id`; artifact contracts use `opportunityId` | Keep artifacts linked to target opportunity. Export/submitted records remain separate future work. |
| Source/Provenance | Source type, label, URL, external reference, content hash, imported timestamp, parser version, parse warnings | Application decisions, opportunity status, recruiter relationship lifecycle | `JobSource`, `Role.source_id`, `Role.job_url`, `parse_metadata` | Preserve existing `job_sources`; consider normalizing richer provenance later instead of hiding it only in metadata. |
| Recruiter/Contact | Human/source identity, relationship context, referral or recruiter signals, notes relevant to sourcing | Opportunity identity, application state, automated communications | No dedicated recruiter/contact model; notes and source labels are partial substitutes | Future Layer 8 may need contact/source entities, but Layer 7B should avoid overbuilding before integrations. |
| External Link | User-saved URLs for applications, postings, artifacts, company pages, or communications | Canonical source truth by itself, workflow state, dedupe identity by itself | Application external links exist; `Role.job_url` stores posting URL | Keep application links for workflow support; canonical source URL should live on Opportunity/provenance. |
| Automation Approval, future Layer 9 | Approval requests, approval decisions, actor, timestamp, proposed automation action, audit trail | Opportunity parsing truth, application state as unreviewed side effect, external sending without approval | Not implemented | Must reference Opportunity/Application/Artifact as targets without owning their core state. |

## 7. Role-to-Opportunity Mapping

| Current implementation | Future Opportunity meaning | Notes |
| --- | --- | --- |
| `roles.id` | `opportunities.id` | Stable identity for the saved professional possibility. Existing references should preserve IDs through migration. |
| `roles.workspace_id` | `opportunities.workspace_id` | Opportunity remains scoped to a workspace/search track. |
| `roles.company_id` | `opportunities.company_id` or employer reference | Keep linked company context; future normalization may enrich employer metadata. |
| `roles.source_id` | `opportunities.source_id` or provenance source reference | Existing `job_sources` can remain a source catalog. Richer provenance may need additional fields or table later. |
| `roles.title` | `opportunities.title` | Normalized display title. |
| `roles.job_url` | `opportunities.source_url` or canonical posting URL | Use for exact URL duplicate detection. Keep distinct from general external links. |
| `roles.location` | `opportunities.location` | Should map toward contract location fields. |
| `roles.remote_type` | `opportunities.remote_mode` | Current values should align with `RemoteTypeSchema` during migration. |
| `roles.compensation_min` | `opportunities.compensation.min` | Preserve numeric lower bound. |
| `roles.compensation_max` | `opportunities.compensation.max` | Preserve numeric upper bound. |
| `roles.compensation_currency` | `opportunities.compensation.currency` | Preserve as explicit currency code/string. |
| `roles.raw_description` | `opportunities.rawContent` | Raw user-pasted or imported source content. |
| `roles.normalized_description` | `opportunities.normalizedContent.description` | May later expand into responsibilities, requirements, benefits, and signals. |
| `roles.parse_metadata` | `opportunities.metadata`, parse warnings, parse confidence, intelligence metadata | Current home for parse output and opportunity intelligence. Decide later what becomes first-class columns. |
| `roles.status` | `opportunities.status` | Listing/opportunity status only. It is not application workflow state. |
| `roles.date_found` | `opportunities.importedAt` or `date_found` | Date the user found or saved the opportunity. |
| `roles.date_posted` | `opportunities.date_posted` or source posting date | Should remain optional and source-qualified. |
| `companies` | Employer/company context for Opportunity | Keep normalized company records. |
| `job_sources` | Source/provenance catalog for Opportunity | Keep source labels/types; expand only when Layer 8 needs it. |
| `compass_evaluations.role_id` | `compass_evaluations.opportunity_id` | Rename later only after API and tests are stable. Semantics remain link to target opportunity. |
| `applications.role_id` | `applications.opportunity_id` | Application workflow attaches to an Opportunity, but owns its own state/history. |
| `generated_artifacts.role_id` | `generated_artifacts.opportunity_id` | Artifacts target an Opportunity and may also link to application/submission records later. |

## 8. Status Model

Opportunity status, Application workflow state, and Artifact lifecycle status are separate state machines.

| Status family | Contract | Meaning | Current implementation |
| --- | --- | --- | --- |
| Opportunity status | `OpportunityStatusSchema` | State of the saved professional possibility or listing, such as discovered, interested, evaluating, evaluated, applied, withdrawn, or archived | `Role.status`, with the frontend currently using a narrower `RoleStatus` union |
| Application workflow state | `ApplicationWorkflowStateSchema` | State of the user's pursuit workflow, such as discovered, interested, applied, interviewing, offer, rejected, withdrawn, or archived | `Application.current_state` plus state history |
| Artifact lifecycle status | `ArtifactLifecycleStatusSchema` | State of a generated artifact: draft, reviewed, submitted, or archived | Artifact contracts define it; current backend generated artifacts now have additive lifecycle fields while workflow APIs remain in progress |

Opportunity status is not the same as Application state.

Examples:

- An Opportunity can be `evaluated` while no Application exists.
- An Opportunity can be `interested` while the Application workflow is still `discovered`.
- An Application can be `interviewing` while the target Opportunity remains a saved listing with separate source/provenance metadata.
- An Artifact can be `draft` even when Application state is `applied`.

Layer 7B should keep these concepts separate in API names, UI copy, tests, and analytics.

## 9. Migration Strategy

### Option 1: Compatibility-first

Keep `roles` as the physical table while using Opportunity as canonical language in documentation, contracts, UI copy, and possibly outward API aliases.

Benefits:

- Lowest risk to existing tests and local data.
- Avoids touching every `role_id` consumer at once.
- Lets `/roles` continue working while Opportunity language stabilizes.
- Good fit for frontend label updates and integration design.

Costs:

- Backend internals remain semantically stale.
- Future integrations may need to remember that Opportunity is backed by Role.
- The longer this lasts, the more alias debt accumulates.

### Option 2: Destructive rename

Rename `roles` to `opportunities`, rename the SQLAlchemy model, rename Pydantic schemas, rename API routes, rename frontend references, and rename foreign keys from `role_id` to `opportunity_id`.

Benefits:

- Cleanest long-term semantic model.
- Avoids a prolonged Role/Opportunity split.
- Pre-production status makes destructive migration permissible if planned carefully.

Costs:

- High blast radius across backend APIs, frontend routes, tests, analytics, COMPASS, applications, artifacts, and activity logs.
- Easy to mix behavior changes into a naming migration.
- Existing `/roles` clients and local workflows break unless compatibility aliases are added.

### Option 3: Hybrid

Introduce Opportunity-facing API/service/schema names first, preserve `/roles` aliases temporarily, update UI language and routes with redirects, then perform the destructive persistence rename after tests and behavior are stable.

Benefits:

- Makes Opportunity the product surface before Layer 8 integrations.
- Keeps existing local behavior working during the transition.
- Lets tests be updated around one semantic target while physical persistence remains stable.
- Creates a controlled point to decide whether a destructive table/model/FK rename is still worth doing.

Costs:

- Requires temporary aliases and migration notes.
- Requires discipline to avoid building new Layer 8 integration code against the legacy Role language.

### Recommendation

Layer 7B should use the hybrid approach.

Do not start Layer 7B with a physical table rename. The current system has many `role_id` consumers: COMPASS evaluations, application workflow, generated artifacts, artifact performance, analytics, source intelligence, historical learning, frontend routes, and tests. The first implementation slice should make Opportunity the outward product/API/UX concept while preserving `/roles` behavior as a compatibility alias.

After `/opportunities` aliases, UI naming, tests, and docs are stable, a later Layer 7C destructive migration can rename `roles` to `opportunities`, rename the SQLAlchemy model, and rename `role_id` foreign keys if the repo still benefits from that physical cleanup.

## 10. Recommended Layer 7B Implementation Scope

Layer 7B compatibility scope:

- Opportunity-facing backend route aliases for core intake/list/detail/update/archive behavior.
- Existing `/roles` routes preserved as temporary compatibility aliases.
- Opportunity-facing Pydantic schema names or exported aliases while keeping payload compatibility.
- Physical `roles` table unchanged.
- SQLAlchemy `Role` model unchanged.
- Existing `role_id` database columns unchanged.
- Frontend user-visible labels moved from Role to Opportunity in the primary intake/list/detail flow.
- `/opportunities`, `/opportunities/new`, and `/opportunities/:opportunityId` frontend routes added.
- Backward-compatible redirects or route aliases from `/roles` paths to the corresponding Opportunity paths.
- Tests asserting Opportunity-facing behavior while preserving coverage for `/roles` compatibility.
- Docs updated to make the temporary Role-backed implementation explicit.

Layer 7B does not:

- Rename physical database tables.
- Rename SQLAlchemy models.
- Rename foreign key columns.
- Remove `/roles` behavior.
- Implement Layer 8 integrations.
- Implement Layer 9 automation.

The destructive persistence rename should be a separate follow-up after the outward Opportunity surface is stable.

Layer 7B retained compatibility debt:

- The `roles` table, SQLAlchemy `Role` model, and `role_id` foreign keys remain current persistence.
- Runtime `Role.status` remains narrower than the canonical `OpportunityStatusSchema`; status expansion belongs in a separate approved change.
- COMPASS evaluation APIs still use `/api/roles/{role_id}/evaluations` during the compatibility phase.
- Internal frontend `Role*` component names remain until a later cleanup can avoid unnecessary churn.

## 11. Deduplication and Similarity Strategy

MVP deduplication should be deterministic and lightweight:

- Exact normalized URL match.
- Same company plus similar normalized title.
- Same source content hash.
- Same recruiter/source plus similar content.
- User-visible possible duplicate signal.

The system should surface likely duplicates without auto-merging. A duplicate signal is advisory intelligence, not a destructive action.

`OpportunityIntelligenceService` is a useful starting point because it already detects exact URL matches, same-company/title similarity, description similarity, and hidden/misleading signals on Role-backed records. Layer 7B can keep this service Role-backed while changing outward language to Opportunity. A later migration can rename the service internals when the physical model changes.

Do not introduce vector databases, embeddings, or AI-driven deduplication for this layer unless a later recon identifies a concrete need that deterministic matching cannot satisfy.

## 12. Source / Provenance / Recruiter Intelligence Strategy

Layer 7 should prepare Opportunity for future Layer 8 integrations while staying local-first and privacy-conscious.

Opportunity/provenance should support:

- Source type.
- Source URL.
- Source label/name.
- Imported timestamp.
- Content hash.
- Parser version.
- Parse warnings.
- Recruiter/contact source when known.
- Original external system reference when known.

Existing `job_sources`, `roles.source_id`, `roles.job_url`, `roles.date_found`, and `roles.parse_metadata` cover part of this. Future Layer 8 imports should not require public cloud sync, background polling, or external account linkage by default. Imported content should remain local unless the user explicitly configures an integration.

Recruiter/contact intelligence should begin as source metadata and user-visible notes. A dedicated Contact or Recruiter model should be added only when integration or workflow requirements make it necessary.

## 13. Analytics Integration Plan

Opportunity should support future analytics such as:

- Response rate by source.
- Compensation fit by role type.
- High-fit and low-compensation opportunities.
- Recruiter/source quality.
- Artifact variant performance.
- Search-track retrospectives.
- Duplicate and near-duplicate trends.
- Opportunity outcomes over time.

The current analytics services already aggregate over Role-backed records, Application state, COMPASS evaluations, generated artifacts, artifact performance, source intelligence, and historical learning. Layer 7B should preserve those behaviors while gradually renaming outward metrics from Role to Opportunity. Do not change analytics semantics as part of a naming-only transition.

## 14. UX Naming Transition Plan

The UI should move from "Role" to "Opportunity" in a controlled transition.

Recommendations:

- Use "Opportunities" for navigation and list page titles.
- Use "Add opportunity" for intake.
- Use "Opportunity title" instead of "Role title".
- Use "Opportunity intelligence" for the existing intelligence panel.
- Use `/opportunities` routes as the primary routes.
- Keep `/roles` redirects or route aliases during the transition.
- Rename frontend component/type names after route and copy behavior are covered by tests, not as a first step if it creates unnecessary churn.
- Avoid showing both "Role" and "Opportunity" in the same workflow except where temporary migration copy is helpful.
- Keep developer docs explicit that current Opportunity behavior is Role-backed until the persistence rename happens.

This transition should reduce user confusion by making the broad concept visible immediately while preserving existing local workflows.

## 15. Non-Goals

Layer 7A and the following Layer 7B naming/migration work do not implement:

- Integrations.
- Automation.
- Production auth.
- Marketplace features.
- Coach/advisor mode.
- Vector dedupe.
- External email/calendar sending.
- Artifact export implementation.

## 16. Open Questions

- Should the destructive persistence rename happen in Layer 7C, or should `roles` remain the physical table indefinitely with Opportunity as the canonical product language?
- When the persistence rename happens, should every `role_id` column become `opportunity_id` in one migration, or should compatibility views/aliases exist during a transition?
- Should source/provenance become a first-class table separate from `job_sources`, or should richer fields live on Opportunity metadata until Layer 8?
- What is the minimum Contact/Recruiter model needed before Gmail, Outlook, LinkedIn, or job-board integrations?
- Should ActivityLog `entity_type` values migrate from `role` to `opportunity`, and how should historical activity be displayed?
- Should existing `Role.status` values map exactly to `OpportunityStatusSchema`, or should the frontend/backend status set be expanded during Layer 7B?
- Should ExternalLink attach to Opportunity as well as Application, or should Opportunity source URL remain the only canonical opportunity-level link for now?
- How long should `/roles` API compatibility remain after `/opportunities` exists in a pre-production local-first app?

