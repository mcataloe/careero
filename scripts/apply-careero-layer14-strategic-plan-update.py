#!/usr/bin/env python3
"""Apply the Layer 14 strategic-plan update to Careero's canonical planning doc.

Run from the root of the mjcataldi/careero repository:

    python scripts/apply-careero-layer14-strategic-plan-update.py
    git diff -- docs/careero-application-plan-and-layer-status.md
    git add docs/careero-application-plan-and-layer-status.md
    git commit -m "Add Layer 14 model choice credits and API intelligence strategy"
"""
from pathlib import Path

DOC_PATH = Path("docs/careero-application-plan-and-layer-status.md")
SECTION_PATH = Path("docs/careero-layer-14-strategic-plan-section.md")

STEP_6 = """## Step 6 — Layer 14 Strategic Recon

### Goal

Plan model choice, credits, API-only job ingestion, and company research caching without destabilizing the existing workflow roadmap.

### Tasks

- Define the Prompt Compiler module model.
- Define the model provider/catalog/price snapshot architecture.
- Define default model selection UX by artifact type.
- Define prompt-only export behavior.
- Define credit wallet, reservation, debit, refund, rollover, and top-up rules.
- Define provider/tool/API cost tracking.
- Validate official API access for target job posting sources.
- Define normalized `job_posting` ingestion records.
- Define company research source categories, source records, facts, summaries, and TTLs.
- Define source licensing/compliance review workflow.
- Add a backlog item to revisit scraping later; do not implement scraping in this pass.

### Exit criteria

- Layer 14 implementation slices are ready.
- API-only boundary is clear.
- Scraping revisit is tracked as a future TODO only.
- Credit economics are transparent and ledger-backed.
- Source freshness and source governance rules are explicit.
"""


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one match for anchor, found {count}: {old[:120]!r}")
    return text.replace(old, new, 1)


