## Layer 14 — Model Choice, Credits & API-First Intelligence

### Status

Future / appended strategic layer.

Layer 14 is appended after the existing layer list to preserve roadmap continuity. It should not be interpreted as meaning every Layer 14 capability must wait until after Marketplace/Employer-Side Exploration.

Execution split:

- Layer 14A and 14B can be pulled forward with Layer 11 productization when model usage, billing, and cost controls are actively implemented.
- Layer 14C and 14D should wait until Opportunity semantics, integration boundaries, source governance, and productization controls are stable.
- Layer 13 remains the last employer-facing/trust-sensitive expansion.

### Purpose

Give Careero a flexible but controlled system for user-selected AI models, credit-based usage, API-only job-posting ingestion, and reusable company research intelligence.

The strategic goal:

> Careero owns the workflow, prompt compiler, source grounding, quality checks, credit ledger, and research memory. Users can choose model, budget, and research depth inside those guardrails.

### Hard boundary

Layer 14 is API-only for external data acquisition.

Do not implement scraping, restricted-source extraction, browser-driven collection, or terms-sensitive data collection in this layer. Scraping can be revisited later only through an explicit legal/product/technical review.

### Layer 14A — Prompt Compiler & Model Gateway

#### Purpose

Let users choose which model/provider to use for resume generation, cover letters, job fit analysis, company research, interview prep, and future content while Careero preserves standardized prompt behavior, source grounding, quality checks, and cost controls.

#### Candidate capabilities

- Model catalog with provider, model, task suitability, pricing snapshot, context limits, quality tier, latency tier, and enabled/disabled state.
- User defaults by artifact type:
  - resume model
  - cover-letter model
  - company-research model
  - interview-prep model
  - job-fit-analysis model
  - prompt-only export mode
- Careero-owned Prompt Compiler using modular, versioned prompt specifications rather than freeform one-off prompt generation.
- Model adapters for OpenAI, Anthropic, Google, and future model gateways/routers.
- Prompt-only export for users who want to copy a generated prompt into ChatGPT, Claude, Gemini, or another external model themselves.
- Optional future bring-your-own-key mode after productization, security, and support boundaries are defined.
- Quality-check pass after generation to detect factual drift, fabrication, missing job alignment, ATS readability issues, tone mismatch, and length problems.

#### Prompt Compiler model

Careero should compile prompts from structured inputs rather than generating arbitrary prompts from scratch every time.

Core modules:

- `identity_context`
- `job_extraction`
- `company_context`
- `artifact_rules`
- `model_adapter`
- `truth_policy`
- `ats_policy`
- `quality_rubric`

Prompt specs should include:

- artifact type
- target model
- user profile / source resume facts
- target job / opportunity facts
- company research context and freshness
- output contract
- guardrails
- prompt version
- source references

#### Required boundaries

- Do not allow model-specific prompt logic to leak across the product.
- Do not let job descriptions, company pages, or imported documents override system prompt rules.
- Do not let generated artifacts invent employment history, metrics, tools, certifications, clearance levels, dates, or responsibilities.
- Do not charge users for failed generation attempts unless a usable artifact is produced or the failure policy explicitly permits partial charges.
- Do not implement BYOK until account security, key storage, provider limits, and support burden are explicitly designed.

#### Guidance

Layer 14A can be pulled forward into Layer 11 when AI usage/cost controls and monetization implementation begin.

The UX should present model choice in user-facing value language, not only provider jargon:

- Fast + affordable
- Best writing balance
- Premium reasoning
- Prompt-only export

---

### Layer 14B — Credit Wallet, Usage Metering & Cost Controls

#### Purpose

Introduce a transparent credit economy for generated work, external API usage, company research, retries, and premium model selection.

Credits should represent Careero work units, not raw tokens.

Recommended internal principle:

> Credits = model cost + research/API cost + complexity + margin buffer + abuse buffer.

#### Candidate capabilities

- Monthly subscription credit grants.
- Capped rollover.
- Paid one-time top-ups.
- Optional future auto top-up with user-defined monthly cap.
- Credit reservation before a run.
- Credit debit after successful run.
- Automatic refund/release after failed run.
- Provider/tool/API cost tracking per usage event.
- Artifact-linked usage history.
- User-facing cost estimate before generation.
- User-facing cost breakdown after generation.
- Admin-adjusted credits for support/refund cases.

