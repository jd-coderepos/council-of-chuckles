"""Advisor archetype assignment."""

from __future__ import annotations


ARCHETYPES = [
    "Sage",
    "Strategist",
    "Challenger",
    "Comforter",
    "Trickster",
    "Scientist",
    "Poet",
    "Builder",
    "Skeptic",
    "Spiritual Guide",
]

KEYWORD_ARCHETYPES: list[tuple[str, str]] = [
    ("stoic", "Sage"),
    ("resilience", "Challenger"),
    ("discipline", "Builder"),
    ("productivity", "Strategist"),
    ("strategy", "Strategist"),
    ("psychologist", "Scientist"),
    ("research", "Scientist"),
    ("compassion", "Comforter"),
    ("healing", "Comforter"),
    ("poet", "Poet"),
    ("lyrical", "Poet"),
    ("spiritual", "Spiritual Guide"),
    ("faith", "Spiritual Guide"),
    ("skeptic", "Skeptic"),
    ("risk", "Skeptic"),
    ("humor", "Trickster"),
    ("witty", "Trickster"),
    ("action", "Builder"),
    ("entrepreneur", "Builder"),
]

CATEGORY_DEFAULTS = {
    "Classical Foundations": ["Sage", "Spiritual Guide"],
    "Self-Help Pioneers": ["Builder", "Strategist"],
    "Psychology and Human Potential": ["Scientist", "Comforter"],
    "Business and Strategy": ["Strategist", "Builder"],
    "Creativity and Art": ["Poet", "Trickster"],
    "Philosophers and Thinkers": ["Sage", "Skeptic"],
    "Modern Voices": ["Builder", "Comforter"],
    "Broad Influence": ["Sage", "Challenger"],
}


def assign_archetypes(advisor: dict) -> list[str]:
    haystack = " ".join(
        str(advisor.get(key, ""))
        for key in ["best_for", "category", "role", "core_wisdom", "signature_style", "mastermind_voice", "comic_voice"]
    ).lower()
    found: list[str] = []
    for keyword, archetype in KEYWORD_ARCHETYPES:
        if keyword in haystack and archetype not in found:
            found.append(archetype)
    for archetype in CATEGORY_DEFAULTS.get(advisor.get("category", ""), ["Sage"]):
        if archetype not in found:
            found.append(archetype)
    return found[:3]


NEED_ARCHETYPES = {
    "courage": ["Challenger", "Builder"],
    "perspective": ["Sage", "Skeptic"],
    "action": ["Builder", "Strategist"],
    "comfort": ["Comforter", "Spiritual Guide"],
    "structure": ["Strategist", "Builder"],
    "humor": ["Trickster"],
    "rest": ["Comforter", "Sage"],
    "clarity": ["Sage", "Scientist"],
    "patience": ["Sage", "Spiritual Guide"],
    "discipline": ["Challenger", "Builder"],
    "self-compassion": ["Comforter", "Poet"],
    "decision support": ["Strategist", "Skeptic"],
}

