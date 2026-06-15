"""Conservative text safety routing."""

from __future__ import annotations

from .languages import localized_copy


CRISIS_KEYWORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "self harm",
    "self-harm",
    "hurt myself",
    "overdose",
    "cannot go on",
    "can't go on",
    "in danger",
    "emergency",
    "abused",
    "abuse",
    "domestic violence",
    "assault",
    "being threatened",
]

PROFESSIONAL_KEYWORDS = [
    "medical",
    "diagnosis",
    "prescription",
    "medication",
    "legal",
    "lawyer",
    "lawsuit",
    "contract",
    "immigration",
    "visa",
    "residence permit",
    "tax",
    "financial advice",
    "investment",
    "stocks",
    "debt",
]

HARMFUL_HUMOR_PATTERNS = [
    "make fun of",
    "insult",
    "humiliate",
    "racist joke",
    "sexist joke",
    "joke about disability",
    "mock someone's trauma",
    "mock someones trauma",
    "mock their trauma",
    "demean",
]

PROTECTED_GROUP_TERMS = [
    "race",
    "religion",
    "gender",
    "sexuality",
    "disability",
    "disabled",
    "nationality",
    "ethnicity",
    "women",
    "men",
    "gay",
    "trans",
    "immigrant",
]


def _contains_any(text: str, needles: list[str]) -> bool:
    haystack = text.lower()
    return any(needle in haystack for needle in needles)


def detect_crisis(text: str) -> bool:
    return _contains_any(text, CRISIS_KEYWORDS)


def detect_professional_advice(text: str) -> bool:
    return _contains_any(text, PROFESSIONAL_KEYWORDS)


def detect_harmful_humor_request(text: str) -> bool:
    lowered = text.lower()
    if any(pattern in lowered for pattern in HARMFUL_HUMOR_PATTERNS):
        return True
    return any(group in lowered for group in PROTECTED_GROUP_TERMS) and any(
        word in lowered for word in ["joke", "mock", "insult", "ridicule"]
    )


def safe_support_response(language: str = "English") -> str:
    return localized_copy(language)["safe_support"]


def professional_disclaimer(language: str = "English") -> str:
    return localized_copy(language)["professional_disclaimer"]
