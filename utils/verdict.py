"""Final verdict prompt and fallback builder."""

from __future__ import annotations


def build_verdict_prompt_or_template(
    topic: str,
    analysis: dict,
    active_speakers: list[dict],
    output_language: str,
    council_discussion: str = "",
    humor_intensity: int = 3,
    compassion_level: int = 3,
    include_comic: bool = True,
) -> str:
    speaker_names = ", ".join(advisor["name"] for advisor in active_speakers)
    humor_intensity = int(humor_intensity or 0)
    compassion_level = int(compassion_level or 3)

    if humor_intensity <= 1:
        humor_note = (
            "Use subtle wit: dry humor, gentle irony, and one small comic image. "
            "It should still feel funny, not solemn."
        )
    elif humor_intensity <= 3:
        humor_note = (
            "Use playful humor: witty phrasing, light absurdity, and a memorable image from the user's words."
        )
    else:
        humor_note = (
            "Use high comic energy: harmless exaggeration, mock-epic framing, and one laugh-out-loud but kind image."
        )

    compassion_note = (
        "The joke must make the problem feel smaller, not make the user or other people feel small."
        if compassion_level >= 3
        else "Keep the humor non-cruel and situation-focused."
    )

    return f"""Write a comic final lens in {output_language}, based on the user's question and the council discussion.

User question:
{topic}

Council discussion:
{council_discussion}

Detected themes: {', '.join(analysis.get('themes', []))}
Detected emotions: {', '.join(analysis.get('emotions', []))}
Detected needs: {', '.join(analysis.get('needs', []))}
Advisors: {speaker_names}

Comedy setting:
{humor_note}
{compassion_note}

Rules:
- This is not a serious advice summary; it is a playful closing lens.
- Base it on the council discussion, but do not copy any council line verbatim.
- Use concrete words from the user's question when safe.
- Keep every line short, vivid, and slightly funny.
- Do not write advisor names.
- Do not continue the council dialogue.
- Do not insult the user or real people.
- Do not use therapist/coach phrases such as "you're not alone", "root cause", "workplace dynamics", "productive tasks", "prioritize self-care", "channel that energy", or "not a verdict on your worth".
- Do not sound solemn, motivational-speaker-like, or generic.
- The tiny next action should be concrete, but phrased lightly.
- The final reminder must be the funniest line.
- Output only the structure below.

Use this exact structure:
The Gavel Falls:
What the council agrees on: <playful shared conclusion>
What they disagree on: <funny contrast between approaches>
Hidden pattern: <comic reframe of the real issue>
Tiny next action: <one small action with light wit>
Ridiculous but useful reminder: <the funniest kind image from the user's situation>
"""


def fallback_verdict(topic: str, analysis: dict, active_speakers: list[dict], output_language: str) -> str:
    needs = analysis.get("needs", ["clarity"])
    themes = analysis.get("themes", ["uncertainty"])
    return (
        "The Gavel Falls:\n"
        f"What the council agrees on: The situation is wearing a {themes[0]} costume, but it is still smaller than your whole day.\n"
        "What they disagree on: Some would flow around the chaos; others would label it, file it, and give it a tiny hat.\n"
        f"Hidden pattern: {needs[0].title()} is knocking politely while the drama bangs pots in the hallway.\n"
        "Tiny next action: Do one small visible thing before the problem hires a marching band.\n"
        "Ridiculous but useful reminder: You are not required to become the emotional mayor of every passing circus."
    )

