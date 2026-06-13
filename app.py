from __future__ import annotations

import random

import gradio as gr

from utils.advisors import advisor_by_id, category_options, filter_advisors, load_advisors
from utils.audio import transcribe_audio
from utils.council import run_council
from utils.languages import TEXT_LANGUAGES, VOICE_LANGUAGES, resolve_output_language
from utils.matching import select_active_speakers
from utils.rendering import render_advisor_gallery, render_selected_council_chips
from utils.session import append_session_entry, export_session_markdown
from utils.analyzer import analyze_user_topic


ADVISORS = load_advisors()
DEFAULT_SELECTED_IDS = [advisor["id"] for advisor in ADVISORS[:5]]


def _choices(advisors: list[dict]) -> list[tuple[str, str]]:
    return [(f"{advisor['name']} - {advisor['category']}", advisor["id"]) for advisor in advisors]


def _selected_advisors(selected_ids: list[str] | None) -> list[dict]:
    ids = selected_ids or []
    return [advisor for advisor in (advisor_by_id(ADVISORS, advisor_id) for advisor_id in ids) if advisor]


def _visible(search: str, category: str) -> list[dict]:
    return filter_advisors(ADVISORS, search, category)


def refresh_filtered_controls(search: str, category: str, selected_ids: list[str] | None):
    visible = _visible(search, category)
    selected_ids = selected_ids or []
    visible_ids = {advisor["id"] for advisor in visible}
    visible_selected = [advisor_id for advisor_id in selected_ids if advisor_id in visible_ids]
    gallery = render_advisor_gallery(visible, selected_ids)
    selected = _selected_advisors(selected_ids)
    return (
        gr.update(choices=_choices(visible), value=visible_selected),
        gallery,
        f"{len(selected_ids)} selected council member(s)",
        render_selected_council_chips(selected),
    )


def update_selected_from_visible(visible_values: list[str], selected_ids: list[str] | None, search: str, category: str):
    visible_values = visible_values or []
    selected_set = set(selected_ids or [])
    visible_ids = {advisor["id"] for advisor in _visible(search, category)}
    selected_set -= visible_ids
    selected_set |= set(visible_values)
    ordered = [advisor["id"] for advisor in ADVISORS if advisor["id"] in selected_set]
    selected = _selected_advisors(ordered)
    return (
        ordered,
        render_advisor_gallery(_visible(search, category), ordered),
        f"{len(ordered)} selected council member(s)",
        render_selected_council_chips(selected),
        gr.update(choices=_choices(selected), value=[]),
    )


def select_all_visible(search: str, category: str, selected_ids: list[str] | None):
    visible_ids = [advisor["id"] for advisor in _visible(search, category)]
    selected_set = set(selected_ids or [])
    selected_set.update(visible_ids)
    ordered = [advisor["id"] for advisor in ADVISORS if advisor["id"] in selected_set]
    return refresh_after_selection(ordered, search, category)


def clear_selection(search: str, category: str):
    return refresh_after_selection([], search, category)


def surprise_selection(search: str, category: str):
    pool = _visible(search, category) or ADVISORS
    shuffled = pool[:]
    random.shuffle(shuffled)
    picked = shuffled[: min(5, len(shuffled))]
    ids = [advisor["id"] for advisor in picked]
    return refresh_after_selection(ids, search, category)


def balanced_selection(search: str, category: str):
    pool = _visible(search, category) or ADVISORS
    analysis = {"themes": ["uncertainty"], "emotions": ["confusion"], "needs": ["clarity", "action"]}
    picked = select_active_speakers(pool, analysis, min(5, len(pool)), "Balanced Council")
    ids = [advisor["id"] for advisor in picked]
    return refresh_after_selection(ids, search, category)


