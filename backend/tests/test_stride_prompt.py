from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.services.stride_prompt import build_stride_evaluation_prompt
from app.services.stride_rules import evaluate_role


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

    messages = build_stride_evaluation_prompt(
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


def test_prompt_handles_missing_compensation_and_description() -> None:
    role = role_fixture(
        compensation_min=None,
        compensation_max=None,
        raw_description=None,
        normalized_description=None,
    )
    baseline = evaluate_role(role, {})

    messages = build_stride_evaluation_prompt(
        role=role,
        baseline=baseline,
        user_notes=None,
        user_context={},
    )
    prompt_text = "\n".join(message["content"] for message in messages)

    assert '"min": null' in prompt_text
    assert '"raw_description": null' in prompt_text
    assert "insufficient_data" in prompt_text