#### Candidate plan model

Initial product assumptions may evolve, but the strategic direction is:

- Free/trial credits for onboarding.
- Starter subscription tier.
- Pro subscription tier around the current $20/month concept.
- Search Sprint tier for short, intense job-search bursts.
- Top-up packs.
- Capped rollover to protect users from surge months without creating unlimited liability.

#### Candidate credit events

- `grant`
- `reserve`
- `debit`
- `refund`
- `expire`
- `adjustment`
- `topup_purchase`
- `rollover`

#### Candidate data model

- `credit_wallet`
- `credit_transaction`
- `usage_event`
- `model_provider`
- `model_catalog_entry`
- `model_price_snapshot`
- `artifact_usage_record`

#### Required boundaries

- Do not reduce credit balance without a durable ledger entry.
- Do not use a single mutable `credit_balance` field as the source of truth.
- Do not hide premium model multipliers.
- Do not implement paid credit expiration rules without legal review.
- Do not auto top-up without explicit opt-in and a user-visible spending cap.
- Do not let provider token cost changes silently destroy margins; model price snapshots must be refreshable.

#### Guidance

Layer 14B belongs close to Layer 11 productization because billing, metering, AI usage, and credits are inseparable.

The user should always know why something costs more:

- artifact type
- selected model tier
- company research depth
- external API cost
- retry behavior

---

### Layer 14C — API-Only Job Posting Ingestion

#### Purpose

Create an official-API-first job posting ingestion layer that can normalize postings from ATS providers and job-data providers into durable Careero records.

This should reduce manual entry while preserving source truth, provenance, deduplication, and review-before-save behavior.

#### API-only starting source list

Priority ATS/job-board sources to validate:

- Greenhouse Job Board API
- Lever Postings API / job feed
- Ashby public job posting API
- Recruitee careers site API
- SmartRecruiters posting API
- Workable API where authorized
- BambooHR ATS API where authorized
- iCIMS Job Portal API where authorized
- Workday only through an official, partner, or licensed data path

Potential licensed/broad job-data providers:

- Adzuna
- Coresignal
- Lightcast
- TheirStack
- Other licensed job-data aggregators if pricing and terms fit Careero

#### Candidate normalized record

- `job_posting`
- `job_posting_source_record`
- `job_posting_snapshot`
- `job_posting_ingestion_run`
- `job_posting_match_candidate`

Normalized fields should include:

- source type
- source job id
- company id/name/domain
- title
- department
- location raw/normalized
- remote type
- employment type
- salary min/max/currency
- description HTML/text
- skills extracted
- apply URL
- date posted
- source updated timestamp
- first seen / last seen
- status
- content hash
- provenance metadata

#### Refresh guidance

Refresh cadence should vary by source and user intent:

- saved job: frequent refresh while active
- user-tracked company: regular refresh
- generic company: daily-ish refresh
- expired job: stop after a reasonable closeout window
- aggregator search result: less frequent refresh

Exact TTLs should be validated during Layer 14 Recon.

#### Required boundaries

- Do not scrape job boards in this layer.
- Do not rely on restricted LinkedIn/Indeed/Glassdoor scraping.
- Do not auto-save imported jobs without review unless the user has explicitly enabled a safe workflow.
- Do not treat aggregator data as more authoritative than ATS/source postings.
- Do not overwrite user-edited opportunity data without preserving source snapshots and review.

#### Guidance

Layer 14C should wait until Opportunity semantics are stable enough to receive external job postings cleanly.

---

### Layer 14D — Company Research Memory & Source-Governed Caching

#### Purpose

Store company research so Careero can retrieve, refresh, compare, and reuse it across opportunities without repeatedly re-fetching the same information.

Careero should store source records, extracted facts, generated summaries, and freshness metadata separately.

Recommended principle:

> Cache facts longer than summaries. Regenerate summaries when important facts change. Always show source freshness.

#### API/licensed-source starting list

Company identity / firmographics:

- OpenCorporates
- SEC EDGAR
- Companies House
- Crunchbase or similar licensed provider