def refresh_after_selection(selected_ids: list[str], search: str, category: str):
    visible = _visible(search, category)
    visible_set = {advisor["id"] for advisor in visible}
    visible_value = [advisor_id for advisor_id in selected_ids if advisor_id in visible_set]
    selected = _selected_advisors(selected_ids)
    return (
        selected_ids,
        gr.update(choices=_choices(visible), value=visible_value),
        render_advisor_gallery(visible, selected_ids),
        f"{len(selected_ids)} selected council member(s)",
        render_selected_council_chips(selected),
        gr.update(choices=_choices(selected), value=[]),
    )


def shuffle_active_speakers(selected_ids: list[str] | None, active_count: int, question: str):
    selected = _selected_advisors(selected_ids)
    if not selected:
        return gr.update(choices=[], value=[]), "Select council members first."
    analysis = analyze_user_topic(question or "uncertainty")
    picked = select_active_speakers(selected, analysis, active_count, "Surprise me")
    return gr.update(choices=_choices(selected), value=[advisor["id"] for advisor in picked]), "Active speakers shuffled."


def use_transcript(transcript: str):
    return transcript or ""


def transcribe(audio_path: str | None, spoken_language: str):
    text, status = transcribe_audio(audio_path, spoken_language)
    return text, status


def generate(
    question: str,
    selected_ids: list[str] | None,
    output_language_choice: str,
    custom_output_language: str,
    mode: str,
    strategy: str,
    active_count: int,
    manual_ids: list[str] | None,
    mood: str,
    turns: int,
    humor: int,
    compassion: int,
    include_verdict: bool,
    demo_friendly: bool,
    use_model: bool,
    session: list[dict] | None,
):
    output_language = resolve_output_language(output_language_choice, custom_output_language)
    selected = _selected_advisors(selected_ids)
    result = run_council(
        topic=question,
        selected_advisors=selected,
        output_language=output_language,
        mode=mode,
        strategy=strategy,
        active_count=active_count,
        manual_ids=manual_ids,
        mood=mood,
        turns=turns,
        humor_intensity=humor,
        compassion_level=compassion,
        include_verdict=include_verdict,
        demo_friendly=demo_friendly,
        use_model=use_model,
    )
    session = append_session_entry(
        session,
        {
            "topic": question,
            "mode": mode,
            "analysis_summary": result.get("analysis", {}).get("summary", ""),
            "plain_output": result.get("plain_output", ""),
        },
    )
    return (
        result["engine_html"],
        result["active_html"],
        result["output_html"],
        result["verdict_html"],
        result["status"],
        session,
    )


def export_session(session: list[dict] | None):
    path = export_session_markdown(session)
    return path, "Session exported." if path else "Nothing to export yet."


