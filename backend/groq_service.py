"""
groq_service.py
----------------
Optional Groq LLM parsing path (OpenAI-compatible API).

Rules enforced here:
    - Only used when USE_REAL_LLM=true AND GROQ_API_KEY is set.
    - Any failure (network error, malformed JSON, failed Pydantic
      validation) falls back to the deterministic mock parser.
    - The API key is never exposed to the frontend; this module only
      ever runs server-side.
"""

import os
import json
import logging

from backend.schemas import ParsedTask
from backend.ai_parser import parse_task_description

logger = logging.getLogger("taskflow.groq")

USE_REAL_LLM = os.getenv("USE_REAL_LLM", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SYSTEM_PROMPT = (
    "You are a task parsing assistant. Convert natural language task "
    "descriptions into structured JSON. Return ONLY valid JSON. "
    "Required fields: title, priority, due_date_hint. "
    "priority must be exactly one of: low, medium, high. "
    "due_date_hint may be a short string or null. "
    "Do not invent any additional fields."
)


def _get_client():
    """Lazily build an OpenAI-compatible client pointed at Groq."""
    from openai import OpenAI
    return OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")


def _call_groq(description: str) -> ParsedTask:
    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": description},
        ],
        temperature=0,
    )
    raw_content = response.choices[0].message.content

    # Guard against models that wrap JSON in markdown fences.
    cleaned = raw_content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).replace("json", "", 1)

    data = json.loads(cleaned)  # raises on malformed JSON -> caught below
    return ParsedTask(**data)  # raises on validation failure -> caught below


def parse_with_ai(description: str) -> ParsedTask:
    """
    Main entry point used by the /tasks/quick-add endpoint.

    Never raises: always returns a valid ParsedTask, either from Groq
    or, on any failure whatsoever, from the deterministic mock parser.
    """
    if not USE_REAL_LLM or not GROQ_API_KEY:
        return parse_task_description(description)

    try:
        return _call_groq(description)
    except Exception as exc:  # noqa: BLE001 - intentionally broad: never crash
        logger.warning("Groq parsing failed, falling back to mock parser: %s", exc)
        return parse_task_description(description)
