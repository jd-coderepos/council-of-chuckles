"""Language options for text and spoken input."""

TEXT_LANGUAGES = [
    "English",
    "German",
    "French",
    "Spanish",
    "Italian",
    "Portuguese",
    "Dutch",
    "Polish",
    "Greek",
    "Arabic",
    "Vietnamese",
    "Mandarin Chinese",
    "Japanese",
    "Korean",
]


WHISPER_LANGUAGE_TO_CODE = {
    "English": "en",
    "German": "de",
    "Hindi": "hi",
    "French": "fr",
    "Spanish": "es",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Polish": "pl",
    "Greek": "el",
    "Arabic": "ar",
    "Vietnamese": "vi",
    "Mandarin Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
}


VOICE_LANGUAGES = list(WHISPER_LANGUAGE_TO_CODE)


def resolve_output_language(choice: str, custom_language: str | None = None) -> str:
    """Return a concrete output language name."""
    custom = (custom_language or "").strip()
    if custom:
        return custom
    return choice or "English"
