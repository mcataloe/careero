from decimal import Decimal
from types import SimpleNamespace

from app.config import Settings
from app.schemas.stride_evaluations import StrideEvaluationCreate
from app.services.stride_ai import (
    AIStrideEvaluationOutput,
    AIStrideSection,
    AIStrideItem,
    OpenAIStrideEvaluator,
    merge_ai_analysis,
    reset_ai_evaluation_session_counter,
)
from app.services.stride_rules import evaluate_role


def role_fixture():
    return SimpleNamespace(
        title="Senior Platform Engineer",
        company=SimpleNamespace(
            name="Example Company",
            website_url="https://example.com",
        ),
        location="Chicago, IL",
        remote_type="remote",
        compensation_min=Decimal("140000"),
        compensation_max=Decimal("170000"),
        compensation_currency="USD",
        job_url="https://example.com/jobs/123",
        raw_description="Build Python and PostgreSQL platforms.",
        normalized_description="Senior platform role using Python and PostgreSQL.",
        status="found",
        date_found=None,
        date_posted=None,
    )


def ai_output() -> AIStrideEvaluationOutput:
    grounded = AIStrideSection(
        status="grounded",
        score=82,
        notes="Grounded in the supplied job description.",
        evidence=["Python and PostgreSQL platforms"],
    )
    return AIStrideEvaluationOutput(
        summary="AI-enriched grounded STRIDE analysis.",
        strengths=[
            AIStrideItem(
                code="technical_match",
                message="Python and PostgreSQL are explicit role signals.",
                evidence="Python and PostgreSQL platforms",
            )
        ],
        concerns=[],
        resume_alignment=grounded,
        compensation_alignment=grounded,
        seniority_alignment=grounded,
        remote_alignment=grounded,
        technical_alignment=grounded,
        company_risk=grounded,
        ats_keywords=["postgresql", "python"],
        missing_keywords=[],
        evidence_matches=[
            AIStrideItem(
                code="python_platforms",
                message="Python platform experience is supported.",
                evidence="Python and PostgreSQL platforms",
                status="strong_match",
            )
        ],
        evidence_gaps=[
            AIStrideItem(
                code="leadership_scope",
                message="Leadership scope is only partially supported.",
                evidence=None,
                status="partial_match",
            )
        ],
        positioning_opportunities=[
            AIStrideItem(
                code="platform_positioning",
                message="Position around platform ownership.",
                evidence="Platform role signals",
                status="grounded",
            )
        ],
        unsupported_claim_warnings=[
            AIStrideItem(
                code="no_kubernetes_evidence",
                message="Do not claim Kubernetes experience without source evidence.",
                evidence=None,
                status="no_evidence",
            )
        ],
        ai_overall_score=82,
        ai_recommendation="apply",
        ai_confidence_level="medium",
        grounding_notes=["No external research used."],
    )


class FakeResponses:
    def __init__(self, parsed=None, error: Exception | None = None) -> None:
        self.parsed = parsed
        self.error = error

    def parse(self, **kwargs):
        self.kwargs = kwargs
        if self.error is not None:
            raise self.error
        return SimpleNamespace(output_parsed=self.parsed)


class FakeClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


