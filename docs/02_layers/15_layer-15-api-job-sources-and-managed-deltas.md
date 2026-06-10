# Layer 15 â€” API Job Sources, Import Pipelines & Managed Deltas

Status: Draft  
Doc Type: Layer Spec  
Layer: Layer 15  
Source of Truth: Yes  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/03_domain-design/opportunity-model.md
- docs/05_security-privacy-governance/canonical-domain-model.md

## Status

Future / appended API intelligence layer.

Layer 15 is split out from the older combined Layer 14 planning concept. It owns official-API-first job-source ingestion, imported job records, source snapshots, managed deltas, provider adapters, provenance, and review-before-save flows.

Layer 14 remains focused on model catalog, Careero Prompt Architecture, model choice, usage accounting, and credit controls.

Layer 15 should wait until Opportunity semantics, integration boundaries, source governance, and review-before-save patterns are stable enough to receive external job data safely.

## Purpose

Create a structured API-first job-source layer that can import, normalize, refresh, compare, and review job postings from permitted official APIs and licensed providers.

The strategic goal:

> Careero can ingest external job postings from permitted APIs, preserve immutable source snapshots, compute managed deltas over time, and surface user-reviewable changes without scraping or overwriting user-owned opportunity records.

Layer 15 should reduce manual entry without weakening Careero's core trust model.

## Hard Boundary

Layer 15 is API-only or licensed-source-only.

Do not implement:

- Scraping.
- Restricted-source extraction.
- Browser-driven collection.
- LinkedIn scraping.
- Indeed scraping.
- Glassdoor scraping.
- Terms-sensitive data collection.
- Anti-bot evasion.
- Silent background import from sources without a permitted API or licensed path.

Scraping can be revisited later only through explicit legal, product, privacy, retention, source-terms, operational, and technical review.

## Why This Is a Separate Layer

Model choice and API job-source ingestion are different architectural problems.

Layer 14 asks:

- Which AI model should perform this task?
- How should Careero compile prompts?
- How should generated output be checked?
- How should model usage be metered and credited?

Layer 15 asks:

- Which official job-source APIs can Careero use?
- How are external postings normalized?
- How are source snapshots preserved?
- How are posting deltas computed?
- How do imported postings become reviewable Opportunity candidates?
- How do user edits coexist with refreshed source truth?

Trying to solve both in one layer muddies the build plan. Layer 15 keeps external job-source ingestion in its own architecture lane.

## Starting Source Candidates

Priority ATS/job-source providers to validate:

- Greenhouse Job Board API.
- Ashby public job posting API.
- Lever Postings API / job feed.
- Recruitee careers site API.
- SmartRecruiters posting API.
- Workable API where authorized.
- BambooHR ATS API where authorized.
- iCIMS Job Portal API where authorized.
- Workday only through an official, partner, or licensed data path.

Potential licensed or broad job-data providers:

- Adzuna.
- Coresignal.
- Lightcast.
- TheirStack.
- Other licensed job-data providers if pricing, storage rights, freshness, and source terms fit Careero.

Priority should be based on:

- API availability.
- Terms clarity.
- Source freshness.
- Cost.
- Storage rights.
- Rate limits.
- Field completeness.
- User value.
- Implementation simplicity.
- Compatibility with Careero's Opportunity model.

## Candidate Data Model

Layer 15 should preserve imported source truth separately from user-edited Opportunity records.

Candidate records:

- `job_source_provider`
- `job_source_connection`
- `job_source_account`
- `job_posting`
- `job_posting_source_record`
- `job_posting_snapshot`
- `job_posting_ingestion_run`
- `job_posting_delta`
- `job_posting_delta_field`
- `job_posting_import_candidate`
- `job_posting_match_candidate`
- `opportunity_source_link`
- `managed_delta_review`

These names are candidates, not final schema commitments. LEAP Recon should validate naming against the current Opportunity-backed persistence model and remaining Role compatibility aliases.

## Normalized Job Posting Fields

Recommended normalized fields:

