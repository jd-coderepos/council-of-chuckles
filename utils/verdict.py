"""Final verdict prompt and fallback builder."""

from __future__ import annotations


def build_verdict_prompt_or_template(
    topic: str,
    analysis: dict,
    active_speakers: list[dict],
    output_language: str,
    council_discussion: str = "",
    include_comic: bool = True,
) -> str:
    speaker_names = ", ".join(advisor["name"] for advisor in active_speakers)

    return f"""Write a compact final verdict in {output_language} based on the user's question and the council discussion.

User question:
{topic}

Council discussion:
{council_discussion}

Detected themes: {', '.join(analysis.get('themes', []))}
Detected emotions: {', '.join(analysis.get('emotions', []))}
Detected needs: {', '.join(analysis.get('needs', []))}
Advisors: {speaker_names}

Rules:
- Base the verdict on the actual council discussion above.
- Use concrete details from the user's question.
- Do not use generic therapy language.
- Do not say "not a verdict on your worth".
- Do not mention academic anxiety unless the user question is clearly academic.
- Keep the full verdict under 90 words.
- Make it practical, witty, and specific.
- Do not repeat the council dialogue.

Use this exact structure:
The Gavel Falls:
What the council agrees on:
What they disagree on:
Hidden pattern:
Tiny next action:
Ridiculous but useful reminder:
"""


def fallback_verdict(topic: str, analysis: dict, active_speakers: list[dict], output_language: str) -> str:
    needs = analysis.get("needs", ["clarity"])
    themes = analysis.get("themes", ["uncertainty"])
    return (
        "The Gavel Falls:\n"
        f"What the council agrees on: This is mainly about {themes[0]}, not a verdict on your worth.\n"
        "What they disagree on: Whether the cure begins with stillness, structure, or a briskly supervised first step.\n"
        f"Hidden pattern: {needs[0].title()} is asking to become practical, not perfect.\n"
        "Tiny next action: Set a ten-minute timer and do the smallest visible piece.\n"
        "Ridiculous but useful reminder: Confidence may arrive late; do not give it the only key."
    )

