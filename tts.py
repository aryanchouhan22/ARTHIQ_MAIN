import base64
from app.agent.llm import _get_client
from app.languages import get_language


def speak(text: str, lang: str) -> bytes:
    """Text -> WAV bytes in the given language."""
    l = get_language(lang)
    r = _get_client().text_to_speech.convert(
        text=text, language_code=l.code, model="bulbul:v3", speaker=l.speaker)
    return base64.b64decode(r.audios[0])