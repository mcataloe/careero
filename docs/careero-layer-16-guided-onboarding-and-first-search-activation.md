# Layer 16 — Guided Onboarding & First Search Activation

## Status

Future / appended onboarding and support layer.

Layer 16 defines the guided first-use experience for Careero. It should help a new user understand the basic workflow, create or select a workspace/search track, add their first opportunity, understand where COMPASS fits, and know how to request support or report product feedback.

This layer is intentionally documented as Layer 16 to preserve the current append-only LEAP layer map. Product-wise, much of this experience should appear early in the user's first session after the account/workspace foundation exists.

## Purpose

Create a calm, action-oriented onboarding layer that helps users reach first value quickly.

The strategic goal:

> A new Careero user should be able to understand the platform, start a search track, add a first opportunity, understand the role of COMPASS, and know where to get help without being forced through a heavy setup process.

Layer 16 is not merely a product tour. It is first-search activation.

The user should leave the flow knowing:

- What Careero is for.
- What a workspace/search track is.
- How to start or continue a job search.
- How to add an opportunity.
- How COMPASS helps evaluate fit and improve application materials.
- That COMPASS source-of-truth setup is recommended, but not required to begin.
- How to report bugs, ask for support, or suggest product improvements.

## Why This Is a Separate Layer

Onboarding is cross-cutting. It touches account state, workspace state, opportunity intake, COMPASS explanation, empty states, support flows, analytics, help content, and user trust.

It should not be buried as incidental copy inside a single page.

Layer 16 asks:

- What is the shortest path to first useful action?
- How does Careero explain workspaces/search tracks without overwhelming the user?
- How does the product encourage COMPASS source-of-truth setup without making it an activation wall?
- How can the user skip, resume, or replay guidance?
- How are bugs, suggestions, help requests, UX confusion, and AI-output issues reported?
- What support context should be captured safely?

## First Useful Action

The first useful action should be:

> Create or choose a workspace/search track, then add one opportunity.

The onboarding layer should not require the user to complete a full profile, build a complete COMPASS source of truth, generate artifacts, configure integrations, or read long documentation before they can use Careero.

The product should communicate this plainly:

> You can start now with a job description. You will get better results later if you add source materials and build out your COMPASS source of truth.

## COMPASS Positioning

COMPASS source-of-truth setup should be encouraged, not required.

Recommended framing:

| User state | Recommended path |
| --- | --- |
| I just want to try Careero | Start with a pasted job description. |
| I want better role-fit analysis | Add resume/profile source material. |
| I want higher-trust tailoring and reusable outputs | Build a COMPASS source of truth. |
| I am running a serious multi-role search | Use search tracks plus COMPASS grounding. |

COMPASS is the quality upgrade, not the entry fee.

Layer 16 must avoid creating a setup tax. The user should be able to begin with lightweight opportunity intake and progressively deepen the source-of-truth model when the value is clear.

## Guided Flow

Keep the first-run flow short and action-oriented.

Recommended first-run sequence:

1. **Welcome** — Explain Careero in one sentence and set the expectation that the user can begin lightly.
2. **Workspace/Search Track** — Explain the search-track concept and help the user create or select one.
3. **Opportunity Intake** — Show how to paste a job description or manually add an opportunity.
4. **COMPASS Preview** — Explain that COMPASS evaluates role fit and application strategy using available source material.
5. **Source Materials** — Encourage resume/profile source material and COMPASS source-of-truth setup without requiring it.
6. **Support & Feedback** — Show where to report bugs, ask for help, or suggest improvements.
7. **Finish** — Land the user in the workspace dashboard or first opportunity workflow.

The flow should teach by doing. Avoid a passive slideshow.

## Skippable, Resumable, Replayable

The guided flow must be skippable.

Required controls:

- Start guided setup.
- Skip for now.
- Resume setup later.
- Replay tour/help from the app shell or help menu.

Skipping should not permanently discard guidance. Many users will skip first and return later when they are confused.

## Onboarding Surfaces

Layer 16 should use three complementary surfaces.

### 1. First-run guided flow

Appears after account creation or first login when onboarding is incomplete.

Goal: help the user start a real search.

### 2. Contextual empty states

Examples:

- No workspaces yet: prompt the user to create a search track.
- No opportunities yet: prompt the user to paste a job description or create a manual opportunity.
- No source material yet: explain that COMPASS can work lightly now and improve when sources are added.
- No artifacts yet: explain that resume/cover-letter drafts come after opportunity evaluation and source grounding.

Goal: guide without modal fatigue.

### 3. Help and feedback drawer

Persistent access from the app shell.

Goal: let users recover when confused and submit actionable feedback.

## Support and Feedback Scope

Layer 16 should include basic user-support and feedback paths without overbuilding a full support desk.

Minimum support flows:

- Report a bug.
- Suggest an improvement.
- Ask for help.
- Report UX confusion.
- Report an AI output issue.
- Report a data/privacy concern.

Recommended feedback categories:

- Bug.
- UX confusion.
- Feature suggestion.
- AI output issue.
- Data/privacy concern.
- Account/access issue.
- Other.

Recommended severity levels:

- Low.
- Medium.
- High.
- Blocking.

Feedback should capture enough context to be useful while avoiding unnecessary sensitive data.

Candidate context:

- Current page path.
- User ID.
- Workspace ID, if available.
- Opportunity ID, if available.
- Browser/user-agent summary, if available.
- Timestamp.
- User-provided title and description.
- Optional screenshot or attachment support later only after explicit user action.

