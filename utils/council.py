"""Council Engine orchestration."""

from __future__ import annotations

from .analyzer import analyze_user_topic
from .fallback import advisor_card_text, campfire_lines, trigger_reasons, verdict_text
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
    "Campfire Council Mode": 260,
}

VERDICT_TOKENS = 160

def make_final_verdict(
    topic: str,
    analysis: dict,
    active_speakers: list[dict],
    output_language: str,
    include_verdict: bool,
    use_model: bool,
    status_bits: list[str],
    council_discussion: str = "",
) -> str:
    """Generate the final verdict from the actual council discussion."""
    if not include_verdict:
        return ""

    if use_model:
        prompt = build_verdict_prompt_or_template(
            topic=topic,
            analysis=analysis,
            active_speakers=active_speakers,
            output_language=output_language,
            council_discussion=council_discussion,
        )
        generated, model_status = generate_text(
            prompt,
            max_new_tokens=VERDICT_TOKENS,
            temperature=0.45,
            clean_mode="verdict",
        )
        status_bits.append(f"Verdict: {model_status}")

        if generated:
            generated = generated.strip()
            if "The Gavel Falls:" in generated:
                generated = generated[generated.find("The Gavel Falls:") :].strip()
            elif not generated.startswith("The Gavel Falls"):
                generated = "The Gavel Falls:\n" + generated
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
        text = (
            "The council refuses to bully its own quest-giver or anyone else. "
            "It can offer absurdist humor about procrastination, bureaucracy, awkward timing, "
            "or the situation instead."
        )
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
        if use_model:
            prompt = campfire_prompt(topic, output_language, humor_intensity, compassion_level, analysis, active_speakers, plan)
            generated, model_status = generate_text(prompt, MAX_TOKENS[mode])
            status_bits.append(model_status)
        if generated:
            output_html = render_verdict(disclaimer + ("\n\n" if disclaimer else "") + generated)
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
            output_language,
            include_verdict,
            use_model,
            status_bits,
            council_discussion=plain_output,
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
            if use_model:
                prompt = advisor_prompt(topic, output_language, mode, humor_intensity, compassion_level, analysis, advisor)
                generated, model_status = generate_text(prompt, MAX_TOKENS[mode])
                status_bits.append(model_status)
            body = generated or advisor_card_text(advisor, topic, analysis, mode, output_language)
            cards.append(render_advisor_response(advisor, body, reasons[advisor["id"]]))
            plain_parts.append(f"{advisor['name']}\n{body}")
        council_discussion = "\n\n".join(plain_parts)
        verdict = make_final_verdict(
            topic,
            analysis,
            active_speakers,
            output_language,
            include_verdict,
            use_model,
            status_bits,
            council_discussion=council_discussion,
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
    if use_model:
        prompt = council_prompt(topic, output_language, mode, humor_intensity, compassion_level, analysis, active_speakers)
        generated, model_status = generate_text(prompt, MAX_TOKENS["Council Mode"])
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
        output_language,
        include_verdict,
        use_model,
        status_bits,
        council_discussion=plain,
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