CSS = """
:root {
  --forest: #10180f;
  --moss: #7fab6c;
  --amber: #f0ae4b;
  --ember: #f06f45;
  --violet: #a78bfa;
  --paper: #fff8dd;
}
.gradio-container {
  background: radial-gradient(circle at 25% 10%, rgba(167,139,250,.22), transparent 28%),
              radial-gradient(circle at 80% 15%, rgba(240,174,75,.16), transparent 24%),
              linear-gradient(140deg, #0b120d 0%, #172111 45%, #241433 100%) !important;
  color: var(--paper);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.main-wrap { max-width: 1380px; margin: 0 auto; }
.hero {
  min-height: 230px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-bottom: 1px solid rgba(255,255,255,.12);
}
.hero h1 { font-size: clamp(2.4rem, 6vw, 5.4rem); margin: 0; line-height: 1; color: #fff5cf; }
.hero p { font-size: 1.1rem; max-width: 820px; color: #eadfb9; }
.badge-row, .tags, .chip-row, .active-row, .triggered { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; }
.badge, .tag, .archetype, .selected-badge, .trigger, .disclaimer {
  border: 1px solid rgba(255,255,255,.16);
  border-radius: 999px;
  padding: .22rem .55rem;
  background: rgba(255,255,255,.08);
  color: #fff4cf;
  font-size: .78rem;
}
.tag.warm { background: rgba(240,174,75,.18); }
.advisor-gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: .75rem; max-height: 610px; overflow: auto; padding-right: .25rem; }
.advisor-tile, .response-card, .engine-panel, .verdict-card, .dialogue-turn .bubble {
  background: rgba(18, 25, 18, .82);
  border: 1px solid rgba(255,255,255,.13);
  box-shadow: 0 12px 36px rgba(0,0,0,.28);
  border-radius: 8px;
}
.advisor-tile { position: relative; padding: .8rem; transition: transform .16s ease, border-color .16s ease; }
.advisor-tile:hover { transform: translateY(-2px); border-color: rgba(240,174,75,.55); }
.advisor-tile.selected { border-color: var(--amber); box-shadow: 0 0 0 1px rgba(240,174,75,.45), 0 12px 36px rgba(0,0,0,.28); }
.tile-top, .response-card header { display: flex; gap: .7rem; align-items: center; }
.tile-top h4, .response-card h3 { margin: 0; color: #fff6d6; font-size: 1rem; }
.tile-top p, .response-card p { margin: .12rem 0 0; color: #d8cfab; font-size: .83rem; }
.avatar-fallback, .avatar-img {
  width: 42px; height: 42px; min-width: 42px; border-radius: 50%;
  display: grid; place-items: center; font-weight: 800; color: #172111;
  background: linear-gradient(135deg, #fff2bd, var(--ring, #f0ae4b));
  border: 2px solid var(--ring, #f0ae4b);
}
.avatar-img { object-fit: cover; background: transparent; }
.checkmark { position: absolute; top: .55rem; right: .55rem; color: var(--amber); font-weight: 900; }
.selected-badge { display: inline-block; margin-top: .65rem; background: rgba(240,174,75,.18); }
.avatar-chip, .active-chip, .trigger-chip { display: inline-flex; align-items: center; gap: .4rem; padding: .28rem .55rem; border-radius: 999px; background: rgba(255,255,255,.09); border: 1px solid rgba(255,255,255,.13); }
.avatar-chip .avatar-fallback, .avatar-chip .avatar-img, .active-chip .avatar-fallback, .active-chip .avatar-img, .trigger-chip .avatar-fallback, .trigger-chip .avatar-img { width: 28px; height: 28px; min-width: 28px; font-size: .72rem; }
.trigger-chip em { display: block; color: #d8cfab; font-size: .72rem; font-style: normal; }
.engine-panel, .response-card, .verdict-card { padding: 1rem; margin: .8rem 0; }
.engine-panel h3 { margin: 0 0 .35rem; color: #ffe2a8; }
.engine-panel p { color: #ddd2ad; margin: .3rem 0 .8rem; }
.engine-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: .8rem; margin-bottom: .8rem; }
.active-row { padding: .75rem 0; }
.response-body { line-height: 1.55; color: #fff7d8; }
.dialogue-turn { display: flex; gap: .75rem; margin: .75rem 0; align-items: flex-start; }
.dialogue-turn .bubble { padding: .8rem 1rem; flex: 1; }
.dialogue-turn .bubble span { display: block; color: #d8cfab; font-size: .8rem; margin-top: .1rem; }
.verdict-card { border-color: rgba(240,174,75,.4); background: rgba(45, 28, 13, .78); }
.empty, .muted { color: #d8cfab; padding: .7rem; }
button.primary { background: linear-gradient(135deg, var(--amber), var(--ember)) !important; color: #1c1208 !important; font-weight: 800 !important; }
"""


