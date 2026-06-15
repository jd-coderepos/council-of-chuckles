"""Council Engine orchestration."""

from __future__ import annotations

from .analyzer import analyze_user_topic
from .fallback import advisor_card_text, campfire_lines, trigger_reasons, verdict_text
from .languages import localized_copy
from .matching import select_active_speakers
from .prompts import advisor_prompt, campfire_prompt, council_prompt
from .models import generate_text
from .verdict import build_verdict_prompt_or_template
from .rendering import (
    render_active_speaker_row,
    render_advisor_response,
    render_dialogue_turn,
    render_engine_panel,
    render_verdict,
)
from .safety import (
    detect_crisis,
    detect_harmful_humor_request,
    detect_professional_advice,
    professional_disclaimer,
    safe_support_response,
)


MAX_TOKENS = {
    "Mastermind Mode": 160,
    "Comic Relief Mode": 160,
    "Council Mode": 280,
    "Campfire Council Mode": 360,
}

VERDICT_TOKENS = 280


def _render_generated_dialogue(
    generated: str,
    active_speakers: list[dict],
    reasons: dict[str, str],
) -> str:
    advisor_by_name = {advisor["name"].casefold(): advisor for advisor in active_speakers}
    cards = []

    for raw_line in generated.splitlines():
        line = raw_line.strip().replace("：", ":")
        if not line or ":" not in line:
            continue

        speaker_name, body = line.split(":", 1)
        speaker_name = speaker_name.strip().strip("*")
        body = body.strip()
        if not speaker_name or not body:
            continue

        advisor = advisor_by_name.get(speaker_name.casefold())
        if not advisor:
            advisor = next(
                (
                    candidate
                    for name, candidate in advisor_by_name.items()
                    if speaker_name.casefold() in name or name in speaker_name.casefold()
                ),
                None,
            )
        if not advisor:
            continue

        cards.append(render_dialogue_turn(advisor, body, "respond", reasons.get(advisor["id"], "matched")))

    return "".join(cards)


def _generate_text_or_fallback(*args, **kwargs) -> tuple[str, str]:
    """Call the ZeroGPU text model without letting quota errors reach Gradio."""
    try:
        return generate_text(*args, **kwargs)
    except Exception as exc:
        message = str(exc).lower()
        if "zerogpu" in message or "quota" in message:
            return "", "Fallback mode active: ZeroGPU quota unavailable"
        return "", f"Fallback mode active: {exc.__class__.__name__}"


def make_final_verdict(
    topic: str,
    analysis: dict,
    active_speakers: list[dict],
    input_language: str,
    output_language: str,
    include_verdict: bool,
    use_model: bool,
    status_bits: list[str],
    council_discussion: str = "",
    humor_intensity: int = 3,
    compassion_level: int = 3,
) -> str:
    """Generate the final verdict from the actual council discussion."""
    if not include_verdict:
        return ""

    if use_model:
        prompt = build_verdict_prompt_or_template(
            topic=topic,
            analysis=analysis,
            active_speakers=active_speakers,
            input_language=input_language,
            output_language=output_language,
            council_discussion=council_discussion,
            humor_intensity=humor_intensity,
            compassion_level=compassion_level,
        )
        generated, model_status = _generate_text_or_fallback(
            prompt,
            max_new_tokens=VERDICT_TOKENS,
            temperature=0.5,
            clean_mode="verdict",
        )
        status_bits.append(f"Verdict: {model_status}")

        if generated:
            generated = generated.strip()
            verdict_header = localized_copy(output_language)["verdict_header"]
            if output_language == "English" and "The Gavel Falls:" in generated:
                generated = generated[generated.find("The Gavel Falls:") :].strip()
            elif not generated.startswith(verdict_header):
                generated = verdict_header + "\n" + generated
            return generated

    return verdict_text(topic, analysis, active_speakers, output_language)

