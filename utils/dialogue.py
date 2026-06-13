"""Dialogue planning for Campfire Council Mode."""

from __future__ import annotations

from .matching import trigger_reason


TURN_ARC = [
    "validate",
    "reframe",
    "gentle disagreement",
    "comic relief",
    "practical action",
    "synthesize",
    "tiny next step",
    "challenge",
]


def build_dialogue_plan(
    active_speakers: list[dict],
    analysis: dict,
    mode: str,
    turns: int,
    mood: str,
) -> dict:
    speakers = active_speakers or []
    turn_count = max(1, int(turns or 6))
    planned_turns = []
    counts = {advisor["id"]: 0 for advisor in speakers}
    max_per_speaker = max(1, (turn_count + 1) // 2)

    for index in range(turn_count):
        available = [advisor for advisor in speakers if counts[advisor["id"]] < max_per_speaker] or speakers
        speaker = available[index % len(available)]
        counts[speaker["id"]] += 1
        function = TURN_ARC[index % len(TURN_ARC)]
        planned_turns.append(
            {
                "index": index + 1,
                "speaker_id": speaker["id"],
                "speaker": speaker["name"],
                "function": function,
                "trigger_reason": trigger_reason(speaker, analysis),
            }
        )

    return {
        "scene_title": f"{mood or 'Gentle campfire'}: {analysis.get('summary', 'the question')}",
        "council_mood": mood or "Gentle campfire",
        "mode": mode,
        "turn_order": planned_turns,
    }