def enabled_settings(**overrides) -> Settings:
    values = {
        "enable_ai_evaluations": True,
        "openai_api_key": "sk-test",
        "openai_default_evaluation_model": "gpt-5-mini",
        "openai_timeout_seconds": 30,
        "openai_max_output_tokens": 2500,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_openai_success_is_validated_and_merged() -> None:
    reset_ai_evaluation_session_counter()
    role = role_fixture()
    payload = StrideEvaluationCreate(user_context={"target_keywords": ["python"]})
    baseline = evaluate_role(role, payload.user_context, payload.user_notes)
    responses = FakeResponses(parsed=ai_output())
    evaluator = OpenAIStrideEvaluator(
        enabled_settings(),
        client=FakeClient(responses),
    )

    ai_metadata = evaluator.enrich(role=role, payload=payload, baseline=baseline)
    merged = merge_ai_analysis(baseline, ai_metadata)

    assert ai_metadata["ai_status"] == "completed"
    assert responses.kwargs["model"] == "gpt-5-mini"
    assert responses.kwargs["max_output_tokens"] == 2500
    assert ai_metadata["ai_input_token_estimate"] is not None
    assert ai_metadata["ai_output_token_estimate"] is not None
    assert ai_metadata["ai_latency_ms"] >= 0
    assert merged["summary"] == "AI-enriched grounded STRIDE analysis."
    assert merged["recommendation"] == baseline.recommendation
    assert merged["confidence_level"] == baseline.confidence_level
    assert merged["raw_evaluation_json"]["ai_status"] == "completed"
    assert (
        merged["raw_evaluation_json"]["ai_score_context"]["canonical_score_source"]
        == "deterministic_baseline"
    )
    assert merged["raw_evaluation_json"]["ai_result"]["unsupported_claim_warnings"]
    assert (
        merged["raw_evaluation_json"]["ai_result"]["evidence_matches"][0]["status"]
        == "strong_match"
    )


def test_ai_disabled_stores_skipped_status() -> None:
    role = role_fixture()
    payload = StrideEvaluationCreate()
    baseline = evaluate_role(role, {}, None)
    evaluator = OpenAIStrideEvaluator(Settings(_env_file=None))

    metadata = evaluator.enrich(role=role, payload=payload, baseline=baseline)
    merged = merge_ai_analysis(baseline, metadata)

    assert metadata["ai_status"] == "skipped"
    assert merged["raw_evaluation_json"]["ai_status"] == "skipped"
    assert "disabled" in merged["raw_evaluation_json"]["ai_failure_reason"]


def test_ai_enabled_without_api_key_falls_back() -> None:
    role = role_fixture()
    payload = StrideEvaluationCreate()
    baseline = evaluate_role(role, {}, None)
    evaluator = OpenAIStrideEvaluator(
        enabled_settings(openai_api_key=""),
    )

    metadata = evaluator.enrich(role=role, payload=payload, baseline=baseline)

    assert metadata["ai_status"] == "skipped"
    assert "API key" in metadata["ai_failure_reason"]


def test_openai_error_falls_back_without_secret_leak() -> None:
    reset_ai_evaluation_session_counter()
    role = role_fixture()
    payload = StrideEvaluationCreate()
    baseline = evaluate_role(role, {}, None)
    evaluator = OpenAIStrideEvaluator(
        enabled_settings(),
        client=FakeClient(
            FakeResponses(error=TimeoutError("timeout for sk-secret123"))
        ),
    )

    metadata = evaluator.enrich(role=role, payload=payload, baseline=baseline)

    assert metadata["ai_status"] == "failed"
    assert metadata["ai_error_type"] == "TimeoutError"
    assert "sk-secret123" not in metadata["ai_failure_reason"]
    assert "sk-REDACTED" in metadata["ai_failure_reason"]
    assert metadata["ai_input_token_estimate"] is not None
    assert metadata["ai_output_token_estimate"] is None


def test_invalid_structured_output_falls_back() -> None:
    reset_ai_evaluation_session_counter()
    role = role_fixture()
    payload = StrideEvaluationCreate()
    baseline = evaluate_role(role, {}, None)
    evaluator = OpenAIStrideEvaluator(
        enabled_settings(),
        client=FakeClient(FakeResponses(parsed={"summary": "missing fields"})),
    )

    metadata = evaluator.enrich(role=role, payload=payload, baseline=baseline)

    assert metadata["ai_status"] == "failed"
    assert metadata["ai_error_type"] == "ValidationError"


def test_ai_session_limit_skips_without_calling_openai() -> None:
    reset_ai_evaluation_session_counter()
    role = role_fixture()
    payload = StrideEvaluationCreate()
    baseline = evaluate_role(role, {}, None)
    first_responses = FakeResponses(parsed=ai_output())
    first = OpenAIStrideEvaluator(
        enabled_settings(max_ai_evaluations_per_session=1),
        client=FakeClient(first_responses),
    )
    second_responses = FakeResponses(parsed=ai_output())
    second = OpenAIStrideEvaluator(
        enabled_settings(max_ai_evaluations_per_session=1),
        client=FakeClient(second_responses),
    )

    first_metadata = first.enrich(role=role, payload=payload, baseline=baseline)
    second_metadata = second.enrich(role=role, payload=payload, baseline=baseline)

    assert first_metadata["ai_status"] == "completed"
    assert second_metadata["ai_status"] == "skipped"
    assert "session limit" in second_metadata["ai_failure_reason"]
    assert not hasattr(second_responses, "kwargs")


def test_openai_error_log_does_not_include_secret(caplog) -> None:
    reset_ai_evaluation_session_counter()
    role = role_fixture()
    payload = StrideEvaluationCreate()
    baseline = evaluate_role(role, {}, None)
    evaluator = OpenAIStrideEvaluator(
        enabled_settings(),
        client=FakeClient(FakeResponses(error=RuntimeError("boom sk-secret123"))),
    )

    evaluator.enrich(role=role, payload=payload, baseline=baseline)

    assert "sk-secret123" not in caplog.text
