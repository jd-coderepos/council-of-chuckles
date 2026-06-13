"""Compact prompt builders for small multilingual models."""

from __future__ import annotations


SYSTEM_INSTRUCTION = (
    "You are Council of Chuckles, a whimsical but compassionate multilingual small-model app. "
    "You generate original advice inspired by selected advisor profiles. You do not impersonate "
    "real people and you never claim to quote them. You help users see serious topics with warmth, "
    "perspective, and optional humor. Humor must never be cruel, hateful, discriminatory, or "
    "dismissive of crisis. Answer in the requested output language."
)


def advisor_prompt(
    topic: str,
    output_language: str,
    mode: str,
    humor_intensity: int,
    compassion_level: int,
    analysis: dict,
    advisor: dict,
) -> str:
    voice = advisor.get("comic_voice") if mode == "Comic Relief Mode" else advisor.get("mastermind_voice")
    return f"""SYSTEM:
{SYSTEM_INSTRUCTION}

USER TOPIC:
{topic}

OUTPUT LANGUAGE:
{output_language}

MODE:
{mode}

HUMOR INTENSITY:
{humor_intensity}/5

COMPASSION:
{compassion_level}/5

COUNCIL ENGINE ANALYSIS:
Themes: {', '.join(analysis.get('themes', []))}
Emotions: {', '.join(analysis.get('emotions', []))}
Needs: {', '.join(analysis.get('needs', []))}

ADVISOR PROFILE:
Name: {advisor.get('name')}
Category: {advisor.get('category')}
Archetypes: {', '.join(advisor.get('archetypes', []))}
Role: {advisor.get('role')}
Core wisdom: {advisor.get('core_wisdom')}
Style: {advisor.get('signature_style')}
Voice: {voice}
Catchphrase: {advisor.get('catchphrase')}
Avoid: {advisor.get('avoid')}

TASK:
Generate an original response inspired by this advisor.
Do not claim this is a real quote.
Answer entirely in {output_language}.
Use this exact structure:
Title:
Perspective:
Hidden wisdom:
Tiny next action:
"""


def council_prompt(
    topic: str,
    output_language: str,
    mode: str,
    humor_intensity: int,
    compassion_level: int,
    analysis: dict,
    active_speakers: list[dict],
) -> str:
    profiles = "\n\n".join(
        f"{advisor['name']} ({advisor['category']}; {', '.join(advisor.get('archetypes', []))})\n"
        f"Role: {advisor.get('role')}\nWisdom: {advisor.get('core_wisdom')}\nVoice: {advisor.get('mastermind_voice')}\nAvoid: {advisor.get('avoid')}"
        for advisor in active_speakers
    )
    return f"""SYSTEM:
{SYSTEM_INSTRUCTION}

Topic: {topic}
Language: {output_language}
Mode: {mode}
Humor: {humor_intensity}/5
Compassion: {compassion_level}/5
Themes: {', '.join(analysis.get('themes', []))}
Emotions: {', '.join(analysis.get('emotions', []))}
Needs: {', '.join(analysis.get('needs', []))}

Active advisor profiles:
{profiles}

Write compact advisor cards. Each card must begin with "Inspired by [Name]".
End with a short "The Gavel Falls" verdict.
"""


def campfire_prompt(
    topic: str,
    output_language: str,
    humor_intensity: int,
    compassion_level: int,
    analysis: dict,
    active_speakers: list[dict],
    dialogue_plan: dict,
) -> str:
    profiles = "\n".join(
        f"- {advisor['name']}: {advisor.get('role')} | {', '.join(advisor.get('archetypes', []))} | {advisor.get('comic_voice')}"
        for advisor in active_speakers
    )
    turns = "\n".join(
        f"{turn['index']}. {turn['speaker']}: {turn['function']} ({turn['trigger_reason']})"
        for turn in dialogue_plan.get("turn_order", [])
    )
    return f"""SYSTEM:
{SYSTEM_INSTRUCTION}

User topic: {topic}
Output language: {output_language}
Humor intensity: {humor_intensity}/5
Compassion: {compassion_level}/5
Scene mood: {dialogue_plan.get('council_mood')}
Analysis: themes={analysis.get('themes')}; emotions={analysis.get('emotions')}; needs={analysis.get('needs')}

Active speakers:
{profiles}

Dialogue plan:
{turns}

Write a short scripted dialogue. Each line must be a playful interpretation, not a real quote.
Use concise lines. End with "The Gavel Falls."
"""

