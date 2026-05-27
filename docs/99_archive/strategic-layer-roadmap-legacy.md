# Archived: Careero Strategic Layer Roadmap

Status: Historical  
Doc Type: Archive  
Layer: N/A  
Source of Truth: No  
Last Reviewed: 2026-05-27  
Related Docs:
- docs/99_archive/00_archive-index.md
- docs/01_strategy/00_product-strategy.md
> Archived on 2026-05-20.
>
> This document is retained for historical context only. Do not use it as the source of truth for Careero layer planning, LEAP Recon, or Codex implementation prompts.
>
> Current canonical planning document: `docs/01_strategy/00_product-strategy.md`.
>
> Reason archived: this roadmap used an older Layer 0-12 sequence where Layer 8 was Automation Guardrails. The current application plan revised the sequence so Layer 8 is Integrations and Automation Guardrails is Layer 9.

---

# Careero Strategic Layer Roadmap

## Purpose

This document tracks Careero's Layer 0-12 strategic roadmap.

The roadmap is product-strategy focused. It explains what each layer is meant to accomplish, how the layers sequence, which areas are already built or substantially defined, and which areas remain future-facing. It is not an implementation prompt, sprint plan, or replacement for detailed feature specifications.

Careero's layer model should help the project preserve a coherent product direction while allowing implementation to happen in smaller, reviewable slices.

## Current Layer Status

| Layer | Name | Current status | Purpose | Summary of included capabilities |
| --- | --- | --- | --- | --- |
| Layer 0 | Product Foundation | Built / defined | Establish the product's strategic operating model. | Mission, target users, MVP boundary, product principles, workspace/search-track concept, AI governance posture, UX philosophy, monetization philosophy, and risk boundaries. |
| Layer 1 | Core Platform | Built / mostly built | Provide the technical foundation for a real application. | User accounts, authentication/login, sessions, authorization, user profile, workspace ownership, environment/config setup, and core database structure. |
| Layer 2 | Intake & Parsing | Built / mostly built | Turn raw opportunity and source-material input into structured data. | Pasted job description intake, AI-assisted role parsing, manual field correction, resume/profile source storage, supported local document imports, normalized long-text handling, and source-grounded COMPASS preparation. |
| Layer 3 | Core Domain Model | Built / mostly built | Define Careero's canonical product objects and lifecycle concepts. | Workspace, Opportunity, COMPASS Evaluation, Resume Artifact, Cover Letter Artifact, Application State, canonical contracts, versioning strategy, lifecycle guidance, and migration mapping from earlier role-centered models. |
| Layer 4 | Application Workflow | Built / mostly built | Manage the day-to-day job-search workflow. | Saved opportunities, application state machine, application history/timeline, notes, reminders, interview tracking, status pipeline, archive/reactivate workflows, and basic dashboard views per workspace/search track. |
| Layer 5 | Workflow Intelligence / Insights | Next / partially started | Help users understand what is working, what is stuck, and where to focus next. | Workspace/search-track dashboards, pipeline analytics, stale opportunity detection, follow-up candidates, upcoming reminders/interviews, COMPASS recommendation rollups, opportunity comparison, search-track health indicators, activity trends, and "what should I focus on next?" views. |
| Layer 6 | Advanced COMPASS + Artifact Lifecycle | Planned | Make evaluation and application materials more trustworthy, traceable, and strategically useful. | COMPASS history, cross-opportunity comparison, JD-to-resume evidence mapping, missing requirement detection, TruthGuard checks, resume and cover-letter artifact versioning, submitted artifact tracking, tailoring notes, internal-strategy separation, and source-material traceability. |
| Layer 7 | Integrations | Planned | Reduce manual entry by connecting Careero to tools users already use. | Google Docs import, Gmail/Outlook linkage, calendar interview sync, LinkedIn/job-board save helpers, browser extension or share-sheet intake, resume source sync, DOCX/PDF/Markdown export, and optional cloud storage integrations. |
| Layer 8 | Automation Guardrails | Planned | Automate repetitive actions safely without reducing user control or trust. | Suggested follow-ups, draft-only application material generation, reminder automation, status nudges, review-before-send workflows, no auto-apply without explicit approval, TruthGuard checks before artifact generation, approval logs, and automation boundaries per workspace/search track. |
| Layer 9 | Advanced Search Tracks / Career Strategy | Planned | Make Careero more strategic than tactical. | Multiple long-running career paths, full-time vs. contract strategy comparison, compensation target modeling, skill-gap planning, role-market positioning, career narrative refinement, search-track archival retrospectives, and strategic category adjustments. |
| Layer 10 | Monetization / Productization | Future | Turn Careero into a sustainable product without compromising user trust. | Free tier, paid AI/artifact usage, power-user tier, optional coach/recruiter-adjacent tools, privacy-first billing/account model, and clear separation from employer-sponsored influence. |
| Layer 11 | Team / Coach / Advisor Mode | Future | Allow trusted external help while preserving privacy boundaries. | Career coach access, resume reviewer access, spouse/advisor review mode, comment-only permissions, shared opportunity packets, and privacy-scoped collaboration. |
| Layer 12 | Marketplace / Employer-Side Exploration | Future / last | Explore employer-side or marketplace capabilities only after user-side value is strong. | Recruiter-facing opportunity intake, ethical matching, user-controlled visibility, no pay-to-rank distortion, optional employer partnerships, and strict disclosure rules. |

## Layer Details

### Layer 0 â€” Product Foundation

Layer 0 defines why Careero exists and what boundaries should guide product, UX, AI, monetization, and engineering decisions.

Its purpose is to keep the product job-seeker-first. Careero should reduce the chaos, opacity, and emotional exhaustion of modern job searching by giving individuals a structured, intelligent, and humane system for managing opportunities, evaluating fit, preparing materials, and tracking progress across multiple parallel job-search paths.

