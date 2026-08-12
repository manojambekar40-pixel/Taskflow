"""
ai_parser.py
------------
Deterministic (non-LLM) natural-language task parser.

This is the MANDATORY, grading-safe parsing path. It must work with
zero external dependencies, zero network access, and zero API keys.
The Groq LLM path (groq_service.py) is an optional enhancement that
always falls back to this parser on any failure.

Priority rule (checked in this exact order against the lowercase
description):
    1. "urgent" or "asap"              -> high
    2. "whenever" or "low priority"    -> low
    3. otherwise                       -> medium
    If BOTH a high-signal and low-signal keyword are present, high wins.

Title stripping:
    Every occurrence of urgent / asap / whenever / low priority is
    removed from the ORIGINAL-CASE description (not just the keyword
    that decided the priority), plus the matched due-date phrase.
    If nothing is left afterwards, the title becomes "Untitled task".

Date parsing (checked in this exact order, case-insensitive):
    today
    tomorrow
    next week
    next monday .. next sunday
    monday .. sunday
    The first match wins; the matched phrase is returned lowercase.
"""

import re
from backend.schemas import ParsedTask

PRIORITY_HIGH_KEYWORDS = ["urgent", "asap"]
PRIORITY_LOW_KEYWORDS = ["whenever", "low priority"]

DATE_PHRASES_IN_ORDER = [
    "today",
    "tomorrow",
    "next week",
    "next monday",
    "next tuesday",
    "next wednesday",
    "next thursday",
    "next friday",
    "next saturday",
    "next sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

ALL_STRIP_PHRASES = PRIORITY_HIGH_KEYWORDS + PRIORITY_LOW_KEYWORDS


def _determine_priority(lowered: str) -> str:
    has_high = any(kw in lowered for kw in PRIORITY_HIGH_KEYWORDS)
    has_low = any(kw in lowered for kw in PRIORITY_LOW_KEYWORDS)
    if has_high:
        return "high"
    if has_low:
        return "low"
    return "medium"


def _determine_due_date(lowered: str) -> str | None:
    for phrase in DATE_PHRASES_IN_ORDER:
        if phrase in lowered:
            return phrase
    return None


def _strip_phrase_case_insensitive(text: str, phrase: str) -> str:
    """Remove every case-insensitive occurrence of `phrase` from `text`."""
    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
    return pattern.sub("", text)


def _build_title(original_description: str, matched_date_phrase: str | None) -> str:
    title = original_description
    for phrase in ALL_STRIP_PHRASES:
        title = _strip_phrase_case_insensitive(title, phrase)
    if matched_date_phrase:
        title = _strip_phrase_case_insensitive(title, matched_date_phrase)

    # Collapse extra whitespace left behind by removed phrases.
    title = re.sub(r"\s+", " ", title).strip(" ,.-")

    if not title:
        title = "Untitled task"
    return title


def parse_task_description(description: str) -> ParsedTask:
    """
    Deterministic parser entry point. Always succeeds — never raises
    for well-formed string input, and never requires network access.
    """
    lowered = description.lower()

    priority = _determine_priority(lowered)
    due_date_hint = _determine_due_date(lowered)
    title = _build_title(description, due_date_hint)

    return ParsedTask(title=title, priority=priority, due_date_hint=due_date_hint)
