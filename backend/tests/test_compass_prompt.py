from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.services.compass_prompt import build_compass_evaluation_prompt
from app.services.compass_rules import evaluate_role


def role_fixture(**overrides):
    values = {
        "title": "Senior Platform Engineer",
        "company": SimpleNamespace(
            name="Example Company",
            website_url="https://example.com",
        ),
        "location": "Chicago, IL",
        "remote_type": "remote",
        "compensation_min": Decimal("140000"),
        "compensation_max": Decimal("170000"),
        "compensation_currency": "USD",
        "job_url": "https://example.com/jobs/123",
        "raw_description": "Build Python and PostgreSQL platforms.",
        "normalized_description": "Senior platform role using Python.",
        "status": "found",
        "date_found": date(2026, 5, 13),
        "date_posted": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_prompt_includes_role_baseline_rules_and_grounding_instructions() -> None:
    role = role_fixture()
    baseline = evaluate_role(
        role,
        {"target_keywords": ["python"], "preferred_remote_type": "remote"},
    )

    messages = build_compass_evaluation_prompt(
        role=role,
        baseline=baseline,
        user_notes="Focus on fit.",
        user_context={"target_keywords": ["python"]},
    )
    prompt_text = "\n".join(message["content"] for message in messages)

    assert "Senior Platform Engineer" in prompt_text
    assert "Example Company" in prompt_text
    assert "Chicago, IL" in prompt_text
    assert "140000" in prompt_text
    assert "strategic fit" in prompt_text
    assert "dimension_scores" in prompt_text
    assert "Do not invent resume facts" in prompt_text
    assert "Do not generate resumes" in prompt_text
    assert "sk-" not in prompt_text


def test_prompt_includes_active_resume_source_when_available() -> None:
    role = role_fixture()
    baseline = evaluate_role(role, {})
    active_resume_source = SimpleNamespace(
        id="version-id",
        version_label="master-v1",
        normalized_summary="Senior engineer with Python platform experience.",
        raw_text="Built Python services, PostgreSQL systems, and platform tooling.",
        is_active=True,
        source=SimpleNamespace(
            id="source-id",
            name="Master Resume",
            source_type="master_resume",
        ),
    )

    messages = build_compass_evaluation_prompt(
        role=role,
        baseline=baseline,
        user_notes=None,
        user_context={},
        active_resume_source=active_resume_source,
    )
    prompt_text = "\n".join(message["content"] for message in messages)

    assert "active_resume_source" in prompt_text
    assert "Master Resume" in prompt_text
    assert "Built Python services" in prompt_text
    assert "strong_match" in prompt_text
    assert "no_evidence" in prompt_text


def test_prompt_handles_missing_compensation_and_description() -> None:
    role = role_fixture(
        compensation_min=None,
        compensation_max=None,
        raw_description=None,
        normalized_description=None,
    )
    baseline = evaluate_role(role, {})

    messages = build_compass_evaluation_prompt(
        role=role,
        baseline=baseline,
        user_notes=None,
        user_context={},
    )
    prompt_text = "\n".join(message["content"] for message in messages)

    assert '"min": null' in prompt_text
    assert '"raw_description": null' in prompt_text
    assert '"active_resume_source": null' in prompt_text
    assert "insufficient_data" in prompt_text