def run_council(
    topic: str,
    selected_advisors: list[dict],
    output_language: str,
    mode: str,
    strategy: str,
    active_count: int,
    manual_ids: list[str] | None,
    mood: str,
    turns: int,
    humor_intensity: int,
    compassion_level: int,
    include_verdict: bool,
    demo_friendly: bool,
    use_model: bool = True,
    input_language: str = "English",
) -> dict:
    topic = (topic or "").strip()
    if not topic:
        return {
            "engine_html": "",
            "active_html": "",
            "output_html": '<div class="empty">Ask the council a question first.</div>',
            "verdict_html": "",
            "status": "Waiting for a question.",
            "plain_output": "",
            "analysis": {},
            "active_speakers": [],
        }

    if detect_crisis(topic):
        support = safe_support_response(output_language)
        return {
            "engine_html": "",
            "active_html": "",
            "output_html": render_verdict(support),
            "verdict_html": "",
            "status": "Crisis safety route active. Humor and personas paused.",
            "plain_output": support,
            "analysis": {"risk_level": "crisis"},
            "active_speakers": [],
        }

    if detect_harmful_humor_request(topic):
        text = localized_copy(output_language)["harmful_refusal"]
        return {
            "engine_html": "",
            "active_html": "",
            "output_html": render_verdict(text),
            "verdict_html": "",
            "status": "Harmful humor request transformed.",
            "plain_output": text,
            "analysis": {},
            "active_speakers": [],
        }

    analysis = analyze_user_topic(topic)
    count = min(int(active_count or 5), 5 if demo_friendly else 7)
    turns = min(int(turns or 6), 6 if demo_friendly else 12)
    active_speakers = select_active_speakers(selected_advisors, analysis, count, strategy, manual_ids)
    reasons = trigger_reasons(active_speakers, analysis)
    engine_html = render_engine_panel(analysis, active_speakers, strategy, reasons)
    active_html = render_active_speaker_row(active_speakers)
    status_bits = []
    model_calls_used = 0
    max_model_calls = 1 if use_model else 0
    disclaimer = professional_disclaimer(output_language) if detect_professional_advice(topic) else ""

    if not active_speakers:
        return {
            "engine_html": engine_html,
            "active_html": active_html,
            "output_html": '<div class="empty">Select at least one advisor for your council.</div>',
            "verdict_html": "",
            "status": "No selected advisors.",
            "plain_output": "",
            "analysis": analysis,
            "active_speakers": [],
        }

    if mode == "Campfire Council Mode":
        plan, fallback_turns = campfire_lines(active_speakers, topic, analysis, turns, mood, output_language)
        generated = ""
        if model_calls_used < max_model_calls:
            prompt = campfire_prompt(topic, input_language, output_language, humor_intensity, compassion_level, analysis, active_speakers, plan)
            dialogue_temperature = min(0.9, 0.65 + 0.05 * int(humor_intensity or 0))
            model_calls_used += 1
            generated, model_status = _generate_text_or_fallback(
                prompt,
                MAX_TOKENS[mode],
                temperature=dialogue_temperature,
                clean_mode="dialogue",
            )
            status_bits.append(model_status)
        if generated:
            rendered_dialogue = _render_generated_dialogue(generated, active_speakers, reasons)
            output_html = (render_verdict(disclaimer) if disclaimer else "") + (
                rendered_dialogue or render_verdict(generated)
            )
            plain_output = generated
        else:
            output_html = "".join(
                render_dialogue_turn(advisor, line, function, trigger)
                for advisor, line, function, trigger in fallback_turns
            )
            plain_output = "\n".join(f"{advisor['name']}: {line}" for advisor, line, _, _ in fallback_turns)
            if not status_bits:
                status_bits.append("Fallback mode active")
        verdict = make_final_verdict(
            topic,
            analysis,
            active_speakers,
            input_language,
            output_language,
            include_verdict,
            use_model and model_calls_used < max_model_calls,
            status_bits,
            council_discussion=plain_output,
            humor_intensity=humor_intensity,
            compassion_level=compassion_level,
        )
        return {
            "engine_html": engine_html,
            "active_html": active_html,
            "output_html": output_html,
            "verdict_html": render_verdict(verdict) if verdict else "",
            "status": " | ".join(status_bits),
            "plain_output": (disclaimer + "\n\n" if disclaimer else "") + plain_output + ("\n\n" + verdict if verdict else ""),
            "analysis": analysis,
            "active_speakers": active_speakers,
        }

    if mode in {"Mastermind Mode", "Comic Relief Mode"}:
        cards = []
        plain_parts = []
        for advisor in active_speakers:
            generated = ""
            if model_calls_used < max_model_calls:
                prompt = advisor_prompt(topic, input_language, output_language, mode, humor_intensity, compassion_level, analysis, advisor)
                model_calls_used += 1
                generated, model_status = _generate_text_or_fallback(prompt, MAX_TOKENS[mode])
                status_bits.append(model_status)
            body = generated or advisor_card_text(advisor, topic, analysis, mode, output_language)
            cards.append(render_advisor_response(advisor, body, reasons[advisor["id"]]))
            plain_parts.append(f"{advisor['name']}\n{body}")
        council_discussion = "\n\n".join(plain_parts)
        verdict = make_final_verdict(
            topic,
            analysis,
            active_speakers,
            input_language,
            output_language,
            include_verdict,
            use_model and model_calls_used < max_model_calls,
            status_bits,
            council_discussion=council_discussion,
            humor_intensity=humor_intensity,
            compassion_level=compassion_level,
        )
        return {
            "engine_html": engine_html,
            "active_html": active_html,
            "output_html": (render_verdict(disclaimer) if disclaimer else "") + "".join(cards),
            "verdict_html": render_verdict(verdict) if verdict else "",
            "status": " | ".join(dict.fromkeys(status_bits)) or "Fallback mode active",
            "plain_output": (disclaimer + "\n\n" if disclaimer else "") + "\n\n".join(plain_parts) + ("\n\n" + verdict if verdict else ""),
            "analysis": analysis,
            "active_speakers": active_speakers,
        }

    generated = ""
    if model_calls_used < max_model_calls:
        prompt = council_prompt(topic, input_language, output_language, mode, humor_intensity, compassion_level, analysis, active_speakers)
        model_calls_used += 1
        generated, model_status = _generate_text_or_fallback(prompt, MAX_TOKENS["Council Mode"])
        status_bits.append(model_status)
    if generated:
        output_html = render_verdict((disclaimer + "\n\n" if disclaimer else "") + generated)
        plain = generated
    else:
        cards = [
            render_advisor_response(advisor, advisor_card_text(advisor, topic, analysis, mode, output_language), reasons[advisor["id"]])
            for advisor in active_speakers
        ]
        output_html = (render_verdict(disclaimer) if disclaimer else "") + "".join(cards)
        plain = "\n\n".join(
            f"{advisor['name']}\n{advisor_card_text(advisor, topic, analysis, mode, output_language)}"
            for advisor in active_speakers
        )
        status_bits.append("Fallback mode active")
    verdict = make_final_verdict(
        topic,
        analysis,
        active_speakers,
        input_language,
        output_language,
        include_verdict,
        use_model and model_calls_used < max_model_calls,
        status_bits,
        council_discussion=plain,
        humor_intensity=humor_intensity,
        compassion_level=compassion_level,
    )
    return {
        "engine_html": engine_html,
        "active_html": active_html,
        "output_html": output_html,
        "verdict_html": render_verdict(verdict) if verdict else "",
        "status": " | ".join(dict.fromkeys(status_bits)),
        "plain_output": (disclaimer + "\n\n" if disclaimer else "") + plain + ("\n\n" + verdict if verdict else ""),
        "analysis": analysis,
        "active_speakers": active_speakers,
    }