def main() -> None:
    if not DOC_PATH.exists():
        raise SystemExit(f"Could not find {DOC_PATH}. Run this from the repo root.")
    if not SECTION_PATH.exists():
        raise SystemExit(f"Could not find {SECTION_PATH}.")

    text = DOC_PATH.read_text(encoding="utf-8")
    layer_14_section = SECTION_PATH.read_text(encoding="utf-8").strip()

    if "## Layer 14 — Model Choice, Credits & API-First Intelligence" in text:
        print("Layer 14 section already appears to be present; no changes made.")
        return

    text = replace_once(
        text,
        "The current strategic move is to stabilize existing workflow and intelligence reality while introducing Layer 10 as derived, read-only career strategy synthesis.",
        "The current strategic move is to stabilize existing workflow and intelligence reality while introducing Layer 10 as derived, read-only career strategy synthesis. A later strategic expansion now belongs after Layer 13: user-selected model routing, credit economics, API-only job-posting ingestion, and source-governed company research memory.",
    )

    text = replace_once(
        text,
        "- marketplace or employer-side capabilities\n",
        "- marketplace or employer-side capabilities\n- user-selected model routing for resumes, cover letters, company research, interview prep, and future generated content\n- modular prompt compiler architecture beyond the current artifact-generation prompt foundations\n- provider/model catalog management across OpenAI, Anthropic, Google, and any future model gateway\n- model price snapshots, usage metering, credit reservation, credit debiting, and credit refunds\n- monthly credit grants, capped rollover, paid top-ups, and optional auto top-up controls\n- API-only job posting ingestion from official ATS/job-data providers\n- API-only company research ingestion, source record caching, fact extraction, summary regeneration, and freshness tracking\n- external source licensing/compliance governance for company research and review/salary/culture data\n- scraping or restricted-source extraction; this is explicitly deferred for later legal/product/technical review\n",
    )

    text = replace_once(
        text,
        "| Layer 13 | Marketplace / Employer-Side Exploration | Future / last | Recruiter-facing workflows, ethical matching, user-controlled visibility, employer partnerships, strict disclosure rules. |",
        "| Layer 13 | Marketplace / Employer-Side Exploration | Future / last employer-facing layer | Recruiter-facing workflows, ethical matching, user-controlled visibility, employer partnerships, strict disclosure rules. |\n| Layer 14 | Model Choice, Credits & API-First Intelligence | Future / appended strategic layer | User-selected model routing, modular prompt compilation, credit-based usage, official API-only job posting ingestion, and cached company research intelligence. Scraping is not in scope and is deferred for later review. Numbering is append-only; execution can pull 14A/14B forward during Layer 11 while Layer 13 remains the last employer-side expansion. |",
    )

    text = replace_once(
        text,
        "## Layer 13 — Marketplace / Employer-Side Exploration\n\n### Status\n\nFuture / last.",
        "## Layer 13 — Marketplace / Employer-Side Exploration\n\n### Status\n\nFuture / last employer-facing layer.",
    )

    text = replace_once(
        text,
        "This layer should be last. Careero should not compromise user trust by becoming employer-first too early.",
        "This layer should remain the last employer-facing/marketplace expansion. Careero should not compromise user trust by becoming employer-first too early.",
    )

    text = replace_once(
        text,
        "---\n\n# Recommended Immediate Execution Plan",
        f"---\n\n{layer_14_section}\n\n---\n\n# Recommended Immediate Execution Plan",
    )

    text = replace_once(
        text,
        "---\n\n# Revised Build Order",
        f"---\n\n{STEP_6}\n\n---\n\n# Revised Build Order",
    )

    text = replace_once(
        text,
        "11. Layer 13 marketplace/employer-side exploration.",
        "11. Layer 13 marketplace/employer-side exploration.\n12. Layer 14 model choice, credits, and API-first intelligence. Pull 14A/14B forward during Layer 11 if billing/model usage requires it; keep 14C/14D API-only; keep Layer 13 as the last employer-side expansion.",
    )

    text = replace_once(
        text,
        "- Marketplace last.",
        "- Marketplace/employer-side work last among employer-facing capabilities.\n- User-selected model flexibility under a Careero-owned prompt framework.\n- Credit transparency, usage metering, capped rollover, and top-up economics.\n- API-first job and company intelligence with source freshness and no scraping in current scope.",
    )

    text = replace_once(
        text,
        "- Introduce Opportunity Model Strategy as Layer 7.",
        "- Introduce Opportunity Model Strategy as Layer 7.\n- Add Layer 14 as an appended model-choice, credit-economy, API-first intelligence layer; parts of 14A/14B may execute with Layer 11 productization even though the layer is documented after Layer 13.",
    )

    text = replace_once(
        text,
        "- Marketplace/employer-side work until user-side trust is strong.",
        "- Marketplace/employer-side work until user-side trust is strong.\n- Any scraping strategy until official APIs, licensed providers, source terms, privacy risks, and retention rules have been reviewed.",
    )

    text = replace_once(
        text,
        "- Automation suggests actions around opportunity lifecycle.\n\nThis document should be updated whenever implementation reality changes, especially after branch reconciliation, Layer 4 completion, and Layer 7 LEAP Recon output.",
        "- Automation suggests actions around opportunity lifecycle.\n\nLayer 14 adds a second strategic center for productization-scale intelligence:\n\n> Careero should let users choose the model and budget while Careero controls prompts, source grounding, quality, cost exposure, and API-only research memory.\n\nThe long-term strategic system is not merely an AI resume generator. It is a career application intelligence platform where users can generate, compare, and improve job-search materials using the model, research depth, and budget they choose while Careero protects source truth, freshness, and user control.\n\nThis document should be updated whenever implementation reality changes, especially after branch reconciliation, Layer 4 completion, Layer 7 LEAP Recon output, and Layer 14 source/provider validation.",
    )

    backup_path = DOC_PATH.with_suffix(DOC_PATH.suffix + ".bak")
    backup_path.write_text(DOC_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    DOC_PATH.write_text(text, encoding="utf-8")
    print(f"Updated {DOC_PATH}")
    print(f"Backup written to {backup_path}")


if __name__ == "__main__":
    main()
