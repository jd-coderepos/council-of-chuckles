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
- Write a comic synthesis, not a serious advice summary.
- Base the verdict on the council discussion, but do not copy any council line verbatim.
- Use concrete details from the user's question.
- Use the user's own funny words when safe, such as "bananas", "purple buttons", or "deadline".
- Make the problem feel smaller and more manageable.
- Do not continue the council dialogue.
- Do not write advisor names.
- Do not insult the user or real people.
- Do not use generic phrases like "workplace dynamics", "root cause", "prioritize self-care", or "not a verdict on your worth".
- Do not mention academic anxiety unless the user question is clearly academic.
- Keep each verdict item to one short, witty sentence.
- Output only the structure below.

Use this exact structure:
The Gavel Falls:
What the council agrees on: <funny practical synthesis>
What they disagree on: <playful contrast between approaches>
Hidden pattern: <comic reframe of the real issue>
Tiny next action: <one concrete action>
Ridiculous but useful reminder: <one absurd but kind image from the user's situation>
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

