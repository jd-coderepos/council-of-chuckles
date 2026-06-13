"""Optional ASR and TTS helpers with graceful failure."""

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


ASR_MODEL_ID = os.getenv("ASR_MODEL_ID", "CohereLabs/cohere-transcribe-03-2026")
TTS_MODEL_ID = os.getenv("TTS_MODEL_ID", "openbmb/VoxCPM2")
ENABLE_VOICE_INPUT = os.getenv("ENABLE_VOICE_INPUT", "true").lower() == "true"
ENABLE_TTS = os.getenv("ENABLE_TTS", "false").lower() == "true"


@lru_cache(maxsize=1)
def _load_asr_pipeline():
    from transformers import pipeline

    return pipeline("automatic-speech-recognition", model=ASR_MODEL_ID, trust_remote_code=True)


@spaces.GPU(duration=90)
def transcribe_audio(audio_path: str | None, spoken_language: str) -> tuple[str, str]:
    if not audio_path:
        return "", "No audio provided."
    if not ENABLE_VOICE_INPUT:
        return "", "Voice input is currently wandering in the woods. Please type your question instead."
    try:
        pipe = _load_asr_pipeline()
        result = pipe(audio_path, generate_kwargs={"language": spoken_language})
        return result.get("text", "").strip(), f"Voice mode: Cohere Transcribe ({ASR_MODEL_ID})"
    except Exception:
        return "", "Voice input is currently wandering in the woods. Please type your question instead."


def synthesize_speech(text: str, language: str) -> tuple[str | None, str]:
    if not ENABLE_TTS:
        return None, "TTS: VoxCPM2 disabled"
    return None, "The council's voice is resting by the campfire, but the written verdict is ready."
