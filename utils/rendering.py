"""HTML rendering helpers for the Gradio interface."""

from __future__ import annotations

import html
from pathlib import Path

from .advisors import ROOT, get_initials


CATEGORY_COLORS = [
    "#f6b44b",
    "#89c779",
    "#b98cff",
    "#67c8d7",
    "#f27f88",
    "#d5d46f",
    "#9ed0ff",
]


def _escape(value: object) -> str:
    return html.escape(str(value or ""))


def _category_color(category: str) -> str:
    return CATEGORY_COLORS[abs(hash(category)) % len(CATEGORY_COLORS)]


def avatar_path_exists(path: str) -> bool:
    if not path or path.startswith(("http://", "https://")):
        return False
    candidate = (ROOT / path).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return False
    return candidate.exists() and candidate.is_file()


def render_avatar(advisor: dict) -> str:
    color = _category_color(advisor.get("category", ""))
    path = advisor.get("avatar", "")
    if avatar_path_exists(path):
        src = "/file=" + str((ROOT / path).resolve()).replace("\\", "/")
        return f'<img class="avatar-img" src="{_escape(src)}" alt="{_escape(advisor.get("avatar_alt"))}">'
    initials = _escape(advisor.get("avatar_alt") or get_initials(advisor.get("name", "")))
    return f'<div class="avatar-fallback" style="--ring:{color}">{initials}</div>'


def render_advisor_card(advisor: dict, selected: bool) -> str:
    tags = "".join(f'<span class="tag">{_escape(tag)}</span>' for tag in advisor.get("best_for", [])[:3])
    archetype = " / ".join(advisor.get("archetypes", ["Sage"])[:2])
    selected_badge = '<span class="selected-badge">In your council</span>' if selected else ""
    checkmark = '<span class="checkmark">✓</span>' if selected else ""
    return f"""
    <div class="advisor-tile {'selected' if selected else ''}">
      {checkmark}
      <div class="tile-top">{render_avatar(advisor)}<div><h4>{_escape(advisor['name'])}</h4><p>{_escape(advisor['category'])}</p></div></div>
      <div class="archetype">{_escape(archetype)}</div>
      <div class="tags">{tags}</div>
      {selected_badge}
    </div>
    """


def render_advisor_gallery(advisors: list[dict], selected_ids: list[str]) -> str:
    if not advisors:
        return '<div class="empty">No advisors match this search.</div>'
    selected = set(selected_ids or [])
    cards = "".join(render_advisor_card(advisor, advisor["id"] in selected) for advisor in advisors)
    return f'<div class="advisor-gallery">{cards}</div>'


def render_selected_council_chips(advisors: list[dict]) -> str:
    if not advisors:
        return '<div class="chip-row muted">No council members selected yet.</div>'
    chips = "".join(
        f'<span class="avatar-chip">{render_avatar(advisor)}<span>{_escape(advisor["name"])}</span></span>'
        for advisor in advisors
    )
    return f'<div class="chip-row">{chips}</div>'


def render_active_speaker_row(advisors: list[dict]) -> str:
    if not advisors:
        return '<div class="active-row muted">No active speakers yet.</div>'
    chips = "".join(
        f'<span class="active-chip">{render_avatar(advisor)}<span>{_escape(advisor["name"])}</span></span>'
        for advisor in advisors
    )
    return f'<div class="active-row"><strong>Active Speakers</strong>{chips}</div>'


def render_engine_panel(analysis: dict, active_speakers: list[dict], strategy: str, reasons: dict[str, str]) -> str:
    themes = "".join(f'<span class="tag">{_escape(item)}</span>' for item in analysis.get("themes", []))
    emotions = "".join(f'<span class="tag">{_escape(item)}</span>' for item in analysis.get("emotions", []))
    needs = "".join(f'<span class="tag">{_escape(item)}</span>' for item in analysis.get("needs", []))
    archetypes = sorted({a for advisor in active_speakers for a in advisor.get("archetypes", [])})
    arch = "".join(f'<span class="tag warm">{_escape(item)}</span>' for item in archetypes)
    triggered = "".join(
        f'<span class="trigger-chip">{render_avatar(advisor)}<span>{_escape(advisor["name"])}<em>{_escape(reasons.get(advisor["id"], "matched"))}</em></span></span>'
        for advisor in active_speakers
    )
    return f"""
    <section class="engine-panel">
      <h3>Council Engine</h3>
      <p>The model writes the lines, but the Council Engine directs the scene: it detects the topic, activates matching advisors, balances archetypes, plans the turn order, and keeps the conversation useful.</p>
      <div class="engine-grid">
        <div><b>Detected themes</b><div>{themes}</div></div>
        <div><b>Detected emotions</b><div>{emotions}</div></div>
        <div><b>Detected needs</b><div>{needs}</div></div>
        <div><b>Active archetypes</b><div>{arch}</div></div>
      </div>
      <div class="engine-strategy"><b>Speaker selection strategy:</b> {_escape(strategy)}</div>
      <div class="triggered">{triggered}</div>
    </section>
    """


def render_advisor_response(advisor: dict, body: str, trigger: str) -> str:
    archetype = " / ".join(advisor.get("archetypes", ["Sage"])[:2])
    return f"""
    <article class="response-card">
      <header>{render_avatar(advisor)}<div><h3>{_escape(advisor['name'])}</h3><p>{_escape(advisor['category'])} · {_escape(archetype)}</p></div></header>
      <span class="disclaimer">Inspired by {_escape(advisor['name'])}; not a real quote.</span>
      <span class="trigger">Triggered by: {_escape(trigger)}</span>
      <div class="response-body">{_format_text(body)}</div>
    </article>
    """


def render_dialogue_turn(advisor: dict, line: str, turn_function: str, trigger: str) -> str:
    archetype = " / ".join(advisor.get("archetypes", ["Sage"])[:2])
    return f"""
    <div class="dialogue-turn">
      {render_avatar(advisor)}
      <div class="bubble">
        <b>{_escape(advisor['name'])}</b><span>{_escape(archetype)} · {_escape(turn_function)} · {_escape(trigger)}</span>
        <p>{_escape(line)}</p>
      </div>
    </div>
    """


def render_verdict(text: str) -> str:
    return f'<article class="verdict-card"><div class="response-body">{_format_text(text)}</div></article>'


def _format_text(text: str) -> str:
    safe = _escape(text)
    safe = safe.replace("\n", "<br>")
    return safe

