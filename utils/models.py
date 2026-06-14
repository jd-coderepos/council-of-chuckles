"""Lazy model loading and text generation wrappers."""

from __future__ import annotations

import os
from functools import lru_cache

try:
    import spaces
except Exception:
    class _SpacesFallback:
        def GPU(self, *args, **kwargs):
            if args and callable(args[0]) and len(args) == 1 and not kwargs:
                return args[0]

            def decorator(fn):
                return fn

            return decorator

    spaces = _SpacesFallback()


TEXT_MODEL_ID = os.getenv("TEXT_MODEL_ID", "CohereLabs/tiny-aya-water")
ENABLE_ENGLISH_FALLBACK_MODEL = os.getenv("ENABLE_ENGLISH_FALLBACK_MODEL", "false").lower() == "true"
ENGLISH_FALLBACK_MODEL_ID = os.getenv("ENGLISH_FALLBACK_MODEL_ID", "openbmb/MiniCPM5-1B")

def clean_generation(text: str, max_dialogue_lines: int = 8) -> str:
    """Trim small-model over-generation and recover advisor dialogue lines.

    Handles both:
    - Socrates: advice here
    - **Socrates:** 
      advice here
    """
    text = (text or "").strip()
    text = text.replace("```", "").strip()
    text = text.strip("-").strip()

    # Stop before any verdict or repeated ending.
    for marker in ["The Gavel Falls.", "The Gavel Falls:"]:
        if marker in text:
            text = text.partition(marker)[0].strip()

    banned_starts = [
        "The end.",
        "Let me know",
        "If you'd like",
        "If you would like",
        "Would you like",
        "The Gavel Falls",
    ]

    cleaned_lines = []
    pending_speaker = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Remove simple markdown emphasis/bullets.
        line = line.lstrip("-•0123456789. ").strip()
        line = line.replace("**", "").replace("__", "").strip()

        if not line:
            continue

        if any(line.startswith(prefix) for prefix in banned_starts):
            break

        if ":" in line:
            speaker, body = line.split(":", 1)
            speaker = speaker.strip()
            body = body.strip()

            # Ignore malformed labels.
            if not speaker or len(speaker) > 40:
                continue

            # Case: "Socrates:" with no body yet. Store speaker and use next line.
            if not body:
                pending_speaker = speaker
                continue

            cleaned_lines.append(f"{speaker}: {body}")
            pending_speaker = None

        elif pending_speaker:
            # Case: previous line was "Socrates:" and this line is the advice.
            cleaned_lines.append(f"{pending_speaker}: {line}")
            pending_speaker = None

        elif cleaned_lines:
            # Continuation of the previous advisor line.
            cleaned_lines[-1] = cleaned_lines[-1].rstrip() + " " + line

        if len(cleaned_lines) >= max_dialogue_lines:
            break

    # Remove any accidental empty speaker-only lines.
    cleaned_lines = [
        line for line in cleaned_lines
        if ":" in line and line.split(":", 1)[1].strip()
    ]

    if cleaned_lines:
        return "\n".join(cleaned_lines).strip()

    # If cleaning failed, return the raw text rather than empty advisor names.
    return text.strip()

def clean_verdict_generation(text: str) -> str:
    """Clean Tiny Aya verdict output without cutting lines mid-thought."""
    text = (text or "").strip()
    text = text.replace("```", "").strip()
    text = text.strip("-").strip()

    if "The Gavel Falls:" in text:
        text = text[text.find("The Gavel Falls:") :].strip()
    elif "The Gavel Falls" in text:
        text = text[text.find("The Gavel Falls") :].strip()
    else:
        text = "The Gavel Falls:\n" + text

    labels = [
        "What the council agrees on:",
        "What they disagree on:",
        "Hidden pattern:",
        "Tiny next action:",
        "Ridiculous but useful reminder:",
    ]

    def tidy_value(value: str, max_words: int = 26) -> str:
        value = " ".join(value.strip().split())
        if not value:
            return ""

        # Prefer a complete first sentence rather than cutting at an arbitrary word.
        sentence_ends = [".", "!", "?"]
        first_end_positions = [value.find(p) for p in sentence_ends if value.find(p) != -1]
        if first_end_positions:
            first_end = min(first_end_positions)
            first_sentence = value[: first_end + 1].strip()
            if len(first_sentence.split()) <= max_words:
                return first_sentence

        words = value.split()
        if len(words) <= max_words:
            return value if value[-1] in ".!?" else value + "."

        # Last resort: trim, but avoid leaving dangling words.
        trimmed = " ".join(words[:max_words]).rstrip(",;:")
        dangling = {"and", "or", "but", "because", "with", "without", "to", "of", "the", "a"}
        while trimmed.split() and trimmed.split()[-1].lower() in dangling:
            trimmed = " ".join(trimmed.split()[:-1])
        return trimmed + "."

    lines = ["The Gavel Falls:"]

    for label in labels:
        if label in text:
            after = text.split(label, 1)[1]
            next_positions = [
                after.find(next_label)
                for next_label in labels
                if next_label != label and after.find(next_label) != -1
            ]
            if next_positions:
                after = after[: min(next_positions)]

            value = tidy_value(after, max_words=24)
            if value:
                lines.append(f"{label} {value}")

    return "\n".join(lines).strip()

@lru_cache(maxsize=2)
def load_text_model(model_id: str = TEXT_MODEL_ID):
    """Load the text model lazily. Imports stay inside the function for Spaces reliability."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        torch_dtype=dtype,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    return tokenizer, model


@spaces.GPU(duration=60)
def generate_text(
    prompt: str,
    max_new_tokens: int = 280,
    temperature: float = 0.7,
    clean_mode: str = "dialogue",
) -> tuple[str, str]:
    """Generate text or return a fallback status on failure."""
    try:
        tokenizer, model = load_text_model(TEXT_MODEL_ID)
        inputs = tokenizer(prompt, return_tensors="pt")
        if getattr(model, "device", None):
            inputs = {key: value.to(model.device) for key, value in inputs.items()}
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=0.9,
            repetition_penalty=1.05,
            pad_token_id=tokenizer.eos_token_id,
        )
        decoded = tokenizer.decode(output[0], skip_special_tokens=True)
        text = decoded[len(prompt) :].strip() if decoded.startswith(prompt) else decoded.strip()
        if clean_mode == "dialogue":
            text = clean_generation(text)
        elif clean_mode == "verdict":
            text = clean_verdict_generation(text)
        else:
            text = text.strip()

        return text, f"Model mode: Tiny Aya ({TEXT_MODEL_ID})"

    except Exception as exc:
        if ENABLE_ENGLISH_FALLBACK_MODEL:
            try:
                tokenizer, model = load_text_model(ENGLISH_FALLBACK_MODEL_ID)
                inputs = tokenizer(prompt, return_tensors="pt")
                if getattr(model, "device", None):
                    inputs = {key: value.to(model.device) for key, value in inputs.items()}
                output = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=True, temperature=temperature)
                decoded = tokenizer.decode(output[0], skip_special_tokens=True)
                return clean_generation(decoded.strip()), f"Model mode: English fallback ({ENGLISH_FALLBACK_MODEL_ID})"
            except Exception:
                pass
        return "", f"Fallback mode active: {exc.__class__.__name__}"
