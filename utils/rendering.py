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
    tags = "".join(f'<span class="tag">{_escape(tag)}</span>' for tag in advisor.get("best_for", [])[:2])
    return f"""
    <article class="advisor {'selected' if selected else ''}">
      <div class="advisor-head">
        {render_avatar(advisor)}
        <div>
          <strong>{_escape(advisor['name'])}</strong><br>
          <small>{_escape(advisor['category'])}</small>
        </div>
      </div>
      <div class="tags">{tags}</div>
    </article>
    """

def render_advisor_gallery(advisors: list[dict], selected_ids: list[str], max_cards: int = 8) -> str:
    if not advisors:
        return '<div class="empty">No council members selected yet.</div>'

    selected = set(selected_ids or [])
    shown = advisors[:max_cards]

    cards = "".join(
        render_advisor_card(advisor, advisor["id"] in selected)
        for advisor in shown
    )

    if len(advisors) > max_cards:
        note = (
            f'<div class="empty advisor-preview-note">'
            f'Showing {max_cards} of {len(advisors)} matching advisors. '
            f'Use search or category to narrow the list.'
            f'</div>'
        )
    else:
        note = ""

    return f'<div class="advisor-grid">{cards}</div>{note}'


def render_selected_council_chips(advisors: list[dict]) -> str:
    if not advisors:
        return '<div class="tray muted">No council members selected yet.</div>'
    chips = "".join(
        f'<span class="chip">{render_avatar(advisor)}<span>{_escape(advisor["name"])}</span></span>'
        for advisor in advisors
    )
    return f'<div class="tray">{chips}</div>'


def render_active_speaker_row(advisors: list[dict]) -> str:
    if not advisors:
        return '<div class="speakers muted">No active speakers yet.</div>'
    chips = "".join(
        f'<span class="chip">{render_avatar(advisor)}<span>{_escape(advisor["name"])}</span></span>'
        for advisor in advisors
    )
    return f'<section class="active-speakers"><h3>Active speakers</h3><div class="speakers">{chips}</div></section>'


def render_engine_panel(analysis: dict, active_speakers: list[dict], strategy: str, reasons: dict[str, str]) -> str:
    archetypes = sorted({a for advisor in active_speakers for a in advisor.get("archetypes", [])})
    themes = ", ".join(analysis.get("themes", [])[:3]) or "the question"
    emotions = ", ".join(analysis.get("emotions", [])[:2]) or "the mood"
    needs = ", ".join(analysis.get("needs", [])[:2]) or "a useful next step"
    voice_mix = ", ".join(archetypes[:3]) if archetypes else "balanced"
    names = ", ".join(advisor["name"] for advisor in active_speakers[:4])
    if len(active_speakers) > 4:
        names += f", and {len(active_speakers) - 4} more"

    summary = (
        f"Detected {themes}, {emotions}, and the need for {needs}. "
        f"{_escape(strategy)} selected {voice_mix} voices: {names}."
    )
    return f"""
    <section class="engine-panel">
      <h3>Council Engine</h3>
      <p>{_escape(summary)}</p>
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
    return f"""
    <article class="takeaway">
      <strong>Tiny Gavel</strong>
      <div class="response-body">{_format_text(text)}</div>
    </article>
    """


def _format_text(text: str) -> str:
    safe = _escape(text)
    safe = safe.replace("\n", "<br>")
    return safe