- Source provider.
- Source type.
- Source job ID.
- Source organization/account identifier.
- Company ID/name/domain.
- Title.
- Department/team.
- Location raw.
- Location normalized.
- Remote type.
- Employment type.
- Salary minimum.
- Salary maximum.
- Salary currency.
- Salary period.
- Description HTML.
- Description text.
- Responsibilities.
- Requirements.
- Skills extracted.
- Apply URL.
- Posting URL.
- Date posted.
- Source updated timestamp.
- First seen timestamp.
- Last seen timestamp.
- Posting status.
- Content hash.
- Source snapshot hash.
- Provenance metadata.
- Raw source reference.
- Import/review state.

Field extraction should remain reviewable. Source fields should not automatically become user-owned Opportunity fields without a review step.

## Source Snapshots

Every imported posting should preserve immutable source snapshots.

A snapshot should answer:

- What did the source provide?
- When did Careero see it?
- Which provider/endpoint returned it?
- Which normalized fields were extracted?
- What changed from the previous snapshot?
- Which user-owned Opportunity fields, if any, were updated after review?

Snapshots should be append-only. Do not mutate old snapshots to reflect new source state.

## Managed Deltas

Managed deltas are the core differentiator of Layer 15.

A managed delta compares source snapshots and classifies changes in a way users can understand.

Candidate delta categories:

- New posting.
- Closed or removed posting.
- Reopened posting.
- Title change.
- Seniority change.
- Compensation change.
- Location change.
- Remote/hybrid/on-site policy change.
- Employment type change.
- Requirements change.
- Responsibility change.
- Skills/tooling change.
- Apply URL change.
- Deadline or timing change.
- Description-only low-signal change.
- Source metadata change.

Delta severity should be calibrated:

- High: compensation, remote policy, title/seniority, status closed/reopened, apply URL.
- Medium: requirements, responsibilities, location detail, employment type.
- Low: copy edits, formatting changes, minor metadata changes.

Deltas should be visible before they affect user-owned records.

## Review-Before-Save Flow

Imported jobs should enter Careero as reviewable candidates, not as automatic Opportunities.

Recommended flow:

1. Source adapter fetches postings.
2. Ingestion run stores raw source records and normalized snapshots.
3. Careero deduplicates against existing Opportunities and prior imported postings.
4. Import candidates are presented to the user.
5. User reviews normalized fields and source provenance.
6. User saves as a new Opportunity, links to an existing Opportunity, ignores, or archives the candidate.
7. Later source refreshes produce managed deltas.
8. User reviews meaningful deltas before updating user-owned Opportunity fields.

Do not auto-save imported jobs unless the user explicitly enables a safe, constrained workflow.

## User-Edited Data vs Source Data

Layer 15 must preserve the difference between source truth and user-owned records.

Source data:

- Comes from an official API or licensed source.
- Is stored as source records and snapshots.
- Can change when refreshed.
- Should retain provenance.
- Should not be edited directly by the user.

User-owned Opportunity data:

- Can be corrected, annotated, prioritized, archived, or overridden by the user.
- May differ from the source.
- Should not be overwritten silently.
- Should preserve user edits even when source snapshots change.

If a source refresh conflicts with a user edit, Careero should show the difference and let the user choose.

## Source Adapter Architecture

Each provider adapter should implement a common contract.

Candidate adapter responsibilities:

- Provider identification.
- Credential requirements, if any.
- Supported endpoints.
- Fetch posting list.
- Fetch posting detail.
- Normalize provider payload.
- Detect source update timestamps.
- Produce content hash.
- Preserve raw source payload according to retention/source terms.
- Respect rate limits.
- Handle retry/backoff.
- Report ingestion errors.
- Report terms/storage constraints.
- Provide provider-specific field confidence.

Adapters should not write directly to Opportunity records. They should produce source records, snapshots, and import candidates.

## Ingestion Runs

Each ingestion run should track:

- Provider.
- Source/account.
- Trigger type.
- Started/finished timestamps.
- Status.
- Requested scope.
- Number fetched.
- Number created.
- Number updated.
- Number unchanged.
- Number failed.
- Rate-limit events.
- Error summary.
- Source freshness.
- Cost/usage metadata where applicable.

Trigger types:

- Manual import.
- User-tracked company refresh.
- Saved opportunity refresh.
- Scheduled refresh, future only.
- Admin/provider validation run.
- Backfill, future only.

## Refresh Guidance

Refresh cadence should vary by user intent and source value.

Candidate approach:

