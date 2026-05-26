from dataclasses import dataclass, field
from decimal import Decimal

from app.constants import CompassConfidenceLevel, CompassRecommendation
from app.services.compass_rules import (
    RuleConcern,
    detect_concerns,
    evaluate_role,
    select_recommendation,
)


@dataclass
class CompanyFixture:
    name: str = "Example Company"
    website_url: str | None = "https://example.com"


@dataclass
class RoleFixture:
    title: str
    raw_description: str | None
    normalized_description: str | None = None
    job_url: str | None = "https://example.com/jobs/platform-engineer"
    location: str | None = "Chicago, IL"
    remote_type: str | None = "remote"
    compensation_min: Decimal | None = Decimal("140000")
    compensation_max: Decimal | None = Decimal("170000")
    compensation_currency: str | None = "USD"
    status: str = "found"
    company: CompanyFixture = field(default_factory=CompanyFixture)


STRONG_DESCRIPTION = """
Senior Platform Engineer responsible for designing and building internal developer
platforms. You will own Python and FastAPI services, PostgreSQL data models,
React TypeScript interfaces, AWS infrastructure, Docker delivery, and Terraform
automation. The role partners with product and security teams, mentors engineers,
ships reliable systems, and maintains production observability.
"""

WEAK_DESCRIPTION = """
Rockstar needed for a fast-paced environment. Wear many hats. Other duties as
assigned. Great opportunity with competitive salary.
"""

AMBIGUOUS_DESCRIPTION = "Engineer role. Help the team."


def strong_role() -> RoleFixture:
    return RoleFixture(title="Senior Platform Engineer", raw_description=STRONG_DESCRIPTION)


def weak_role() -> RoleFixture:
    return RoleFixture(
        title="Engineer",
        raw_description=WEAK_DESCRIPTION,
        remote_type="onsite",
        compensation_min=None,
        compensation_max=None,
        company=CompanyFixture(name="Unknown Startup", website_url=None),
    )


def ambiguous_role() -> RoleFixture:
    return RoleFixture(
        title="Engineer",
        raw_description=AMBIGUOUS_DESCRIPTION,
        remote_type=None,
        location=None,
        compensation_min=None,
        compensation_max=None,
    )


def test_strong_fit_scores_apply_with_high_confidence() -> None:
    result = evaluate_role(
        strong_role(),
        {
            "preferred_remote_type": "remote",
            "target_compensation_min": "130000",
            "target_seniority": "senior",
            "target_keywords": ["python", "postgresql", "fastapi", "typescript"],
            "avoid_keywords": ["php"],
            "preferred_locations": ["chicago"],
        },
    )

    assert result.overall_score >= Decimal("75")
    assert result.recommendation == CompassRecommendation.APPLY.value
    assert result.confidence_level == CompassConfidenceLevel.HIGH.value
    assert result.ats_keywords == ["fastapi", "postgresql", "python", "typescript"]
    assert result.missing_keywords == []
    assert result.raw_evaluation_json["ruleset_version"] == "phase_2b_deterministic_v1"


def test_weak_fit_scores_skip_with_risk_flags() -> None:
    result = evaluate_role(
        weak_role(),
        {
            "preferred_remote_type": "remote",
            "target_compensation_min": "150000",
            "target_seniority": "senior",
            "target_keywords": ["python", "kubernetes"],
        },
    )

    assert result.recommendation == CompassRecommendation.SKIP.value
    assert result.confidence_level == CompassConfidenceLevel.LOW.value
    assert any(concern["code"] == "remote_mismatch" for concern in result.concerns)
    assert result.raw_evaluation_json["risk_flags"]


def test_ambiguous_role_needs_review_with_low_confidence() -> None:
    result = evaluate_role(ambiguous_role(), {})

    assert result.recommendation == CompassRecommendation.NEEDS_REVIEW.value
    assert result.confidence_level == CompassConfidenceLevel.LOW.value
    assert any(concern["code"] == "generic_description" for concern in result.concerns)


def test_recommendation_thresholds_are_conservative() -> None:
    assert (
        select_recommendation(80, CompassConfidenceLevel.HIGH.value)
        == CompassRecommendation.APPLY.value
    )
    assert (
        select_recommendation(60, CompassConfidenceLevel.MEDIUM.value)
        == CompassRecommendation.MONITOR.value
    )
    assert (
        select_recommendation(45, CompassConfidenceLevel.MEDIUM.value)
        == CompassRecommendation.NEEDS_REVIEW.value
    )
    assert (
        select_recommendation(39, CompassConfidenceLevel.HIGH.value)
        == CompassRecommendation.SKIP.value
    )
    assert (
        select_recommendation(90, CompassConfidenceLevel.LOW.value)
        == CompassRecommendation.NEEDS_REVIEW.value
    )
    assert (
        select_recommendation(
            90,
            CompassConfidenceLevel.HIGH.value,
            [
                RuleConcern(
                    code="remote_mismatch",
                    severity="high",
                    message="Mismatch",
                    dimension="remote_location_alignment",
                )
            ],
        )
        == CompassRecommendation.SKIP.value
    )


def test_risk_flag_detection_covers_expected_concerns() -> None:
    sprawl_role = RoleFixture(
        title="Engineer",
        raw_description=(
            "Build Java Python Go React TypeScript Node AWS Azure Kubernetes Docker "
            "Terraform Kafka Redis GraphQL SQL platforms and other systems."
        ),
        remote_type="hybrid",
        compensation_min=None,
        compensation_max=None,
    )

    concerns = detect_concerns(
        sprawl_role,
        {"preferred_remote_type": "remote"},
    )
    codes = {concern.code for concern in concerns}

    assert {
        "missing_compensation",
        "unclear_seniority",
        "remote_mismatch",
        "technology_sprawl",
    }.issubset(codes)


def test_target_keywords_create_ats_matches_and_missing_keywords() -> None:
    result = evaluate_role(
        strong_role(),
        {
            "target_keywords": ["python", "postgresql", "kubernetes"],
        },
    )

    assert result.ats_keywords == ["postgresql", "python"]
    assert result.missing_keywords == ["kubernetes"]