with gr.Blocks(css=CSS, title="Council of Chuckles") as demo:
    selected_state = gr.State(DEFAULT_SELECTED_IDS)
    session_state = gr.State([])

    with gr.Column(elem_classes=["main-wrap"]):
        gr.HTML(
            """
            <section class="hero">
              <h1>Council of Chuckles</h1>
              <p>Assemble your Mastermind Alliance. Ask a serious question. Receive wisdom with a wink.</p>
              <div class="badge-row">
                <span class="badge">Thousand Token Wood</span>
                <span class="badge">Tiny Aya Water</span>
                <span class="badge">70+ text languages</span>
                <span class="badge">14 voice languages</span>
                <span class="badge">32B cap friendly</span>
                <span class="badge">Voice optional</span>
                <span class="badge">No paid APIs</span>
                <span class="badge">Council Engine</span>
              </div>
            </section>
            """
        )

        with gr.Row():
            with gr.Column(scale=1, min_width=320):
                gr.Markdown("### Mastermind Alliance")
                search = gr.Textbox(label="Advisor search", placeholder="Search names, roles, tags...")
                category = gr.Dropdown(category_options(ADVISORS), value="All", label="Category filter")
                selected_count = gr.Markdown(f"{len(DEFAULT_SELECTED_IDS)} selected council member(s)")
                selected_chips = gr.HTML(render_selected_council_chips(_selected_advisors(DEFAULT_SELECTED_IDS)))
                advisor_checks = gr.CheckboxGroup(
                    label="Visible advisors",
                    choices=_choices(ADVISORS),
                    value=DEFAULT_SELECTED_IDS,
                )
                with gr.Row():
                    surprise_btn = gr.Button("Surprise Me")
                    balanced_btn = gr.Button("Balanced Council")
                with gr.Row():
                    select_visible_btn = gr.Button("Select All Visible")
                    clear_btn = gr.Button("Clear Selection")
                gallery = gr.HTML(render_advisor_gallery(ADVISORS, DEFAULT_SELECTED_IDS))

            with gr.Column(scale=2, min_width=520):
                gr.Markdown("### Ask The Council")
                with gr.Row():
                    input_mode = gr.Radio(["Text", "Voice"], value="Text", label="Input mode")
                    spoken_language = gr.Dropdown(VOICE_LANGUAGES, value="English", label="Spoken input language")
                    output_language = gr.Dropdown(TEXT_LANGUAGES, value="English", label="Council reply language")
                custom_language = gr.Textbox(label="Custom output language", placeholder="Optional, e.g. Brazilian Portuguese")
                question = gr.Textbox(label="Your question", lines=5, placeholder="What would you like the council to help with?")
                with gr.Row():
                    audio = gr.Audio(label="Microphone or uploaded audio", sources=["microphone", "upload"], type="filepath")
                    transcript = gr.Textbox(label="Editable transcript", lines=4)
                with gr.Row():
                    transcribe_btn = gr.Button("Transcribe audio")
                    use_transcript_btn = gr.Button("Use transcript as question")

                with gr.Row():
                    mode = gr.Dropdown(
                        ["Mastermind Mode", "Comic Relief Mode", "Council Mode", "Campfire Council Mode"],
                        value="Campfire Council Mode",
                        label="Response mode",
                    )
                    strategy = gr.Dropdown(
                        ["Surprise me", "Match to my topic", "Manual selection", "Balanced Council"],
                        value="Balanced Council",
                        label="Speaker selection strategy",
                    )
                    active_count = gr.Slider(3, 7, value=5, step=1, label="Active speakers")
                gr.Markdown("You can build a large Mastermind Alliance, but each session invites a smaller circle of active speakers so the council stays lively, fast, and readable.")
                manual_active = gr.CheckboxGroup(label="Manual active speakers", choices=_choices(_selected_advisors(DEFAULT_SELECTED_IDS)), value=[])
                with gr.Row():
                    mood = gr.Dropdown(
                        [
                            "Gentle campfire",
                            "Philosophical tavern",
                            "Academic panic room",
                            "Woodland nonsense",
                            "Executive board meeting gone weird",
                            "Cosmic customer support desk",
                        ],
                        value="Gentle campfire",
                        label="Council mood",
                    )
                    turns = gr.Slider(4, 12, value=6, step=1, label="Dialogue turns")
                with gr.Row():
                    humor = gr.Slider(0, 5, value=3, step=1, label="Humor intensity")
                    compassion = gr.Slider(0, 5, value=5, step=1, label="Compassion level")
                with gr.Row():
                    include_verdict = gr.Checkbox(value=True, label="Include final verdict")
                    demo_friendly = gr.Checkbox(value=True, label="Demo-friendly mode")
                    use_model = gr.Checkbox(value=True, label="Use Tiny Aya model")
                with gr.Accordion("Advanced speech options", open=False):
                    speak_final = gr.Checkbox(value=False, label="Speak final verdict")
                    speak_cards = gr.Checkbox(value=False, label="Speak every advisor card")
                    speak_turns = gr.Checkbox(value=False, label="Speak Campfire Council turns")
                    gr.Markdown("TTS is optional and disabled by default for deployment reliability.")
                with gr.Row():
                    shuffle_btn = gr.Button("Shuffle Active Speakers")
                    generate_btn = gr.Button("Generate Council", variant="primary")

                status = gr.Markdown("Model mode: template fallback ready")
                engine_panel = gr.HTML()
                active_row = gr.HTML()
                output = gr.HTML()
                verdict = gr.HTML()
                with gr.Row():
                    export_btn = gr.Button("Export Session as Markdown")
                    export_file = gr.File(label="Session export")
                export_status = gr.Markdown()

        gr.HTML(
            """
            <footer class="engine-panel">
              <p>This app generates original responses inspired by public personas and ideas. It does not produce real quotes.</p>
              <p>Humor is for perspective, not dismissal. No conversations are permanently stored by this app. Text mode supports 70+ languages; voice input supports 14 spoken languages. The model writes the lines; the Council Engine directs the scene.</p>
              <p>Default text-only stack: Tiny Aya Water 3.35B. Voice-input stack: 5.35B. Optional full voice-in/voice-out stack: 7.35B. All configurations are below the 32B cap.</p>
            </footer>
            """
        )

    search.change(refresh_filtered_controls, [search, category, selected_state], [advisor_checks, gallery, selected_count, selected_chips])
    category.change(refresh_filtered_controls, [search, category, selected_state], [advisor_checks, gallery, selected_count, selected_chips])
    advisor_checks.change(
        update_selected_from_visible,
        [advisor_checks, selected_state, search, category],
        [selected_state, gallery, selected_count, selected_chips, manual_active],
    )
    select_visible_btn.click(
        select_all_visible,
        [search, category, selected_state],
        [selected_state, advisor_checks, gallery, selected_count, selected_chips, manual_active],
    )
    clear_btn.click(clear_selection, [search, category], [selected_state, advisor_checks, gallery, selected_count, selected_chips, manual_active])
    surprise_btn.click(surprise_selection, [search, category], [selected_state, advisor_checks, gallery, selected_count, selected_chips, manual_active])
    balanced_btn.click(balanced_selection, [search, category], [selected_state, advisor_checks, gallery, selected_count, selected_chips, manual_active])
    shuffle_btn.click(shuffle_active_speakers, [selected_state, active_count, question], [manual_active, status])
    transcribe_btn.click(transcribe, [audio, spoken_language], [transcript, status])
    use_transcript_btn.click(use_transcript, [transcript], [question])
    generate_btn.click(
        generate,
        [
            question,
            selected_state,
            output_language,
            custom_language,
            mode,
            strategy,
            active_count,
            manual_active,
            mood,
            turns,
            humor,
            compassion,
            include_verdict,
            demo_friendly,
            use_model,
            session_state,
        ],
        [engine_panel, active_row, output, verdict, status, session_state],
    )
    export_btn.click(export_session, [session_state], [export_file, export_status])


if __name__ == "__main__":
    demo.launch()
