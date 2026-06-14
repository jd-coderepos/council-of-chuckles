"""Final verdict prompt and fallback builder."""

from __future__ import annotations

import hashlib
import re


STOPWORDS = {
    "about",
    "after",
    "again",
    "because",
    "before",
    "could",
    "does",
    "have",
    "having",
    "help",
    "into",
    "just",
    "like",
    "machen",
    "should",
    "that",
    "there",
    "this",
    "want",
    "wenn",
    "what",
    "when",
    "where",
    "with",
    "would",
}


def _pick(options: list[str], seed: str, offset: int = 0) -> str:
    digest = hashlib.sha256(seed.encode("utf-8", errors="ignore")).hexdigest()
    index = (int(digest[:8], 16) + offset) % len(options)
    return options[index]


def _topic_terms(topic: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9']+", topic.lower())
    return [word for word in words if len(word) > 2 and word not in STOPWORDS][:6]


def _topic_handle(topic: str, theme: str) -> str:
    terms = _topic_terms(topic)
    if not terms:
        return theme.replace("-", " ")

    if any(term in {"flour", "mehl"} for term in terms):
        return "the flour surplus"
    if any(term in {"paper", "thesis", "submit", "submission"} for term in terms):
        return "the paper submission"
    if any(term in {"hurt", "save", "people", "person"} for term in terms):
        return "the save-two-hurt-one knot"
    if any(term in {"job", "work", "boss", "career"} for term in terms):
        return "the work puzzle"
    if any(term in {"friend", "family", "partner", "relationship"} for term in terms):
        return "the relationship tangle"

    return " ".join(terms[:4])


def _action_line(topic: str, theme: str, need: str, handle: str, seed: str) -> str:
    lowered = topic.lower()
    if "mehl" in lowered or "flour" in lowered:
        return "Put the flour into three piles: bake now, store safely, give away."
    if "hurt" in lowered and ("save" in lowered or "people" in lowered):
        return "Write the least-harm option, the reversible option, and who must be consulted."
    if theme == "academic anxiety" or "submit" in lowered or "paper" in lowered:
        return "Do one final obvious-issues pass, then move the submit button into view."
    if theme == "money":
        return "Write the next number on paper before the budget becomes theater."
    if theme == "relationships":
        return "Send one plain sentence instead of a five-act emotional screenplay."
    if need in {"clarity", "decision support"}:
        return f"Name the next decision about {handle}, then choose the smallest reversible step."
    if need == "rest":
        return "Protect one real pause before the tired brain starts making policy."
    if need == "courage":
        return "Do the brave thing at postage-stamp size before making it ceremonial."
    return f"Make one visible move on {handle} before trying to solve the whole saga."


def _disagreement_line(active_speakers: list[dict], seed: str) -> str:
    names = [advisor.get("name", "one advisor") for advisor in active_speakers[:3]]
    if len(names) >= 3:
        templates = [
            f"{names[0]} would simplify; {names[1]} would test the duty; {names[2]} would ask for a prototype.",
            f"{names[0]} wants less grasping; {names[1]} wants cleaner judgment; {names[2]} wants a bolder experiment.",
            f"{names[0]} would lower the temperature; {names[1]} would sharpen the principle; {names[2]} would redesign the dashboard.",
        ]
    elif len(names) == 2:
        templates = [
            f"{names[0]} would soften the grip; {names[1]} would tighten the reasoning.",
            f"{names[0]} wants patience; {names[1]} wants a cleaner next move.",
        ]
    else:
        templates = ["The council disagrees mainly about whether to whisper, label, or sprint."]
    return _pick(templates, seed, 1)


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
    emotions = analysis.get("emotions", ["confusion"])
    need = needs[0] if needs else "clarity"
    theme = themes[0] if themes else "uncertainty"
    emotion = emotions[0] if emotions else "confusion"
    handle = _topic_handle(topic, theme)
    seed = "|".join([topic, theme, need, ",".join(advisor.get("name", "") for advisor in active_speakers)])
    agreement = _pick(
        [
            f"{handle.title()} needs {need}, not a courtroom with snacks.",
            f"{handle.title()} is real, but it is asking for {need}, not a royal decree.",
            f"The useful move is to make {handle} smaller, kinder, and less fog-machine-shaped.",
            f"The council sees {emotion}; the answer is one concrete step, not a dramatic weather report.",
        ],
        seed,
    )
    hidden = _pick(
        [
            f"{theme.title()} is trying to wear the manager badge, while {need} is doing the actual work.",
            f"The noisy part is {emotion}; the useful part is the next ordinary handle you can grab.",
            f"The question is pretending to be huge, but it has a small door marked {need}.",
            f"You are not solving all of {handle}; you are choosing the next honest move.",
        ],
        seed,
        2,
    )
    reminder = _pick(
        [
            f"{handle.title()} does not get to rent the entire control room.",
            "A tiny honest step is still a step, even without ceremonial lighting.",
            "No one has appointed this problem chairperson of the whole afternoon.",
            "You may answer the situation without becoming its unpaid stage manager.",
        ],
        seed,
        3,
    )
    return (
        "The Gavel Falls:\n"
        f"What the council agrees on: {agreement}\n"
        f"What they disagree on: {_disagreement_line(active_speakers, seed)}\n"
        f"Hidden pattern: {hidden}\n"
        f"Tiny next action: {_action_line(topic, theme, need, handle, seed)}\n"
        f"Ridiculous but useful reminder: {reminder}"
    )
