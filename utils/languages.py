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

VOICE_LANGUAGES = [
    "English",
    "French",
    "German",
    "Italian",
    "Spanish",
    "Portuguese",
    "Greek",
    "Dutch",
    "Polish",
    "Arabic",
    "Vietnamese",
    "Mandarin Chinese",
    "Japanese",
    "Korean",
]


def resolve_output_language(choice: str, custom_language: str | None = None) -> str:
    """Return a concrete output language name."""
    custom = (custom_language or "").strip()
    if custom:
        return custom
    return choice or "English"

