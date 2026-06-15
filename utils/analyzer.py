"""Deterministic topic, emotion, and need analysis for the Council Engine."""

from __future__ import annotations

from collections import Counter

from .safety import detect_crisis


THEME_KEYWORDS: dict[str, list[str]] = {
    "procrastination": ["procrastinate", "delay", "put off", "stuck", "avoid", "later", "deadline"],
    "perfectionism": ["perfect", "not good enough", "flawless", "mistake", "standards", "polish"],
    "burnout": ["burnout", "exhausted", "tired", "drained", "overworked", "no energy"],
    "conflict": ["conflict", "fight", "argument", "tension", "disagree", "angry at"],
    "career": ["career", "job", "work", "promotion", "interview", "boss", "colleague", "老板", "工作", "同事"],
    "money": ["money", "budget", "debt", "salary", "rent", "investment", "financial"],
    "creativity": ["creative", "write", "art", "idea", "blocked", "project"],
    "meaning": ["meaning", "purpose", "why", "empty", "direction", "life"],
    "health": ["health", "sleep", "pain", "doctor", "medical", "exercise"],
    "relationships": ["relationship", "partner", "friend", "family", "lonely", "date"],
    "academic anxiety": ["paper", "thesis", "exam", "reviewer", "submit", "research", "professor"],
    "leadership": ["lead", "team", "manager", "strategy", "responsibility"],
    "decision-making": ["decide", "choice", "options", "whether", "uncertain", "decision"],
    "grief": ["grief", "loss", "died", "mourning", "miss them"],
    "uncertainty": ["uncertain", "unknown", "worry", "future", "ambiguous"],
    "productivity": ["productive", "tasks", "todo", "focus", "planning", "schedule", "待办", "任务", "清单", "计划", "日程", "专注"],
    "confidence": ["confidence", "believe in myself", "self-esteem", "courage"],
    "fear of judgment": ["judge", "judged", "embarrass", "shame", "criticized", "rejected"],
}

EMOTION_KEYWORDS: dict[str, list[str]] = {
    "anxiety": ["anxious", "anxiety", "worried", "panic", "nervous", "afraid"],
    "sadness": ["sad", "down", "cry", "depressed", "heartbroken"],
    "anger": ["angry", "furious", "resent", "mad", "rage"],
    "overwhelm": ["overwhelmed", "too much", "can't handle", "swamped", "buried", "太多", "不知所措", "受不了"],
    "self-doubt": ["doubt", "not good enough", "imposter", "inadequate", "fail"],
    "excitement": ["excited", "thrilled", "energized", "hopeful"],
    "confusion": ["confused", "unclear", "lost", "don't know", "unsure"],
    "guilt": ["guilty", "regret", "should have"],
    "shame": ["ashamed", "shame", "humiliated", "embarrassed"],
    "fear": ["fear", "scared", "terrified", "afraid"],
    "frustration": ["frustrated", "annoyed", "irritated", "fed up"],
    "loneliness": ["lonely", "alone", "isolated", "no one"],
}

NEED_KEYWORDS: dict[str, list[str]] = {
    "courage": ["afraid", "fear", "brave", "submit", "start"],
    "perspective": ["perspective", "overthinking", "spiral", "meaning", "worry"],
    "action": ["do", "next", "start", "submit", "finish", "move", "开始", "下一步", "做"],
    "comfort": ["comfort", "sad", "grief", "hard", "hurt"],
    "structure": ["plan", "steps", "schedule", "organize", "structure", "计划", "步骤", "安排", "整理"],
    "humor": ["funny", "laugh", "comic", "lighter", "humor"],
    "rest": ["burnout", "tired", "exhausted", "rest", "sleep"],
    "clarity": ["confused", "unclear", "decide", "choice", "clarity"],
    "patience": ["wait", "slow", "patience", "rushed"],
    "discipline": ["discipline", "habit", "routine", "focus"],
    "self-compassion": ["shame", "guilt", "critic", "not good enough", "kind"],
    "decision support": ["decide", "choice", "options", "whether"],
}


def _score_keywords(text: str, mapping: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    scores: Counter[str] = Counter()
    for label, keywords in mapping.items():
        for keyword in keywords:
            if keyword in lowered:
                scores[label] += 1
    return [label for label, _ in scores.most_common()]


def analyze_user_topic(text: str) -> dict:
    """Detect themes, emotions, and needs using transparent keyword scoring."""
    themes = _score_keywords(text, THEME_KEYWORDS)
    emotions = _score_keywords(text, EMOTION_KEYWORDS)
    needs = _score_keywords(text, NEED_KEYWORDS)

    if not themes:
        themes = ["uncertainty"]
    if not emotions:
        emotions = ["confusion"]
    if not needs:
        needs = ["clarity", "action"]

    summary_parts = (themes[:2] + emotions[:1])[:3]
    return {
        "themes": themes[:5],
        "emotions": emotions[:4],
        "needs": needs[:5],
        "summary": " + ".join(summary_parts),
        "risk_level": "crisis" if detect_crisis(text) else "normal",
    }