Layer 0 is not primarily feature work. It is the strategic foundation that later layers should answer to.

### Layer 1 â€” Core Platform

Layer 1 provides the base application foundation.

It covers identity, access, ownership, configuration, sessions, profiles, and database structure. The goal is to make Careero a durable application instead of a loose local prototype.

### Layer 2 â€” Intake & Parsing

Layer 2 focuses on getting role and source-material data into the system.

It includes pasted job description intake, AI-assisted parsing, manual correction, resume/profile source storage, supported local document imports, and the review-before-save pattern. The layer should keep AI assistive, editable, and grounded in user-reviewed source material.

### Layer 3 â€” Core Domain Model

Layer 3 defines the canonical objects Careero uses to reason about the job-search workflow.

The central objects include Workspace, Opportunity, COMPASS Evaluation, Resume Artifact, Cover Letter Artifact, and Application State. These contracts should provide a stable bridge between frontend rendering, backend persistence, AI orchestration, workflow tracking, and future export generation.

### Layer 4 â€” Application Workflow

Layer 4 manages the actual job-search workflow.

It includes saved opportunities, state transitions, notes, reminders, interviews, application history, status pipelines, archive/reactivate flows, and dashboard basics. The purpose is to help users manage active searches without collapsing everything into a spreadsheet or one flat opportunity list.

### Layer 5 â€” Workflow Intelligence / Insights

Layer 5 turns accumulated workflow activity into useful guidance.

Once Careero can save opportunities and track state, the natural user question becomes: what should I focus on next? This layer should answer that through dashboards, stale-opportunity detection, follow-up recommendations, COMPASS rollups, pipeline health, activity trends, and search-track-level insight.

### Layer 6 â€” Advanced COMPASS + Artifact Lifecycle

Layer 6 deepens evaluation quality and artifact traceability.

It should make COMPASS evaluations more comparable over time, connect role requirements to resume evidence, detect missing high-priority terms, apply TruthGuard checks before artifact generation, and track resume and cover-letter artifacts through draft, reviewed, submitted, and archived states.

This layer should preserve a strict separation between internal strategy and employer-facing materials.

### Layer 7 â€” Integrations

Layer 7 reduces manual entry by connecting Careero to tools job seekers already use.

Candidate integrations include Google Docs, Gmail/Outlook, calendar interview sync, LinkedIn/job-board save helpers, browser extension or share-sheet intake, resume source sync, DOCX/PDF/Markdown export, and optional cloud storage integrations.

Integrations should come after the internal workflow is stable enough to know what data should be imported, exported, or synchronized.

### Layer 8 â€” Automation Guardrails

Layer 8 adds automation while preserving user review and control.

The goal is to help with repetitive work without turning Careero into an unsupervised application machine. Suggested follow-ups, reminder automation, draft-only material generation, review-before-send workflows, TruthGuard checks, and approval logs belong here.

No auto-apply behavior should exist without explicit user approval and a clear review boundary.

### Layer 9 â€” Advanced Search Tracks / Career Strategy

Layer 9 makes Careero more strategic than tactical.

This layer supports long-running career paths, full-time vs. contract strategy comparison, compensation modeling, skill-gap planning, role-market positioning, career narrative refinement, and search-track retrospectives.

It should help users understand not only what they are applying to, but whether their overall search strategy is working.

### Layer 10 â€” Monetization / Productization

Layer 10 addresses sustainability without compromising trust.

Potential capabilities include a free tier, paid AI/artifact usage, power-user tiers, privacy-first billing, optional coach/recruiter-adjacent tools, and clear separation from employer-sponsored influence.

The product should avoid monetization patterns that make users feel steered, ranked, or exploited during a stressful career transition.

### Layer 11 â€” Team / Coach / Advisor Mode

Layer 11 allows trusted external help.

This may include career coach access, resume reviewer access, spouse/advisor review mode, comment-only permissions, shared opportunity packets, and privacy-scoped collaboration.

The layer should be permission-first. External reviewers should see only what the user intentionally shares.

### Layer 12 â€” Marketplace / Employer-Side Exploration

Layer 12 should be explored only after the user-side product is strong.

Possible capabilities include recruiter-facing opportunity intake, ethical matching, user-controlled visibility, optional employer partnerships, and strict disclosure rules.

This layer should not introduce pay-to-rank distortion or employer-sponsored influence that undermines the job-seeker-first foundation.

## Recommended Build Sequence

The recommended maturity curve is:

```text
structure -> workflow -> insight -> better decisions -> less manual entry -> safe automation -> strategy -> collaboration -> productization/ecosystem
```

The practical sequence is:

1. Stabilize Layers 0-4 as the product and workflow foundation.
2. Build Layer 5 so the workflow becomes informative, not merely record-keeping.
3. Build Layer 6 so COMPASS and artifacts become more traceable, auditable, and useful.
4. Build Layer 7 integrations after internal data flows are stable.
5. Build Layer 8 automation only after review, approval, and TruthGuard boundaries are clear.
6. Build Layer 9 career strategy once enough workflow history exists to generate useful retrospectives.
7. Explore Layers 10-12 only after the user-side workflow has proven durable value.

## Maintenance Notes

- Keep this roadmap product-strategy focused. Do not turn it into a detailed implementation prompt archive.
- Update layer status when a layer moves from planned to in progress, mostly built, or complete.
- Keep README.md concise and link here instead of duplicating the full roadmap there.
- Use separate implementation documents or prompt files for detailed LHS/Codex build slices.
- When implementation reality diverges from this roadmap, update this document rather than relying on chat history as the source of truth.
- Preserve the user-first, AI-grounded, review-before-action posture across all future layers.


