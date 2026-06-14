"""Optional ASR and TTS helpers with graceful failure."""

from __future__ import annotations

import os
import traceback
from functools import lru_cache

from utils.languages import WHISPER_LANGUAGE_TO_CODE

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


ASR_MODEL_ID = os.getenv("ASR_MODEL_ID", "openai/whisper-tiny")
TTS_MODEL_ID = os.getenv("TTS_MODEL_ID", "openbmb/VoxCPM2")
ENABLE_VOICE_INPUT = os.getenv("ENABLE_VOICE_INPUT", "true").lower() == "true"
ENABLE_TTS = os.getenv("ENABLE_TTS", "false").lower() == "true"
ASR_FALLBACK_MESSAGE = (
    "Voice input is currently wandering in the woods. "
    "Please type your question instead."
)


@lru_cache(maxsize=1)
def _load_asr_pipeline():
    import torch
    from transformers import pipeline

    kwargs = {"model": ASR_MODEL_ID}
    if torch.cuda.is_available():
        kwargs["device"] = 0
        kwargs["torch_dtype"] = torch.float16

    return pipeline("automatic-speech-recognition", **kwargs)


def _prepare_audio(audio_path: str):
    import numpy as np
    from transformers.audio_utils import load_audio

    audio = np.asarray(load_audio(audio_path, sampling_rate=16000), dtype=np.float32)
    audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)

    if audio.ndim > 1:
        audio = audio.mean(axis=-1)

    if audio.size == 0:
        return None, "I could not find any audio in that recording. Please try again.", 0.0, 0.0

    duration_s = audio.size / 16000
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if duration_s < 0.25 or peak < 1e-5:
        return None, "I could not catch enough speech there. Please try a slightly longer recording.", duration_s, peak

    if peak > 1.0:
        audio = audio / peak

    return audio, "", duration_s, peak


def _decode_text(decoded) -> str:
    if isinstance(decoded, list):
        decoded = decoded[0] if decoded else ""
    if isinstance(decoded, dict):
        decoded = decoded.get("text", "")
    return (decoded or "").strip()


@spaces.GPU(duration=60)
def transcribe_audio(audio_path: str | None, spoken_language: str) -> tuple[str, str]:
    if not audio_path:
        return "", "No audio provided."

    if not ENABLE_VOICE_INPUT:
        return "", "Voice input is currently disabled. Please type your question instead."

    try:
        language_code = WHISPER_LANGUAGE_TO_CODE.get(spoken_language, "en")

        print(f"[ASR] audio_path={audio_path}")
        print(f"[ASR] model={ASR_MODEL_ID}")
        print(f"[ASR] spoken_language={spoken_language} -> language_code={language_code}")

        audio, audio_error, duration_s, peak = _prepare_audio(audio_path)
        if audio_error:
            return "", audio_error

        print(f"[ASR] duration_s={duration_s:.2f}, peak={peak:.4f}")

        result = _load_asr_pipeline()(
            {"array": audio, "sampling_rate": 16000},
            generate_kwargs={"language": language_code, "task": "transcribe"},
        )
        text = _decode_text(result)

        if not text:
            return "", (
                "ASR ran but returned an empty transcript. "
                "Try recording a slightly longer, louder clip."
            )

        return text, f"Voice mode: Whisper tiny ({ASR_MODEL_ID}, language={language_code})"

    except Exception:
        print("[ASR ERROR]")
        traceback.print_exc()
        return "", ASR_FALLBACK_MESSAGE


def synthesize_speech(text: str, language: str) -> tuple[str | None, str]:
    if not ENABLE_TTS:
        return None, "TTS: VoxCPM2 disabled"
    return None, "The council's voice is resting by the campfire, but the written verdict is ready."
