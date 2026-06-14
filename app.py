from __future__ import annotations

import random

import gradio as gr

from utils.banner import HERO_HTML
from utils.advisors import advisor_by_id, category_options, filter_advisors, load_advisors
from utils.audio import transcribe_audio
from utils.council import run_council
from utils.languages import TEXT_LANGUAGES, VOICE_LANGUAGES, resolve_output_language
from utils.rendering import render_advisor_gallery
from utils.session import append_session_entry, export_session_markdown


ADVISORS = load_advisors()
DEFAULT_SELECTED_IDS = [advisor["id"] for advisor in ADVISORS[:5]]


def _choices(advisors: list[dict]) -> list[tuple[str, str]]:
    return [(f"{advisor['name']} - {advisor['category']}", advisor["id"]) for advisor in advisors]


def _selected_advisors(selected_ids: list[str] | None) -> list[dict]:
    ids = selected_ids or []
    return [advisor for advisor in (advisor_by_id(ADVISORS, advisor_id) for advisor_id in ids) if advisor]

def _category_pool(category: str) -> list[dict]:
    return filter_advisors(ADVISORS, "", category)


def _available_advisors(selected_ids: list[str] | None, category: str) -> list[dict]:
    selected = set(selected_ids or [])
    return [advisor for advisor in _category_pool(category) if advisor["id"] not in selected]


def refresh_panel2(selected_ids: list[str] | None, category: str):
    selected_ids = selected_ids or []
    selected = _selected_advisors(selected_ids)
    available = _available_advisors(selected_ids, category)
    return (
        selected_ids,
        gr.update(choices=_choices(available), value=None),
        render_advisor_gallery(selected, selected_ids),
        f"{len(selected_ids)} selected council member(s)",
        gr.update(choices=_choices(selected), value=None),
    )

def refresh_category(category: str, selected_ids: list[str] | None):
    return refresh_panel2(selected_ids, category)


def add_advisor_to_council(advisor_id: str | None, selected_ids: list[str] | None, category: str):
    selected_ids = list(selected_ids or [])
    if advisor_id and advisor_id not in selected_ids:
        selected_ids.append(advisor_id)
    return refresh_panel2(selected_ids, category)


def remove_advisor_from_council(advisor_id: str | None, selected_ids: list[str] | None, category: str):
    selected_ids = [item for item in (selected_ids or []) if item != advisor_id]
    return refresh_panel2(selected_ids, category)


def clear_selection(category: str):
    return refresh_panel2([], category)


def surprise_selection(category: str):
    pool = _category_pool(category) or ADVISORS
    shuffled = pool[:]
    random.shuffle(shuffled)
    picked = shuffled[: min(5, len(shuffled))]
    ids = [advisor["id"] for advisor in picked]
    return refresh_panel2(ids, category)

def use_transcript(transcript: str):
    return transcript or ""

def toggle_input_mode(input_mode: str):
    is_voice = input_mode == "Voice"

    if is_voice:
        input_language_update = gr.update(
            visible=True,
            choices=VOICE_LANGUAGES,
            value="English",
            label="Spoken input language",
        )
    else:
        input_language_update = gr.update(
            visible=True,
            choices=TEXT_LANGUAGES,
            value="English",
            label="Typed question language",
        )

    return (
        input_language_update,              # input language selector
        gr.update(visible=is_voice),        # audio
        gr.update(visible=is_voice),        # transcribe button
        gr.update(visible=is_voice),        # use transcript button
        gr.update(visible=is_voice),        # transcript textbox
        gr.update(visible=is_voice, value=""),  # voice status
    )

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
  --cream: #fff8ee;
  --paper: #ffffff;
  --ink: #101010;
  --muted: #695f56;
  --line: #ecd5b1;
  --orange: #ff7a18;
  --gold: #ffb000;
  --ember: #ff4f1f;
  --plum: #251235;
  --violet: #efe6ff;
  --green: #ddf8d0;
  --blue: #e0f2ff;
  --shadow: 0 18px 46px rgba(67, 38, 15, .14);
}

