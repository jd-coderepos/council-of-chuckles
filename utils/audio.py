"""Optional ASR and TTS helpers with graceful failure."""

from __future__ import annotations

import os
import traceback
from functools import lru_cache

try:
    import spaces  # type: ignore[import-not-found]
except Exception:
    class _SpacesFallback:
        def GPU(self, *args, **kwargs):
            if args and callable(args[0]) and len(args) == 1 and not kwargs:
                return args[0]

            def decorator(fn):
                return fn

            return decorator

    spaces = _SpacesFallback()


ASR_MODEL_ID = os.getenv("ASR_MODEL_ID", "CohereLabs/cohere-transcribe-03-2026")
TTS_MODEL_ID = os.getenv("TTS_MODEL_ID", "openbmb/VoxCPM2")
ENABLE_VOICE_INPUT = os.getenv("ENABLE_VOICE_INPUT", "true").lower() == "true"
ENABLE_TTS = os.getenv("ENABLE_TTS", "false").lower() == "true"


LANGUAGE_TO_CODE = {
    "English": "en",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Spanish": "es",
    "Portuguese": "pt",
    "Greek": "el",
    "Dutch": "nl",
    "Polish": "pl",
    "Arabic": "ar",
    "Vietnamese": "vi",
    "Mandarin Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
}


@lru_cache(maxsize=1)
def _load_asr_model():
    import torch
    from transformers import AutoProcessor, CohereAsrForConditionalGeneration

    processor = AutoProcessor.from_pretrained(
        ASR_MODEL_ID,
        trust_remote_code=True,
    )

    model = CohereAsrForConditionalGeneration.from_pretrained(
        ASR_MODEL_ID,
        device_map="auto",
        torch_dtype="auto",
        trust_remote_code=True,
    )

    model.eval()
    return processor, model, torch


@spaces.GPU(duration=60)
def transcribe_audio(audio_path: str | None, spoken_language: str) -> tuple[str, str]:
    if not audio_path:
        return "", "No audio provided."

    if not ENABLE_VOICE_INPUT:
        return "", "Voice input is currently disabled. Please type your question instead."

    try:
        from transformers.audio_utils import load_audio

        language_code = LANGUAGE_TO_CODE.get(spoken_language, "en")

        print(f"[ASR] audio_path={audio_path}")
        print(f"[ASR] spoken_language={spoken_language} -> language_code={language_code}")

        processor, model, torch = _load_asr_model()

        audio = load_audio(audio_path, sampling_rate=16000)

        inputs = processor(
            audio,
            sampling_rate=16000,
            return_tensors="pt",
            language=language_code,
        )

        audio_chunk_index = inputs.get("audio_chunk_index")
        inputs.to(model.device, dtype=model.dtype)

        with torch.inference_mode():
            outputs = model.generate(**inputs, max_new_tokens=256)

        decoded = processor.decode(
            outputs,
            skip_special_tokens=True,
            audio_chunk_index=audio_chunk_index,
            language=language_code,
        )

        if isinstance(decoded, list):
            text = decoded[0] if decoded else ""
        else:
            text = decoded

        text = (text or "").strip()

        if not text:
            return "", (
                "ASR ran but returned an empty transcript. "
                "Try recording a slightly longer, louder clip."
            )

        return text, f"Voice mode: Cohere Transcribe ({ASR_MODEL_ID}, language={language_code})"

    except Exception as exc:
        print("[ASR ERROR]")
        traceback.print_exc()
        return "", f"ASR error: {type(exc).__name__}: {exc}"


def synthesize_speech(text: str, language: str) -> tuple[str | None, str]:
    if not ENABLE_TTS:
        return None, "TTS: VoxCPM2 disabled"
    return None, "The council's voice is resting by the campfire, but the written verdict is ready."