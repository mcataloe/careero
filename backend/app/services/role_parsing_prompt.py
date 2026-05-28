import json
from typing import Any

from app.schemas.role_parsing import RoleParseRequest

ROLE_PARSER_VERSION = "role_parser_v1"

ROLE_PARSING_SYSTEM_PROMPT = """
You are Careero's role intake parser. Extract only facts explicitly present in
the supplied pasted job content and optional user-provided URL/source. Do not
infer compensation, company URLs, dates, remote type, or facts not present in
the input. Missing values must be null. Preserve original wording where useful,
normalize whitespace, and return structured JSON only.
""".strip()


ROLE_PARSING_RULES = """
Rules:
- Output must match the supplied schema exactly.
- Use null for missing or uncertain scalar values.
- compensationMin and compensationMax must be numbers only when explicitly stated.
- Do not estimate compensation from title, seniority, location, or market knowledge.
- remoteType may be remote, hybrid, or onsite only when explicitly stated.
- companyWebsite and jobUrl must not be fabricated.
- datePosted must only be set when explicitly present as a date.
- warnings should explain missing/uncertain important fields.
- If the input is irrelevant or does not include a complete job posting, still
  return valid schema output: null scalar fields, empty extractedSkills, and a
  warning such as "Input did not include a complete job posting."
- confidence values must be 0.0 to 1.0 and reflect extraction confidence.
- Do not include markdown, prose, comments, or extra fields.
""".strip()


def build_role_parsing_prompt(payload: RoleParseRequest) -> list[dict[str, str]]:
    prompt_payload: dict[str, Any] = {
        "input": {
            "rawText": payload.raw_text,
            "source": payload.source.value if payload.source else None,
            "jobUrl": payload.job_url,
        },
        "parserVersion": ROLE_PARSER_VERSION,
        "rules": ROLE_PARSING_RULES,
        "expectedNullHandling": "Use null, not empty strings, for missing values.",
    }
    return [
        {
            "role": "system",
            "content": ROLE_PARSING_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": json.dumps(prompt_payload, indent=2, sort_keys=True),
        },
    ]