* { box-sizing: border-box; }

.gradio-container {
  color: var(--ink) !important;
  background:
    linear-gradient(135deg, rgba(255, 176, 0, .08) 25%, transparent 25%) 0 0 / 42px 42px,
    linear-gradient(225deg, rgba(255, 176, 0, .08) 25%, transparent 25%) 0 0 / 42px 42px,
    var(--cream) !important;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

.gradio-container .main-wrap {
  width: min(1240px, calc(100% - 32px));
  max-width: none;
  margin: 0 auto;
}

/* Hide Gradio's default surrounding panels so the custom panels carry the design. */
.gradio-container .panel,
.gradio-container .voice-card,
.gradio-container .stage {
  overflow: visible;
}

.gradio-container .hero {
  position: relative !important;
  min-height: 460px !important;
  overflow: hidden !important;
  padding: 34px 0 26px !important;
}
.gradio-container .hero::before {
  content: "";
  position: absolute;
  right: -70px;
  top: 76px;
  width: min(58vw, 760px);
  height: 390px;
  border-radius: 44% 56% 42% 58% / 58% 42% 58% 42%;
  background: linear-gradient(135deg, var(--gold) 0%, var(--orange) 44%, var(--ember) 100%);
  transform: rotate(-7deg);
}
.gradio-container .hero-grid {
  position: relative !important;
  z-index: 1 !important;
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) 520px !important;
  gap: 28px !important;
  align-items: center !important;
}
.gradio-container .hero .brand {
  display: inline-flex !important;
  align-items: center !important;
  gap: 10px !important;
  padding: 8px 12px !important;
  border: 2px solid var(--ink) !important;
  border-radius: 999px !important;
  background: rgba(255, 255, 255, .88) !important;
  color: var(--ink) !important;
  font-size: .9rem !important;
  font-weight: 900 !important;
  box-shadow: 4px 4px 0 var(--gold) !important;
}
.brand-mark {
  width: 24px;
  height: 24px;
  border-radius: 7px;
  background: var(--orange);
  position: relative;
  transform: rotate(45deg);
}
.brand-mark::before,
.brand-mark::after {
  content: "";
  position: absolute;
  inset: 5px;
  border: 2px solid #fff6df;
  border-radius: 5px;
}
.brand-mark::after { inset: 9px; }
.gradio-container .hero h1 {
  margin: 26px 0 14px !important;
  max-width: 760px !important;
  font-size: clamp(4rem, 8.1vw, 7.45rem) !important;
  line-height: .82 !important;
  letter-spacing: 0 !important;
  color: var(--ink) !important;
  font-weight: 700 !important;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
  text-wrap: balance;
}