- Saved active job: refresh more frequently while active.
- User-tracked company: regular refresh.
- Generic company page: daily-ish or less frequent.
- Expired/closed job: stop after a reasonable closeout window.
- Aggregator search result: less frequent and clearly labeled.
- User-ignored import candidate: no refresh unless resurfaced by a later search.

Exact TTLs should be validated during Layer 15 Recon.

## Relationship to Opportunity Model

Layer 15 depends on Layer 7 Opportunity semantics.

Layer 15 should not remove Role compatibility aliases. It should target the Opportunity-backed persistence model and preserve compatibility surfaces until a separate cleanup is approved.

Layer 15 should define:

- How imported job postings map to Opportunity candidates.
- How imported postings link to existing Opportunities.
- How duplicates are detected.
- How source refreshes affect saved Opportunities.
- How application records remain separate from job-source records.

## Relationship to Layer 8 Integrations

Layer 15 is an integration-like capability, but it deserves its own layer because official job-source ingestion, snapshots, deltas, provider governance, and provenance are deeper than local import/export.

Layer 8 remains the broader integration layer. Layer 15 owns the official job-source API spine.

## Relationship to Layer 14

Layer 15 may use Layer 14 services after they exist:

- AI-assisted field extraction.
- Requirement summarization.
- Job-fit preparation.
- Company or job-source summary generation.
- Usage metering and credit reporting for provider/API costs.

But Layer 15 must not depend on model routing for basic source ingestion. The first version should be able to ingest, normalize, snapshot, diff, and review postings deterministically.

## Source Governance

Every source should have a validation record before implementation.

Recommended source validation fields:

- Provider name.
- API documentation URL.
- Authentication requirement.
- Allowed use.
- Storage permission.
- Summary permission.
- Raw payload retention permission.
- Rate limits.
- Pricing.
- Attribution requirement.
- Refresh constraints.
- User-facing disclosure requirement.
- Known restrictions.
- Risk level.
- Approval status.

Do not treat a provider as approved merely because an endpoint exists.

## Required Boundaries

Layer 15 must not:

- Scrape job boards.
- Use restricted LinkedIn/Indeed/Glassdoor extraction.
- Auto-save imported jobs without user review unless explicitly enabled by a safe workflow.
- Treat aggregator data as more authoritative than ATS/source postings.
- Overwrite user-edited Opportunity data without preserving snapshots and user review.
- Hide source freshness.
- Hide provider/source provenance.
- Store raw licensed data unless the license permits storage.
- Use API import to create employer/recruiter visibility or marketplace ranking.

## Recommended LEAP Recon Questions

- Which official job-source APIs should be validated first?
- Which provider has the best first MVP shape: Greenhouse, Ashby, Lever, or another source?
- What fields can each provider reliably supply?
- What source data can be stored, summarized, or only referenced?
- What is the canonical normalized job posting record?
- How should source snapshots be stored?
- How should field-level deltas be computed?
- Which deltas are user-notable?
- How should import candidates map to existing Opportunities?
- How should deduplication work?
- How should user-edited Opportunity fields coexist with source refreshes?
- What refresh cadence should each source category use?
- What provider costs or rate limits affect product design?
- What should remain out of scope until legal/source-terms review?
- What belongs in a future scraping review backlog?

## Recommended Implementation Order

1. Layer 15 Recon and provider/source validation matrix.
2. Source governance record format.
3. Job-source provider adapter interface.
4. Normalized job posting contract.
5. Source record and snapshot model.
6. Import candidate model.
7. First read-only provider spike, likely Greenhouse or Ashby after validation.
8. Deduplication and match-candidate logic.
9. Review-before-save UX.
10. Managed delta model.
11. Field-level delta computation.
12. Saved Opportunity refresh and delta review flow.
13. Rate-limit/error/cost reporting.
14. Future provider expansion.

## Exit Criteria

Layer 15 is implementation-ready when:

- First provider candidates are validated.
- Source terms/storage permissions are documented.
- The provider adapter interface is defined.
- Normalized job posting fields are defined.
- Source snapshot strategy is defined.
- Managed delta categories are defined.
- Review-before-save flow is defined.
- Opportunity mapping strategy is defined.
- Non-goals are explicit.
- Scraping is clearly out of scope.