Culture / reviews / employee sentiment:

- Comparably API / partnership path
- RepVue where role-relevant
- Glassdoor only through official API, partnership, or licensed source path if available
- Other licensed review/culture providers if terms allow storage and summarization

Compensation:

- Levels.fyi API/access path
- PayScale
- BLS / CareerOneStop
- Licensed compensation-data providers

Safety / layoffs / risk:

- OSHA data
- WARN notices / state WARN datasets
- EEOC public aggregate data where useful and appropriate

News / market context:

- GDELT
- SEC filings/news for public companies
- official company blog / press room
- BuiltWith or similar technology-profile API
- Other licensed news/company intelligence providers

#### Candidate data model

- `company`
- `company_alias`
- `company_source_record`
- `company_fact`
- `company_research_summary`
- `company_research_refresh_run`
- `user_company_research_history`

#### Candidate freshness categories

- company identity
- open jobs
- culture/review aggregate
- salary benchmark
- recent news
- funding/acquisition/filing event
- safety/compliance signal
- technology stack signal
- generated summary

#### Required boundaries

- Do not store scraped review content.
- Do not store licensed raw data unless the license permits storage.
- Do not summarize restricted content in a way that violates source terms.
- Do not present cached summaries without freshness metadata.
- Do not treat employee review sources as objective truth; label them as sentiment signals.
- Do not overstate company risk from small sample sizes.
- Do not implement scraping in Layer 14D.

#### Guidance

Company research memory can become one of Careero's strongest differentiators, but only if source governance is handled cleanly.

The database should support source-level TTLs and regeneration rather than one global cache period.

---

### Layer 14E — Future Scraping Review Backlog Item

#### Purpose

Track scraping as a deferred strategic question without allowing it to leak into the near-term implementation plan.

#### TODO

Revisit scraping later only after official API and licensed-source options have been validated.

The review must include:

- legal review
- source terms review
- robots.txt / access-policy review where relevant
- privacy review
- data retention review
- storage vs summary distinction
- rate-limit and anti-abuse considerations
- user trust implications
- operational support burden
- whether the same product value can be achieved through official APIs or licensed providers

#### Current decision

Scraping is explicitly out of scope for Layer 14 implementation.

---

### Recommended Layer 14 LEAP Recon questions

- What model providers and model gateways should Careero support first?
- Which artifact types should allow user-selected models?
- What is the minimum viable Prompt Compiler architecture?
- What prompt modules are shared across artifacts?
- What prompt modules are model-specific?
- What prompt-only export experience should exist?
- What quality checks must run after model generation?
- How should Careero estimate and reserve credits before a run?
- How should failed runs, low-quality outputs, and retries affect credits?
- What credit grants, rollover caps, and top-up products make sense for MVP?
- What provider/tool/API costs need to be tracked per usage event?
- Which official job posting APIs are viable for MVP?
- What job posting fields should be normalized?
- How should source snapshots and user-edited opportunity data coexist?
- Which company research sources are official, licensed, or partner-accessible?
- What source records can be stored, summarized, or only referenced?
- What TTL should each company research source category use?
- How should Careero display source freshness and confidence?
- What data cannot be cached or summarized under source terms?
- What should be put in the future scraping review backlog?

### Recommended implementation order

1. Layer 14 Recon and source/provider validation.
2. Prompt Compiler design.
3. Model catalog and task-default UX.
4. Usage-event and credit-ledger design.
5. Credit reservation/debit/refund implementation.
6. Prompt-only export.
7. First managed model-routing implementation.
8. API-only job source abstraction.
9. First ATS API integration.
10. Company/source record model.
11. Company fact extraction and source freshness.
12. Company summary regeneration.
13. Licensed-source/culture/salary provider expansion.
14. Future scraping review, if still justified.

### Strategic guidance

Layer 14 should make Careero feel flexible without making it chaotic.

The user may choose the model and budget. Careero should control:

- prompt structure
- source grounding
- no-fabrication policy
- quality checks
- cost estimates
- credit ledger
- source provenance
- research freshness
- API/licensing boundaries

This layer should support the long-term positioning:

> Careero is a career application intelligence platform where users can generate, compare, and improve job-search materials using the model, research depth, and budget they choose.