.gradio-container .hero .subtitle {
  max-width: 650px !important;
  margin: 0 !important;
  color: var(--muted) !important;
  font-size: 1.18rem !important;
  line-height: 1.5 !important;
  font-weight: 720 !important;
}
.badges,
.actions,
.tray,
.chips,
.speakers,
.tags,
.triggered {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.badges { margin-top: 24px; }
.badge,
.pill,
.chip,
.tag,
.archetype,
.selected-badge,
.trigger,
.disclaimer,
.trigger-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255, 255, 255, .88);
  color: var(--muted);
  padding: 8px 12px;
  font-size: .86rem;
  font-weight: 850;
}
.gradio-container .hero .badge {
  color: var(--muted) !important;
  font-weight: 850 !important;
}
.tag {
  background: var(--violet);
  color: #442053;
  padding: 5px 8px;
  font-size: .74rem;
}
.tag.warm { background: #fff1d0; color: #684016; }
.disclaimer,
.trigger { margin: 8px 6px 0 0; }
.trigger-chip {
  background: rgba(255,247,234,.9);
  color: var(--ink);
}
.trigger-chip em {
  display: block;
  color: var(--muted);
  font-size: .72rem;
  font-style: normal;
}

/* SVG thinker sticker banner. */
.gradio-container .hero-art {
  width: 520px !important;
  min-height: 396px !important;
  position: relative !important;
  isolation: isolate !important;
  overflow: visible !important;
}

.gradio-container .hero-art::before {
  content: "";
  position: absolute;
  right: 0;
  top: 6px;
  width: 100%;
  height: 366px;
  border-radius: 48% 52% 46% 54% / 54% 46% 54% 46%;
  background:
    radial-gradient(circle at 28% 28%, rgba(255,255,255,.12), transparent 0 23%),
    radial-gradient(circle at 78% 72%, rgba(255,255,255,.13), transparent 0 18%),
    linear-gradient(135deg, rgba(255,176,0,.34), rgba(255,79,31,.08));
  z-index: -1;
}
.thinker-sticker {
  position: absolute;
  width: 102px;
  text-align: center;
  transform: rotate(var(--tilt, 0deg));
  filter: drop-shadow(0 18px 20px rgba(61, 26, 0, .23));
  z-index: 2;
}
.thinker-sticker svg {
  display: block;
  width: 100%;
  height: auto;
  overflow: visible;
  position: relative;
  z-index: 2;
}
.thinker-label {
  display: inline-block;
  position: relative;
  z-index: 3;
  margin-top: -10px;
  padding: 5px 10px 6px;
  border: 2px solid #111;
  border-radius: 999px;
  background: #fff7ea;
  color: #111;
  box-shadow: 4px 4px 0 rgba(255, 176, 0, .92);
  font-size: .72rem;
  line-height: 1;
  font-weight: 950;
  white-space: nowrap;
}
.thinker-sticker.feature { width: 136px; left: 300px; top: 146px; --tilt: 2deg; }
.thinker-sticker.socrates { width: 100px; left: 170px; top: 28px; --tilt: 6deg; }
.thinker-sticker.aristotle { width: 92px; left: 296px; top: 18px; --tilt: 8deg; }
.thinker-sticker.confucius { width: 102px; left: 92px; top: 176px; --tilt: -6deg; }
.thinker-sticker.rumi { width: 98px; left: 214px; top: 246px; --tilt: -5deg; }
.thinker-sticker.jung { width: 100px; left: 400px; top: 228px; --tilt: 4deg; }
.thinker-sticker.feature .thinker-label {
  font-size: .82rem;
  margin-top: -14px;
  padding: 7px 12px 8px;
}
.spark {
  position: absolute;
  width: 20px;
  height: 20px;
  background: var(--gold);
  border-radius: 55% 45% 50% 50%;
  transform: rotate(28deg);
  right: 18px;
  top: 26px;
  box-shadow:
    -32px 38px 0 rgba(255, 247, 234, .85),
    -68px 12px 0 rgba(255, 176, 0, .75),
    -104px 62px 0 rgba(255, 247, 234, .7);
}

/* Main app structure. */
.app-shell {
  display: grid !important;
  grid-template-columns: minmax(340px, .9fr) minmax(0, 1.4fr) !important;
  gap: 18px !important;
  padding: 8px 0 48px;
  align-items: start !important;
}
.app-shell > * { min-width: 0; }
.panel {
  border: 1px solid var(--line) !important;
  border-radius: 8px !important;
  background: rgba(255, 255, 255, .94) !important;
  box-shadow: var(--shadow) !important;
  padding: 18px !important;
  color: var(--ink) !important;
}
.panel + .panel { margin-top: 16px; }
.voice-card {
  border: 1px solid var(--line) !important;
  background: rgba(255, 255, 255, .94) !important;
}
.stage {
  position: sticky !important;
  top: 14px;
  background:
    radial-gradient(circle at 94% 10%, rgba(255, 176, 0, .2), transparent 10rem),
    linear-gradient(150deg, #2b163b, #1b1024) !important;
  color: #fff7ea !important;
  border-color: rgba(37, 18, 53, .7) !important;
  max-height: calc(100vh - 28px);
  overflow: auto !important;
}
.stage .badge,
.stage .chip {
  background: rgba(255,255,255,.12);
  color: #fff7ea;
  border-color: rgba(255,247,234,.26);
}
.stage .muted { color: #f0d9bd; }
.stage .avatar-fallback,
.stage .avatar-img { color: var(--ink); }
.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.panel-title h2,
.panel h3,
.stage h3 {
  margin: 0;
  letter-spacing: 0;
}
.panel-title h2 { font-size: 1.32rem; }
.stage h3 { color: #fff7ea; }
.number {
  color: var(--orange);
  font-weight: 950;
  margin-right: 7px;
}

/* Make Gradio radio buttons visibly selected. */
.gradio-container input[type="radio"] {
  -webkit-appearance: none !important;
  appearance: none !important;
  width: 17px !important;
  height: 17px !important;
  min-width: 17px !important;
  border: 1.8px solid #e6b56e !important;
  border-radius: 999px !important;
  background: #fffdf8 !important;
  box-shadow: none !important;
  vertical-align: middle !important;
}

.gradio-container input[type="radio"]:checked {
  border-color: var(--orange) !important;
  background:
    radial-gradient(circle at center, var(--orange) 0 42%, #fffdf8 45% 100%) !important;
}

.gradio-container input[type="radio"]:focus-visible {
  outline: 3px solid rgba(255, 122, 24, .18) !important;
  outline-offset: 2px !important;
}

.gradio-container .scene-radio label:has(input[type="radio"]:checked) {
  border-color: var(--orange) !important;
  background: #fff1d0 !important;
}

.voice-status {
  min-height: 0 !important;
  margin: 4px 0 8px !important;
  color: var(--muted) !important;
  font-size: .82rem !important;
}

.voice-status p {
  margin: 0 !important;
}

/* Gradio form controls. */
.gradio-container label,
.gradio-container .block-label,
.gradio-container .wrap label {
  color: var(--muted) !important;
  font-size: .82rem !important;
  font-weight: 850 !important;
}
.gradio-container input,
.gradio-container select,
.gradio-container textarea {
  border: 1px solid var(--line) !important;
  border-radius: 8px !important;
  background: #fffdf8 !important;
  color: var(--ink) !important;
}
.gradio-container input:focus,
.gradio-container select:focus,
.gradio-container textarea:focus {
  border-color: var(--orange) !important;
  box-shadow: 0 0 0 3px rgba(255, 122, 24, .18) !important;
}
.gradio-container button {
  border: 1px solid var(--line) !important;
  border-radius: 8px !important;
  background: #fffdf8 !important;
  color: var(--ink) !important;
  font-weight: 900 !important;
  box-shadow: 0 3px 0 rgba(236, 213, 177, .7) !important;
}
.gradio-container button.primary {
  border-color: #e46913 !important;
  background: linear-gradient(135deg, var(--gold), var(--orange), var(--ember)) !important;
  color: var(--ink) !important;
  box-shadow: 0 9px 18px rgba(255, 122, 24, .28) !important;
  min-width: 220px;
}
.stage button {
  background: rgba(255,255,255,.92) !important;
}

/* Advisor cards and selected council tray. */
.tray {
  border: 1px dashed #e3bd7e;
  background: #fff7e6;
  padding: 12px;
  border-radius: 8px;
  margin: 12px 0;
}
.advisor-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 12px;
}
.advisor-preview-note {
  margin-top: 10px;
  font-size: .82rem;
}
.advisor-preview-block {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
}
.advisor-preview-block > div {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
}
.advisor {
  min-height: 126px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fffefb;
  padding: 12px;
  position: relative;
}
.advisor.selected {
  background: linear-gradient(180deg, #fffefa, #fff1d0);
  border-color: var(--orange);
}
.advisor.selected::after {
  content: "In council";
  position: absolute;
  right: 10px;
  top: 10px;
  border-radius: 999px;
  background: var(--ink);
  color: #fff;
  padding: 4px 8px;
  font-size: .68rem;
  font-weight: 900;
}
.advisor-head {
  display: flex;
  gap: 10px;
  align-items: center;
  padding-right: 72px;
}
.advisor small,
.muted { color: var(--muted); font-weight: 750; }
.avatar-fallback,
.avatar-img {
  display: inline-grid;
  place-items: center;
  width: 30px;
  height: 30px;
  min-width: 30px;
  border: 2px solid #9d6616;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffe66a, #ffc21a);
  color: var(--ink);
  font-size: .76rem;
  font-weight: 950;
  object-fit: cover;
}
.chip .avatar-fallback,
.chip .avatar-img,
.trigger-chip .avatar-fallback,
.trigger-chip .avatar-img {
  width: 28px;
  height: 28px;
  min-width: 28px;
}

/* Stage output. Keep compatibility with old renderer class names. */
.engine-panel,
.response-card,
.verdict-card,
.dialogue-turn .bubble {
  border-radius: 8px;
  padding: 13px;
  margin: 12px 0;
}
.engine-panel {
  border: 1px solid rgba(255,247,234,.22);
  background: rgba(255,255,255,.1);
}
.engine-panel h3,
.response-card h3 {
  margin: 0 0 6px;
  color: #fff7ea;
}
.engine-panel p {
  color: #f0d9bd;
  margin: .3rem 0 .8rem;
}
.engine-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: .8rem;
  margin-bottom: .8rem;
}
.engine-strategy { color: #fff7ea; margin-bottom: .55rem; }
.response-card {
  background: #fff7ea;
  color: var(--ink);
  border: 1px solid #ffd89b;
}
.response-card header {
  display: flex;
  gap: .7rem;
  align-items: center;
}
.response-card h3 { color: var(--ink); }
.response-card p,
.response-card .response-body {
  color: var(--ink);
}
.response-body {
  line-height: 1.55;
}
.dialogue-turn {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: start;
  margin-top: 12px;
}
.dialogue-turn .bubble {
  background: #fff7ea;
  color: var(--ink);
  border: 1px solid #ffd89b;
}
.dialogue-turn .bubble span {
  display: block;
  color: var(--muted);
  font-size: .8rem;
  margin-top: .1rem;
}
.dialogue-turn .bubble p {
  margin: 6px 0 0;
  line-height: 1.45;
}
.takeaway,
.verdict-card {
  background: linear-gradient(135deg, #fff7ea, #ffe6ad);
  color: var(--ink);
  border: 1px solid var(--gold);
  border-radius: 8px;
  padding: 14px;
  margin-top: 14px;
}
.empty {
  color: var(--muted);
  padding: .7rem;
}
footer.engine-panel {
  margin: 0 0 40px;
  background: rgba(255, 255, 255, .85);
  color: var(--muted);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
}
footer.engine-panel p { color: var(--muted); }

@media (max-width: 1040px) {
  .hero { min-height: auto; }
  .hero::before { opacity: .42; right: -260px; top: 150px; }
  .hero-grid,
  .app-shell {
    grid-template-columns: 1fr !important;
  }
  .hero-art {
  width: 100% !important;
  min-height: 318px !important;
  }
  .hero-art::before { right: 0; top: 8px; width: 100%; height: 300px; }

  .thinker-sticker.feature { width: 122px; left: 62%; top: 116px; }
  .thinker-sticker.socrates { width: 88px; left: 33%; top: 24px; }
  .thinker-sticker.aristotle { width: 82px; left: 55%; top: 18px; }
  .thinker-sticker.confucius { width: 90px; left: 10%; top: 148px; }
  .thinker-sticker.rumi { width: 86px; left: 39%; top: 210px; }
  .thinker-sticker.jung { width: 88px; left: 74%; top: 198px; }
  .stage { position: static !important; max-height: none; }
}

@media (max-width: 620px) {
  .gradio-container .main-wrap { width: min(100% - 20px, 1240px); }
  .hero h1 { font-size: 3.45rem; }
  .hero-art { display: none; }
  .advisor-grid { grid-template-columns: 1fr; }
  .panel-title { align-items: flex-start; flex-direction: column; }
  .gradio-container button,
  .gradio-container button.primary { width: 100%; min-width: 0; }
}
"""


with gr.Blocks(title="Council of Chuckles") as demo:
    selected_state = gr.State(DEFAULT_SELECTED_IDS)
    session_state = gr.State([])

    with gr.Column(elem_classes=["main-wrap"]):
        gr.HTML(HERO_HTML)

        with gr.Row(elem_classes=["app-shell"]):
            with gr.Column(scale=5, min_width=340):
                with gr.Group(elem_classes=["panel", "voice-card"]):
                    gr.HTML(
                        """
                        <div class="panel-title">
                        <h2><span class="number">01</span>Ask by voice</h2>
                        <span class="badge">Text is still available</span>
                        </div>
                        """
                    )

                    with gr.Row():
                        input_mode = gr.Radio(
                            ["Voice", "Text"],
                            value="Voice",
                            label="Input mode",
                            interactive=True,
                        )
                        spoken_language = gr.Dropdown(VOICE_LANGUAGES, value="English", label="Spoken input language")
                        output_language = gr.Dropdown(TEXT_LANGUAGES, value="English", label="Council reply language")

                    custom_language = gr.Textbox(
                        label="Custom output language",
                        placeholder="Optional, e.g. Brazilian Portuguese",
                    )

                    audio = gr.Audio(
                        label="Record or upload your question",
                        sources=["microphone", "upload"],
                        type="filepath",
                        visible=True,
                    )

                    with gr.Row():
                        transcribe_btn = gr.Button("Transcribe", visible=True)
                        use_transcript_btn = gr.Button("Use transcript as question", visible=True)

                    transcript = gr.Textbox(label="Editable transcript", lines=4, visible=True)

                    voice_status = gr.Markdown("", elem_classes=["voice-status"], visible=True)

                    question = gr.Textbox(
                        label="Your question",
                        lines=5,
                        placeholder="What would you like the council to help with?",
                    )

                with gr.Group(elem_classes=["panel"]):
                    gr.HTML(
                        """
                        <div class="panel-title">
                        <h2><span class="number">02</span>Build your council</h2>
                        <span class="badge">Select your advisors</span>
                        </div>
                        """
                    )

                    with gr.Row():
                        advisor_search = gr.Dropdown(
                            label="Search and add advisor",
                            choices=_choices(_available_advisors(DEFAULT_SELECTED_IDS, "All")),
                            value=None,
                            interactive=True,
                            info="Start typing a name, then click a result to add it to the council.",
                        )
                        category = gr.Dropdown(category_options(ADVISORS), value="All", label="Category filter")

                    with gr.Row(elem_classes=["actions"]):
                        surprise_btn = gr.Button("Surprise Me")
                        clear_btn = gr.Button("Clear")

                    selected_count = gr.Markdown(f"{len(DEFAULT_SELECTED_IDS)} selected council member(s)")

                    gallery = gr.HTML(
                        render_advisor_gallery(_selected_advisors(DEFAULT_SELECTED_IDS), DEFAULT_SELECTED_IDS),
                        elem_classes=["advisor-preview-block"],
                    )

                    with gr.Row():
                        remove_advisor = gr.Dropdown(
                            label="Remove advisor",
                            choices=_choices(_selected_advisors(DEFAULT_SELECTED_IDS)),
                            value=None,
                            interactive=True,
                            info="Choose one selected advisor to remove.",
                        )
                        remove_btn = gr.Button("Remove", elem_classes=["remove-advisor-btn"])

                with gr.Group(elem_classes=["panel"]):
                    gr.HTML(
                        """
                        <div class="panel-title">
                        <h2><span class="number">03</span>Choose the scene</h2>
                        <span class="badge">Mode and mood</span>
                        </div>
                        """
                    )

                    mode = gr.Radio(
                        ["Mastermind Mode", "Comic Relief Mode", "Council Mode", "Campfire Council Mode"],
                        value="Campfire Council Mode",
                        label="Response mode",
                        elem_classes=["scene-radio"],
                    )

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

                        active_count = gr.Dropdown(
                            [1, 2, 3, 4, 5],
                            value=3,
                            label="Maximum voices in this response",
                            info="If fewer advisors are selected, all selected advisors can speak.",
                        )

                    strategy = gr.Dropdown(
                        choices=[
                            ("Best match to the question", "Match to my topic"),
                            ("Random from my council", "Surprise me"),
                        ],
                        value="Match to my topic",
                        label="Speaker picker",
                        info="Used when your council has more advisors than the maximum voices above.",
                    )

                    with gr.Row():
                        humor = gr.Slider(0, 5, value=3, step=1, label="Humor intensity")
                        compassion = gr.Slider(0, 5, value=3, step=1, label="Compassion level")

                    # Internal defaults kept hidden so the generation callback still receives
                    # the values it expects.
                    manual_active = gr.State([])
                    turns = gr.State(6)
                    include_verdict = gr.State(True)
                    demo_friendly = gr.State(True)
                    use_model = gr.State(True)

                    with gr.Row(elem_classes=["actions"]):
                        generate_btn = gr.Button("Generate Council", variant="primary")

            with gr.Column(scale=7, min_width=520):
                with gr.Group(elem_classes=["panel", "stage"]):
                    gr.HTML(
                        """
                        <div class="panel-title">
                        <h2><span class="number">04</span>Council Stage</h2>
                        <span class="badge">Live output</span>
                        </div>
                        """
                    )

                    status = gr.Markdown("Model mode: template fallback ready")
                    engine_panel = gr.HTML()
                    active_row = gr.HTML()
                    output = gr.HTML()
                    verdict = gr.HTML()

                    with gr.Row(elem_classes=["actions"]):
                        export_btn = gr.Button("Export Session")
                        export_file = gr.File(label="Session export")

                    export_status = gr.Markdown()        

        gr.HTML(
            """
            <footer class="engine-panel">
              <p>This app generates original responses inspired by public personas and ideas. It does not produce real quotes.</p>
              <p>Humor is for perspective, not dismissal. No conversations are permanently stored by this app. Text mode supports 70+ languages; voice input supports 15 curated Whisper languages. The model writes the lines; the Council Engine directs the scene.</p>
              <p>Default text-only stack: Tiny Aya Water 3.35B. Voice-input stack: 3.594B. Optional full voice-in/voice-out stack: 5.594B. All configurations are below the 32B cap; the ASR model is under 3B.</p>
            </footer>
            """
        )

    panel2_outputs = [selected_state, advisor_search, gallery, selected_count, remove_advisor]

    advisor_search.change(
        add_advisor_to_council,
        [advisor_search, selected_state, category],
        panel2_outputs,
    )

    category.change(
        refresh_category,
        [category, selected_state],
        panel2_outputs,
    )

    remove_btn.click(
        remove_advisor_from_council,
        [remove_advisor, selected_state, category],
        panel2_outputs,
    )

    clear_btn.click(
        clear_selection,
        [category],
        panel2_outputs,
    )

    surprise_btn.click(
        surprise_selection,
        [category],
        panel2_outputs,
    )

    input_mode.change(
        toggle_input_mode,
        [input_mode],
        [spoken_language, audio, transcribe_btn, use_transcript_btn, transcript, voice_status],
    )

    transcribe_btn.click(transcribe, [audio, spoken_language], [transcript, voice_status])
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
    demo.launch(css=CSS)
