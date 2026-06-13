"""Profile-driven fallback generation that works without a loaded LLM."""

from __future__ import annotations

from .dialogue import build_dialogue_plan
from .matching import trigger_reason
from .verdict import fallback_verdict


def advisor_card_text(advisor: dict, topic: str, analysis: dict, mode: str, output_language: str) -> str:
    if output_language != "English":
        prefix = f"Fallback mode is currently English-only; requested language: {output_language}.\n"
    else:
        prefix = ""
    voice = advisor.get("comic_voice") if mode == "Comic Relief Mode" else advisor.get("mastermind_voice")
    humor = (
        f"\nRidiculous but useful reminder: {advisor.get('catchphrase')}"
        if mode in {"Comic Relief Mode", "Campfire Council Mode"}
        else ""
    )
    return (
        f"{prefix}Title: In the spirit of {advisor.get('name')}\n"
        f"Perspective: {voice} For this topic, notice the pattern of {analysis.get('summary', 'uncertainty')}.\n"
        f"Hidden wisdom: {advisor.get('core_wisdom')}\n"
        f"Tiny next action: Do one ten-minute move that expresses {analysis.get('needs', ['clarity'])[0]} before trying to solve the whole story."
        f"{humor}"
    )


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
    for turn in plan["turn_order"]:
        advisor = advisor_map[turn["speaker_id"]]
        need = analysis.get("needs", ["clarity"])[0]
        theme = analysis.get("themes", ["uncertainty"])[0]
        if turn["function"] == "comic relief":
            line = f"Inspired by {advisor['name']}: {advisor.get('catchphrase')}"
        elif turn["function"] == "practical action":
            line = f"Inspired by {advisor['name']}: make {need} physical: open the file, send the message, or write the first plain sentence."
        elif turn["function"] == "challenge":
            line = f"Inspired by {advisor['name']}: the fear may be loud, but it has not earned veto power over your next step."
        elif turn["function"] == "synthesize":
            line = f"Inspired by {advisor['name']}: the council sees {theme}; answer it with one small act, not a grand identity trial."
        elif turn["function"] == "reframe":
            line = f"Inspired by {advisor['name']}: this is not proof that you are failing; it is information asking for a kinder plan."
        else:
            line = f"Inspired by {advisor['name']}: begin by naming the concern without letting it become your whole weather system."
        if output_language != "English":
            line = f"[Fallback English; requested {output_language}] {line}"
        lines.append((advisor, line, turn["function"], turn["trigger_reason"]))
    return plan, lines


def verdict_text(topic: str, analysis: dict, active_speakers: list[dict], output_language: str) -> str:
    text = fallback_verdict(topic, analysis, active_speakers, output_language)
    if output_language != "English":
        return f"Fallback mode is currently English-only; requested language: {output_language}.\n{text}"
    return text


def trigger_reasons(active_speakers: list[dict], analysis: dict) -> dict[str, str]:
    return {advisor["id"]: trigger_reason(advisor, analysis) for advisor in active_speakers}

