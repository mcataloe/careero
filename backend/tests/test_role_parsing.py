from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.roles import get_role_parsing_service
from app.config import Settings
from app.main import create_app
from app.schemas.role_parsing import ParsedRole, RoleParseAIOutput, RoleParseResponse
from app.services.role_parsing import (
    RoleParsingService,
    RoleParsingUnavailableError,
    RoleParsingValidationError,
)
from app.services.role_parsing_prompt import build_role_parsing_prompt


class FakeResponses:
    def __init__(self, parsed=None) -> None:
        self.parsed = parsed

    def parse(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(output_parsed=self.parsed)


class FakeClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


def enabled_settings(**overrides) -> Settings:
    values = {
        "enable_ai_role_parsing": True,
        "openai_api_key": "sk-test",
        "openai_default_role_parsing_model": "gpt-5-mini",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def ai_output(**overrides) -> RoleParseAIOutput:
    values = {
        "roleTitle": None,
        "company": None,
        "companyWebsite": None,
        "jobUrl": None,
        "source": None,
        "location": None,
        "remoteType": None,
        "compensationMin": None,
        "compensationMax": None,
        "currency": None,
        "employmentType": None,
        "seniority": None,
        "datePosted": None,
        "normalizedDescription": None,
        "extractedSkills": [],
        "warnings": [],
        "confidence": {
            "roleTitle": None,
            "company": None,
            "companyWebsite": None,
            "jobUrl": None,
            "source": None,
            "location": None,
            "remoteType": None,
            "compensationMin": None,
            "compensationMax": None,
            "currency": None,
            "employmentType": None,
            "seniority": None,
            "datePosted": None,
            "normalizedDescription": None,
            "extractedSkills": None,
        },
    }
    confidence = values["confidence"]
    confidence_override = overrides.pop("confidence", None)
    if confidence_override is not None:
        confidence.update(confidence_override)
    values.update(overrides)
    return RoleParseAIOutput(**values)


def test_role_parsing_prompt_contains_grounding_rules() -> None:
    from app.schemas.role_parsing import RoleParseRequest

    payload = RoleParseRequest(
        rawText="Senior Engineer at Example. Remote. No salary listed.",
        source="linkedin_manual",
        jobUrl="https://example.com/jobs/1",
    )

    messages = build_role_parsing_prompt(payload)
    text = "\n".join(message["content"] for message in messages)

    assert "Do not estimate compensation" in text
    assert "Missing values must be null" in text
    assert "companyWebsite and jobUrl must not be fabricated" in text
    assert "structured JSON only" in text or "JSON only" in text
    assert "sk-" not in text


def test_role_parser_success_validates_and_applies_request_defaults() -> None:
    responses = FakeResponses(
        parsed=ai_output(
            roleTitle="Senior Backend Engineer",
            company="Example Company",
            location="Chicago, IL",
            remoteType="remote",
            compensationMin=None,
            compensationMax=None,
            currency=None,
            normalizedDescription="Build Python services.",
            extractedSkills=["Python", "PostgreSQL"],
            warnings=["Compensation was not explicitly present."],
            confidence={"roleTitle": 0.93},
        )
    )
    service = RoleParsingService(
        settings=enabled_settings(),
        client=FakeClient(responses),
    )

    result = service.parse(
        __import__("app.schemas.role_parsing", fromlist=["RoleParseRequest"]).RoleParseRequest(
            rawText="messy job post",
            source="linkedin_manual",
            jobUrl="https://example.com/jobs/1",
        )
    )

    assert result.parsed.role_title == "Senior Backend Engineer"
    assert result.parsed.source == "linkedin_manual"
    assert result.parsed.job_url == "https://example.com/jobs/1"
    assert result.metadata.parser_version == "role_parser_v1"
    assert responses.kwargs["model"] == "gpt-5-mini"


@pytest.mark.parametrize(
    "parsed",
    [
        {"roleTitle": "Engineer", "jobUrl": "not-a-url"},
        {"roleTitle": "Engineer", "remoteType": "sometimes"},
        {"roleTitle": "Engineer", "compensationMin": 200000, "compensationMax": 100000},
        {"roleTitle": "Engineer", "confidence": {"roleTitle": 1.2}},
    ],
)
def test_role_parser_rejects_invalid_ai_output(parsed: dict) -> None:
    service = RoleParsingService(
        settings=enabled_settings(),
        client=FakeClient(FakeResponses(parsed=parsed)),
    )
    request = __import__("app.schemas.role_parsing", fromlist=["RoleParseRequest"]).RoleParseRequest(
        rawText="messy job post"
    )

    with pytest.raises(RoleParsingValidationError):
        service.parse(request)


def test_role_parser_disabled_or_missing_key_is_unavailable() -> None:
    request = __import__("app.schemas.role_parsing", fromlist=["RoleParseRequest"]).RoleParseRequest(
        rawText="messy job post"
    )

    with pytest.raises(RoleParsingUnavailableError):
        RoleParsingService(settings=Settings(_env_file=None)).parse(request)

    with pytest.raises(RoleParsingUnavailableError):
        RoleParsingService(
            settings=enabled_settings(openai_api_key=""),
        ).parse(request)


def test_role_parse_endpoint_success_and_failures() -> None:
    app = create_app(Settings(_env_file=None))

    class FakeService:
        def parse(self, payload):
            return RoleParseResponse(
                parsed=ParsedRole(roleTitle="Engineer", company="Acme"),
                metadata={"parserVersion": "role_parser_v1", "model": "gpt-5-mini"},
            )

    app.dependency_overrides[get_role_parsing_service] = lambda: FakeService()
    with TestClient(app) as client:
        success = client.post("/api/roles/parse", json={"rawText": "Engineer at Acme"})
        empty = client.post("/api/roles/parse", json={"rawText": " "})

    assert success.status_code == 200
    assert success.json()["parsed"]["roleTitle"] == "Engineer"
    assert empty.status_code == 422


def test_role_parse_endpoint_maps_service_errors() -> None:
    app = create_app(Settings(_env_file=None))

    class UnavailableService:
        def parse(self, payload):
            raise RoleParsingUnavailableError("AI role parsing is disabled")

    app.dependency_overrides[get_role_parsing_service] = lambda: UnavailableService()
    with TestClient(app) as client:
        unavailable = client.post("/api/roles/parse", json={"rawText": "Engineer"})

    class InvalidService:
        def parse(self, payload):
            raise RoleParsingValidationError("Role parser returned invalid data")

    app.dependency_overrides[get_role_parsing_service] = lambda: InvalidService()
    with TestClient(app) as client:
        invalid = client.post("/api/roles/parse", json={"rawText": "Engineer"})

    assert unavailable.status_code == 503
    assert invalid.status_code == 502