Do not silently capture raw resumes, raw job descriptions, private notes, compensation strategy, generated artifacts, or COMPASS rationale in support payloads.

## Candidate Data Model

Candidate onboarding state:

```ts
UserOnboardingState {
  id: string
  userId: string
  hasSeenWelcome: boolean
  hasCreatedFirstWorkspace: boolean
  hasAddedFirstOpportunity: boolean
  hasViewedCompassIntro: boolean
  hasSeenSourceMaterialPrompt: boolean
  hasSeenSupportIntro: boolean
  hasCompletedFirstRun: boolean
  skippedAtStep?: string | null
  completedAt?: string | null
  createdAt: string
  updatedAt: string
}
```

Candidate feedback record:

```ts
UserFeedback {
  id: string
  userId: string
  workspaceId?: string | null
  opportunityId?: string | null
  type: "bug" | "suggestion" | "help" | "ai_output_issue" | "ux_confusion" | "privacy_concern" | "account_access" | "other"
  severity?: "low" | "medium" | "high" | "blocking"
  pagePath?: string | null
  title: string
  description: string
  status: "new" | "reviewed" | "planned" | "resolved" | "closed"
  createdAt: string
  updatedAt: string
}
```

These names are candidates, not final schema commitments. LEAP Recon should validate naming against existing user/account/workspace conventions.

## Relationship to Existing Layers

### Layer 0 — Product Foundation

Layer 16 operationalizes Layer 0's calm, humane, user-first UX philosophy. The user should leave onboarding clearer, calmer, and more in control.

### Layer 1 — Local Platform Foundation

Layer 16 depends on account/session state and user ownership boundaries so onboarding progress can persist per user.

### Layer 2 — Intake, Parsing & Grounding

Layer 16 introduces the user to opportunity intake and explains why source materials improve COMPASS quality.

### Layer 3 — COMPASS + Artifact Foundation

Layer 16 explains COMPASS as advisory, grounded, and optional at first. It should not hide the difference between lightweight analysis and source-grounded analysis.

### Layer 4 — Application Workflow

Layer 16 should land users in the workspace or application workflow after first setup, not trap them in onboarding screens.

### Layer 5 — Workflow Intelligence / Insights

Layer 16 may eventually use lightweight activation analytics, but should not become a pressure machine or gamified productivity system.

### Layer 11 — Productization / Deployment / Monetization

Layer 16 support and feedback data will matter for product readiness, but it should remain local-first until hosted support, retention, privacy, and production account boundaries are defined.

### Layer 14 — Model Catalog, Prompt Architecture & Credit Controls

Layer 16 should not require model choice or paid credits to complete onboarding.

### Layer 15 — API Job Sources, Import Pipelines & Managed Deltas

Layer 16 should not depend on external job-source import. Manual/paste-in opportunity intake remains the first activation path.

## Required Boundaries

Layer 16 must not:

- Require COMPASS source-of-truth setup before a user can start.
- Require artifact generation before the user understands the opportunity workflow.
- Require integrations, API job sources, browser extensions, or external accounts.
- Depend on AI availability for the tour to function.
- Auto-submit applications.
- Auto-send external communications.
- Capture sensitive support context silently.
- Turn onboarding into a long documentation sequence.
- Add shame-based productivity nudges or application-volume gamification.
- Become a full support-ticketing platform in the MVP.

## Pressure-Test Summary

### Keep

- Treat the layer as first-search activation, not a generic tour.
- Keep the first useful action focused on workspace/search-track creation plus one opportunity.
- Make COMPASS recommended but optional.
- Make the tour skippable, resumable, and replayable.
- Use contextual empty states in addition to any guided flow.
- Add basic support, bug-report, and suggestion flows.
- Keep support categories separate so bug reports, UX confusion, AI issues, and feature requests do not become one junk drawer.
- Keep AI optional for the tour itself.

### Avoid

- Forcing a full COMPASS Layer 0/source-of-truth build before first value.
- Explaining every platform concept before the user can act.
- Overbuilding a live support desk.
- Capturing private application data in support reports by default.
- Adding sample/demo-mode requirements in this layer.

## Recommended Implementation Order

1. Layer 16 Recon and final UX-flow boundary confirmation.
2. Onboarding state contract and persistence.
3. First-run route/entry decision.
4. Guided setup shell.
5. Workspace/search-track creation or selection step.
6. First opportunity intake step.
7. COMPASS and source-material explanation step.
8. Help/support/feedback drawer entry point.
9. Feedback persistence and basic admin/dev review surface.
10. Contextual empty states across workspace, opportunity, source, and artifact surfaces.
11. Tour replay/resume behavior.
12. Tests for onboarding state, feedback submission, skip/resume/replay behavior, and privacy-safe support payloads.
13. README and strategic-plan reconciliation after implementation.

## Exit Criteria

Layer 16 is implementation-ready when:

- The first-run user path is defined.
- The first useful action is clear.
- Onboarding can be skipped, resumed, and replayed.
- COMPASS is encouraged but not required.
- Support/feedback categories and statuses are defined.
- Candidate onboarding and feedback records are defined.
- Sensitive support-data boundaries are explicit.
- Empty-state guidance strategy is defined.
- Non-goals are explicit.

Layer 16 is implemented when:

- A new user can reach a first workspace/search track and first opportunity without reading documentation.
- The user understands what COMPASS does and why source materials improve output quality.
- The user can submit a bug report, help request, suggestion, UX confusion report, AI-output issue, or privacy concern.
- Onboarding progress persists per user.
- The flow can be skipped, resumed, and replayed.
- No support payload silently includes private application materials or source content.
