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
    """Trim small-model over-generation, repeated endings, and runaway dialogue."""
    text = (text or "").strip()

    # Remove markdown fences or separators that small models often add.
    text = text.replace("```", "").strip()
    text = text.strip("-").strip()

    marker = "The Gavel Falls."
    if marker in text:
        before, _, _after = text.partition(marker)
        text = before.strip()

    banned_starts = [
        "The end.",
        "Let me know",
        "If you'd like",
        "If you would like",
        "Would you like",
        "The Gavel Falls",
    ]

    cleaned_lines = []
    dialogue_lines = 0

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if any(stripped.startswith(prefix) for prefix in banned_starts):
            break

        # Keep advisor-like lines only, e.g. "Socrates: ..."
        if ":" in stripped:
            cleaned_lines.append(stripped)
            dialogue_lines += 1

        if dialogue_lines >= max_dialogue_lines:
            break

    if cleaned_lines:
        return "\n".join(cleaned_lines).strip()

    return text.strip()

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


@spaces.GPU(duration=120)
def generate_text(prompt: str, max_new_tokens: int = 280, temperature: float = 0.7) -> tuple[str, str]:
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
        return clean_generation(text), f"Model mode: Tiny Aya ({TEXT_MODEL_ID})"
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
