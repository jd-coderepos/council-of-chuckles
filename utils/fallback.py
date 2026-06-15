"""Profile-driven fallback generation that works without a loaded LLM."""

from __future__ import annotations

from .dialogue import build_dialogue_plan
from .languages import localized_copy, localized_situation
from .matching import trigger_reason
from .verdict import fallback_verdict


def advisor_card_text(advisor: dict, topic: str, analysis: dict, mode: str, output_language: str) -> str:
    copy = localized_copy(output_language)
    situation = localized_situation(output_language, topic)
    parts = [
        copy["card_title"].format(advisor=advisor.get("name", "the advisor"), situation=situation),
        copy["card_perspective"].format(advisor=advisor.get("name", "the advisor"), situation=situation),
        copy["card_hidden"].format(advisor=advisor.get("name", "the advisor"), situation=situation),
        copy["card_action"].format(advisor=advisor.get("name", "the advisor"), situation=situation),
    ]
    if mode in {"Comic Relief Mode", "Campfire Council Mode"}:
        parts.append(copy["card_reminder"].format(advisor=advisor.get("name", "the advisor"), situation=situation))
    return "\n".join(parts)


def campfire_lines(
    active_speakers: list[dict],
    topic: str,
    analysis: dict,
    turns: int,
    mood: str,
    output_language: str,
) -> tuple[dict, list[tuple[dict, str, str, str]]]:
    plan = build_dialogue_plan(active_speakers, analysis, "Campfire Council Mode", turns, mood)
    lines = []
    advisor_map = {advisor["id"]: advisor for advisor in active_speakers}
    copy = localized_copy(output_language)
    turn_copy = copy["turns"]
    for turn in plan["turn_order"]:
        advisor = advisor_map[turn["speaker_id"]]
        line = turn_copy.get(turn["function"], turn_copy["validate"])
        lines.append((advisor, line, turn["function"], turn["trigger_reason"]))
    return plan, lines


def verdict_text(topic: str, analysis: dict, active_speakers: list[dict], output_language: str) -> str:
    return fallback_verdict(topic, analysis, active_speakers, output_language)


def trigger_reasons(active_speakers: list[dict], analysis: dict) -> dict[str, str]:
    return {advisor["id"]: trigger_reason(advisor, analysis) for advisor in active_speakers}
