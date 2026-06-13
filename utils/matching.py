"""Transparent advisor matching and active speaker selection."""

from __future__ import annotations

import random
from collections import defaultdict

from .archetypes import NEED_ARCHETYPES


def score_advisor(advisor: dict, analysis: dict) -> float:
    text = " ".join(
        [
            advisor.get("category", ""),
            advisor.get("role", ""),
            advisor.get("core_wisdom", ""),
            advisor.get("signature_style", ""),
            advisor.get("mastermind_voice", ""),
            advisor.get("comic_voice", ""),
            " ".join(advisor.get("best_for", [])),
        ]
    ).lower()

    score = 0.0
    for label in analysis.get("themes", []):
        if label in text:
            score += 2.0
        for word in label.split():
            if word in text:
                score += 0.5
    for need in analysis.get("needs", []):
        if need in text:
            score += 2.0
        for archetype in NEED_ARCHETYPES.get(need, []):
            if archetype in advisor.get("archetypes", []):
                score += 1.4
    for emotion in analysis.get("emotions", []):
        if emotion in text:
            score += 0.8
    return score


def _limit(n: int, count: int) -> int:
    if count <= 0:
        return 0
    return max(1, min(int(n or 5), count))


def _balanced(advisors: list[dict], analysis: dict, n: int) -> list[dict]:
    scored = sorted(advisors, key=lambda advisor: score_advisor(advisor, analysis), reverse=True)
    picked: list[dict] = []
    category_counts: defaultdict[str, int] = defaultdict(int)
    archetype_counts: defaultdict[str, int] = defaultdict(int)
    while scored and len(picked) < n:
        scored.sort(
            key=lambda advisor: (
                category_counts[advisor.get("category", "")],
                min(archetype_counts[a] for a in advisor.get("archetypes", ["Sage"])),
                -score_advisor(advisor, analysis),
            )
        )
        advisor = scored.pop(0)
        picked.append(advisor)
        category_counts[advisor.get("category", "")] += 1
        for archetype in advisor.get("archetypes", []):
            archetype_counts[archetype] += 1
    return picked


def select_active_speakers(
    selected_advisors: list[dict],
    analysis: dict,
    n: int,
    strategy: str,
    manual_ids: list[str] | None = None,
) -> list[dict]:
    if not selected_advisors:
        return []
    count = _limit(n, len(selected_advisors))
    strategy = strategy or "Match to my topic"

    if strategy == "Manual selection":
        manual_ids = manual_ids or []
        manual = [advisor for advisor in selected_advisors if advisor["id"] in manual_ids][:count]
        if len(manual) < min(3, count):
            fill = [advisor for advisor in selected_advisors if advisor["id"] not in {a["id"] for a in manual}]
            manual.extend(sorted(fill, key=lambda advisor: score_advisor(advisor, analysis), reverse=True)[: count - len(manual)])
        return manual[:count]

    if strategy == "Surprise me":
        pool = selected_advisors[:]
        random.shuffle(pool)
        return pool[:count]

    if strategy == "Balanced Council":
        return _balanced(selected_advisors, analysis, count)

    return sorted(selected_advisors, key=lambda advisor: score_advisor(advisor, analysis), reverse=True)[:count]


def trigger_reason(advisor: dict, analysis: dict) -> str:
    matches = []
    text = " ".join(advisor.get("best_for", []) + advisor.get("archetypes", [])).lower()
    for need in analysis.get("needs", []):
        if need in text:
            matches.append(need)
    for theme in analysis.get("themes", []):
        if any(word in text for word in theme.split()):
            matches.append(theme)
    if matches:
        return " + ".join(matches[:2])
    return "archetype balance"

