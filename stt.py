import os, uuid
from app.agent.llm import _get_client


def transcribe(wav_bytes: bytes):
    """WAV bytes -> (transcript, detected language code)."""
    os.makedirs("data", exist_ok=True)
    path = f"data/up_{uuid.uuid4().hex}.wav"
    with open(path, "wb") as f:
        f.write(wav_bytes)
    try:
        with open(path, "rb") as f:
            r = _get_client().speech_to_text.transcribe(
                file=f, model="saaras:v4", mode="codemix")
        return (r.transcript or "").strip(), getattr(r, "language_code", None)
    finally:
        os.remove(path)