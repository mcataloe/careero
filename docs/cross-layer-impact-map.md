# Cross-Layer Impact Map

## Layer 10 - Advanced Search Tracks / Career Strategy

Layer 10 depends on existing stored evidence and must remain derived, read-only,
and workspace-scoped until a later user-reviewed persistence build is approved.

Explicit dependencies:

- Layer 4 application workflow.
- Layer 5 analytics/intelligence.
- Layer 6 artifact lifecycle.
- Layer 7 Opportunity compatibility.
- Layer 8 local integration/export boundaries.
- Layer 9 automation guardrails.

Layer 10 impact rules:

- Reuse Layer 5 instead of duplicating analytics.
- Do not require Layer 7C destructive rename.
- Do not export internal strategy into employer-facing artifacts.
- Strategy actions must route through Layer 9 only if reviewable and approval-logged.
- Artifact performance signals are weak/correlational until artifact lifecycle is complete.
- Follow-up/reminder strategy must not overstate confidence while reminder UX/API is incomplete or partially reconciled.

| Layer | Impact on Layer 10 | Risk | Guardrail | Current status |
| --- | --- | --- | --- | --- |
| Layer 4 | Provides application states, outcomes, reminders, notes, links, and interviews. | Partial reminders can weaken follow-up confidence. | Expose sample size and uncertainty. | Substantially built; reminders still partial. |
| Layer 5 | Provides analytics, health, source, compensation, recommendations, and history. | Duplicated or conflicting insight logic. | Compose existing services first. | Partially built and reused. |
| Layer 6 | Provides artifact and artifact performance context. | Correlation overstated as causation. | Label artifact signals as correlational. | Artifact generation exists; lifecycle incomplete. |
| Layer 7 | Provides Opportunity-facing compatibility while persistence remains Role-backed. | Destructive rename scope creep. | Keep Role-backed persistence unchanged. | Compatibility surface started. |
| Layer 8 | Provides local export boundaries and future integration context. | Internal strategy leaking to exports. | Do not export strategy into artifacts. | Backend export exists; frontend workflow future. |
| Layer 9 | Provides suggestion and approval guardrails. | Advisory actions become hidden automation. | No `AutomationSuggestion` creation without explicit user action. | Local guardrail foundation exists. |
| Layer 10 | Synthesizes strategy across stored evidence. | Durable hidden strategy memory. | Read-only response models only in MVP. | Derived strategy MVP started. |
