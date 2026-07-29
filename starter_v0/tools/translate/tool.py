def translate_text(text: str, target_language: str = "Vietnamese") -> dict[str, str]:
    """
    Mock implementation of a translation tool.
    In a real scenario, this would call an API like Google Translate or DeepL.
    """
    return {
        "text": text,
        "target_language": target_language,
        "translated_text": f"[Translated to {target_language}]: {text}"
    }
